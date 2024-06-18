from .message   import *
from .types     import Seed, Pool, Tree, Logger
from .node      import Node
from .task      import Task, Parent, Mcast, Plan, Result
from .utils     import *

from queue              import Queue, SimpleQueue
from typing             import List
from datetime           import datetime

import zmq
import csv

class Run():
    def __init__(self, run:dict, params:dict, root:str, nodes:List, seed:int):
        self.name       = run["name"]
        self.strategy   = run["strategy"]
        self.K          = params["hyperparameter"]
        self.rate       = params["rate"]
        self.duration   = params["duration"]
        self.pool       = Pool([n for n in nodes], self.K, seed)
        self.tree       = Tree(name=self.name, root=root, fanout=params["fanout"], depth=params["depth"])
        self.data       = []

    def to_dict(self):
        ret = {
            "name": self.name, 
            "strategy": self.strategy, 
            "params": {
                "K": self.K, 
                "rate": self.rate, 
                "duration": self.duration
            },
            "tree": {
                "name": self.name, 
                "root": self.tree.root.id,
                "fanout": self.tree.fanout,
                "depth": self.tree.dmax,
            }
        }
        return ret

class Runner():
    def __init__(self, root:str, nodes:List, params:dict, runs:List, infra:str):
        self.seed   = Seed()
        self.runQ   = SimpleQueue()
        self.runs   = [ Run(run, params, root, nodes, self.seed.get()) for run in runs ]
        self.run    = self.runs[0]
        self.infra  = infra
        self.data   = []
        self.L      = Logger()

        for run in self.runs: self.runQ.put(run)

    def completed(self):
        return self.runQ.empty()

    def next(self):
        self.run = self.runQ.get_nowait()
        return self.run

    def build(self, result:Result):
        addrs = [ d for d in result.data["selected"] ]
        self.run.tree.n_add(addrs)
        self.run.pool.n_remove(addrs)

    def save(self, run:Run, result:Result):
        timestamp = datetime.now().strftime("%m-%d %H:%M:%S")
        row = [ run.tree.name, 
                result.data['data'][0]['p90'], 
                run.tree.hash(),
                run.tree.d, 
                run.tree.fanout,
                run.rate, 
                run.duration, 
                timestamp]

        self.data.append(row)

    def write(self):
        file = f"/work/logs/results.csv"
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
    def __init__(self, schema:dict, name:str, ip:str, port:str):
        super().__init__(name=name, stype=zmq.REQ)
        self.addr       = f"{ip}:{port}"
        self.schema     = schema
        self.workers    = [ f"{a}:{self.schema['port']}" for a in self.schema["addrs"][1:] ]
        self.tasks      = Queue()
        self.runner     = Runner(self.workers[0], 
                                 self.workers[1:], 
                                 schema["params"], 
                                 schema["runs"], 
                                 schema["infra"])
        self.L          = Logger(name=f"{name}:{ip}")

    def go(self):
        self.L.state(f"{self.name} UP")
        try:
            self.establish()
            self.L.record(f"CONNECTED[{len(self.workers)}]")

            while(not self.runner.completed()):
                self.run = self.runner.next()
                self.L.state(f"STATE[RUN={self.run.name}]")

                self.L.event({"RUN":  self.run.to_dict()})
                self.L.event({"POOL": self.run.pool.pool})
                while(not self.run.tree.full()):
                    result = self.parent() if self.run.name != "RAND" else self.rand()
                    self.runner.build(result)

                    self.L.record(f"TREE[{self.run.tree.name}] SELECTION[{self.run.tree.n}/{self.run.tree.nmax}]: PARENT[{result.data['root']}] => CHILDREN {[ a for a in result.data['selected'] ]}")
                    self.L.event({"BUILD": result.data})
                    if self.run.tree.full():
                        self.L.event({"TREE": self.run.tree.to_dict()})

                result = self.mcast()
                self.runner.save(self.run, result)

                self.L.record(f"TREE[{self.run.tree.name}] PERFORMANCE[{result.data['selected'][0]}]: {result.data['data'][0]['p90']}")
                self.L.event({"PERF": result.data})
                self.L.event({"POOL": self.run.pool.pool})

            self.runner.write()
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

    def parent(self) -> Result:
        addr = self.run.tree.next()
        arr  = [addr] + self.run.pool.slice()
        plan = Plan(rate=self.run.rate, duration=self.run.duration, depth=1, fanout=len(arr[1:]), select=self.run.tree.fanout, arr=arr)
        task = Parent()
        c    = task.build(plan)
        m    = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.handshake(m)
        job  = self.verify(m, r, field="job")
        task.job.CopyFrom(job)
        ret  = self.report(task)
        return ret

    def mcast(self) -> Result:
        addr = self.run.tree.root.id
        arr  = self.run.tree.arr()
        plan = Plan(rate=self.run.rate, duration=self.run.duration, depth=self.run.tree.d, fanout=self.run.tree.fanout, select=1, arr=arr)
        task = Mcast()
        c    = task.build(plan)
        m    = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.handshake(m)
        job  = self.verify(m, r, field="job")
        task.job.CopyFrom(job)
        ret  = self.report(task)
        return ret

    def rand(self) -> Result:
        r = Result()
        arr = self.run.pool.slice()

        r.data["root"] = self.run.tree.next()
        for a in arr:                         r.data["data"].append(r.element(addr=a))
        for _ in range(self.run.tree.fanout): r.data["selected"].append(self.run.pool.select(arr))

        return r

    def report(self, task:Task, interval:int=1) -> Result:
        while True:
            job = task.job
            m = self.message(src=self.addr, dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
            r = self.handshake(m)
            rjob = self.verify(m, r, field="job")

            if rjob.end: return task.process(rjob, self.run.strategy)
            else:        self.timer.sleep_sec(interval)
