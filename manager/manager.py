from .node      import Node
from .message   import *
from .types     import Pool, Tree, Logger
from .parent    import Parent
from .mcast     import Mcast

from queue      import Queue, SimpleQueue
from typing     import List
from datetime import datetime

import zmq
import csv

class Run():
    def __init__(self, run:dict, params:dict, root:str, nodes:List):
        self.name       = run["name"]
        self.strategy   = run["strategy"]
        self.K          = params["hyperparameter"]
        self.rate       = params["rate"]
        self.dur        = params["duration"]
        self.pool       = Pool([n for n in nodes], self.K, len(nodes))
        self.tree       = Tree(name=self.name, root=root, fanout=params["fanout"], depth=params["depth"])
        self.data       = []

class Runner():
    def __init__(self, root:str, nodes:List, params:dict, runs:List):
        self.runQ = SimpleQueue()
        self.runs = [ Run(run, params, root, nodes) for run in runs ]
        self.run  = self.runs[0]
        self.data = []
        self.L    = Logger()

        for run in self.runs: self.runQ.put(run)

    def completed(self):
        return self.runQ.empty()

    def next(self):
        self.run = self.runQ.get_nowait()
        self.L.state(f"STATE[RUN={self.run.name}]")
        return self.run

    def build(self, data:dict):
        root  = data["root"]
        addrs = [ d["addr"] for d in data["selected"] ]
        self.run.tree.n_add(addrs)
        self.run.pool.n_remove(addrs)
        self.L.record(f"TREE[{self.run.tree.name}] SELECTION[{self.run.tree.n}/{self.run.tree.max}]: PARENT[{root}] => CHILDREN {[c for c in addrs]}")

    def log(self, run:Run, data:dict):
        timestamp = datetime.now().strftime("%m-%d %H:%M:%S")
        row = [ run.tree.name, 
                data['selected'][0]['perc'], 
                run.tree.hash(),
                run.tree.d, 
                run.tree.fanout,
                run.rate, 
                run.dur, 
                timestamp]

        self.data.append(row)
        self.L.record(f"TREE[{self.run.tree.name}] PERFORMANCE[{data['selected'][0]['addr']}]: {data['selected'][0]['perc']}")

    def flush(self):
        file = f"/volume/results.csv"
        headers = ['NAME', 
                   'LATENCY', 
                   'ID',
                   'DEPTH', 
                   'FANOUT', 
                   'RATE', 
                   'DUR' ,
                   'TIME']

        with open(file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for d in self.data: writer.writerow(d)

class Manager(Node):
    def __init__(self, plan:dict, name:str, ip:str, port:str):
        super().__init__(name=name, stype=zmq.REQ)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"

        self.plan       = plan
        self.workers    = self.plan["addrs"][1:]
        self.tasks      = SimpleQueue()
        self.runner     = Runner(self.workers[0], self.workers[1:], plan["params"], plan["runs"])
        self.L          = Logger(name=f"manager:{self.addr}")

    def go(self):
        try:
            self.establish()
            self.L.record(f"CONNECTED[{len(self.workers)}]")

            while(not self.runner.completed()):
                self.run = self.runner.next()

                while(not self.run.tree.full()):
                    if self.run.name == "RAND": data = self.rand()
                    else:                       data = self.parent()
                    self.runner.build(data)

                data = self.mcast()
                self.runner.log(self.run, data)

            self.runner.flush()
            self.L.record("FINISHED!")

        except Exception as e:
            self.L.log("INTERRUPTED!")
            raise e

        finally:
            self.L.flush()
            self.socket.close()

    def establish(self):
        for addr in self.workers:
            m = self.message(src=self.addr, dst=addr, t=Type.CONNECT)
            r = self.handshake(m)
            self.verify(m, r)

    def parent(self):
        addr = self.run.tree.next()
        c = Command(flag=Flag.PARENT, id=self.gen(), addr=addr, layer=1, select=self.run.tree.fanout, rate=self.run.rate, dur=self.run.dur, data=self.run.pool.slice())
        m = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(m)
        job  = self.verify(m, r, field="job")
        self.tasks.put(Parent(c, job))
        data = self.report()
        return data

    def mcast(self):
        data = self.run.tree.ids()
        addr = data[0]
        c = Command(flag=Flag.MCAST, id=self.gen(), addr=addr, layer=self.run.tree.d, select=1, rate=self.run.rate, dur=self.run.dur, depth=self.run.tree.d, fanout=self.run.tree.fanout, data=data)
        m = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(m)
        job = self.verify(m, r, field="job")
        self.tasks.put(Mcast(c, job))
        data = self.report()
        return data

    def rand(self) -> dict:
        data = { "root": self.run.tree.next(), "selected": [] }
        for _ in range(self.run.tree.fanout): 
            addr = self.run.pool.select()
            data["selected"].append({"addr": addr})

        self.run.pool.pool.extend([d["addr"] for d in data["selected"]])
        return data

    def report(self, dur:int=2) -> dict:
        task = self.tasks.get_nowait()
        while True:
            job = task.copy()
            m = self.message(src=self.addr, dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
            r = self.handshake(m)
            rjob = self.verify(m, r, field="job")

            if rjob.end: 
                data = task.process(rjob, self.run.strategy)
                self.L.stats(message=f"TASK[{Flag.Name(rjob.flag)}][{rjob.id}:{rjob.addr}]", data=data)
                return data

            self.timer.sleep_sec(dur)
