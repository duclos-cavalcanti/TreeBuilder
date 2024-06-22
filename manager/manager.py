from .message       import *
from .types         import Logger, ResultDict, ItemDict
from .node          import Node
from .task          import Task, Parent, Mcast
from .utils         import *

from queue          import Queue
from typing         import List

import zmq

class Manager(Node):
    def __init__(self, name:str, ip:str, port:str, workers:List, map:dict):
        super().__init__(name=name, stype=zmq.REQ)
        self.L          = Logger(name=f"{name}:{ip}")
        self.addr       = f"{ip}:{port}"
        self.workers    = workers
        self.map        = map
        self.tasks      = Queue()
        self.L.record(f"{self.name} UP")

    def build(self, run):
        while(not run.tree.full()):
            if run.data["name"] != "RAND":  result = self.parent(run)
            else:                           result = self.rand(run)
            self.L.record(f"TREE[{run.tree.name}] SELECTION[{run.tree.n}/{run.tree.nmax}]: PARENT[{result['root']}] => CHILDREN {[ a for a in result['selected'] ]}")
            yield result

    def evaluate(self, run):
        result = self.mcast(run)
        self.L.record(f"TREE[{run.tree.name}] PERFORMANCE[{result['selected'][0]}]: {result['items'][0]['p90']}")
        return result

    def establish(self):
        for addr in self.workers:
            m = self.message(src=self.addr, dst=addr, t=Type.CONNECT)
            r = self.handshake(m)
            self.verify(m, r)
        self.L.record(f"CONNECTED[{len(self.workers)}]")

    def parent(self, run) -> ResultDict:
        addr = run.tree.next()
        task = Parent()
        c    = task.build(run)
        m    = self.message(src=self.addr, dst=addr, ref=f"{self.map[self.addr]}/{self.map[addr]}", t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.handshake(m)
        job  = self.verify(m, r, field="job")
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def mcast(self, run) -> ResultDict:
        addr = run.tree.root.id
        task = Mcast()
        c    = task.build(run)
        m    = self.message(src=self.addr, dst=addr, ref=f"{self.map[self.addr]}/{self.map[addr]}", t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.handshake(m)
        job  = self.verify(m, r, field="job")
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def rand(self, run) -> ResultDict:
        data:ResultDict = {
                "root": run.tree.next(),
                "key": run.data["strategy"]["key"],
                "select": 1, 
                "rate": run.data["parameters"]["rate"],
                "duration": run.data["parameters"]["duration"],
                "items": [],
                "selected": []
        }
        arr = run.pool.slice()
        for a in arr:                       
            item: ItemDict = {
                    "addr":     a,
                    "p90":      0.0,
                    "p75":      0.0,
                    "p50":      0.0,
                    "p25":      0.0,
                    "stddev":   0.0,
                    "recv":     0,
            }
            data["items"].append(item)

        for _ in range(run.tree.fanout):    
            data["selected"].append(run.pool.select(arr))

        return data

    def report(self, task:Task, run, interval:int=1) -> ResultDict:
        while True:
            job = task.job
            m = self.message(src=self.addr, dst=job.addr, ref=f"{self.map[self.addr]}/{self.map[job.addr]}", t=Type.REPORT, mdata=Metadata(job=job))
            r = self.handshake(m)
            rjob = self.verify(m, r, field="job")

            if rjob.end: return task.process(rjob, run.data["strategy"])
            else:        self.timer.sleep_sec(interval)
