from .message   import *
from .types     import Pool, Tree, Logger
from .node      import Node
from .task      import Parent, Mcast
from .utils     import *

from queue              import Queue, SimpleQueue
from typing             import List
from datetime           import datetime

import zmq
import csv
import os

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
    def __init__(self, root:str, nodes:List, params:dict, runs:List, infra:str):
        self.runQ   = SimpleQueue()
        self.runs   = [ Run(run, params, root, nodes) for run in runs ]
        self.run    = self.runs[0]
        self.data   = []
        self.infra  = infra
        self.L      = Logger()

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

    def upload(self):
        if not self.infra in ["gcp", "docker"]:
            return

        bucket      = "exp-results-nyu-systems-multicast"
        timestamp   = datetime.now().strftime("%m-%d-%H:%M:%S")
        folder      = f"treefinder-{self.infra}-{timestamp}/results.tar.gz"
        commands    = [ f"cd /work && tar -zcvf results.tar.gz ./logs" ]

        if self.infra == "gcp":
            commands += [ 
                f"cd /work && gcloud storage cp results.tar.gz gs://{bucket}/{folder}/results.tar.gz",
                f"cd /work && gcloud storage cp project/plans/default.yaml gs://{bucket}/{folder}/default.yaml"
            ]

        else:
            commands += [ 
                f"cd /work && mv results.tar.gz /work/logs",
                f"cd /work && mv project/plans/docker.yaml /work/logs"
            ]

        for c in commands: 
            if os.system(f"{c}") != 0: 
                raise RuntimeError(f"{c} failed")

        self.L.record(f"RESULTS[{bucket}] => {folder}!")

class Manager(Node):
    def __init__(self, plan:dict, name:str, ip:str, port:str):
        super().__init__(name=name, stype=zmq.REQ)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"

        self.plan       = plan
        self.workers    = self.plan["addrs"][1:]
        self.tasks      = Queue()
        self.runner     = Runner(self.workers[0], self.workers[1:], plan["params"], plan["runs"], plan["infra"])
        self.L          = Logger(name=f"manager:{self.ip}")

    def go(self):
        self.L.state(f"{self.name} UP")
        try:
            self.establish()
            self.L.record(f"CONNECTED[{len(self.workers)}]")

            while(not self.runner.completed()):
                self.run = self.runner.next()

                while(not self.run.tree.full()):
                    if self.run.name == "RAND": data = self.rand()
                    else:                       data = self.parent()
                    self.runner.build(data)

                self.L.trees(f"{self.run.tree}")

                data = self.mcast()
                self.runner.log(self.run, data)

            self.runner.write()
            self.runner.upload()
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
        data = { 
            "root": self.run.tree.next(), 
            "selected": [ 
                         {"addr": a } for a in self.run.pool.slice(param=self.run.tree.fanout)
            ]
        }
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
