from .message   import *
from .ds        import SQueue, Pool, Tree, Logger

from typing import List, Callable, Any

from google.protobuf.json_format import MessageToJson, MessageToDict

import heapq

class Runner():
    class Run():
        def __init__(self, d:dict):
            self.step       = d["step"]
            self.name       = d["name"]
            self.best       = d["best"]

    def __init__(self, root:str, pool:Pool, runs:List, logger:Logger):
        self.runs       = SQueue(arr=runs)
        self.run        = self.Run(self.runs.pop())
        self.root       = root
        self.pool       = pool
        self.orderQ     = SQueue()
        self.tree       = Tree(name=self.run.name, root=root, fanout=2, depth=2)
        self.logger     = logger 
        self.logger.write(key="root", data=self.root)
        self.logger.write(key="pool", data=self.pool.to_dict())

    def resolve(self, job:Job):
        self.logger.event(f"REPORT[{Flag.Name(job.flag)}]", MessageToDict(job))
        if job.flag == Flag.PARENT: return self.parent(job)
        if job.flag == Flag.MCAST:  return self.mcast(job)
        else:                       raise NotImplementedError()

    def order(self):
        o = self.orderQ.pop()
        if self.tree.full():    
            step = "MCAST"
        else:
            step = "PARENT"

        return o, step

    def parent(self, job:Job):
        data  = {}
        percs  = [f for f in job.floats]
        sorted = heapq.nsmallest(len(percs), enumerate(percs), key=lambda x: x[1])

        if self.run.best: items = sorted[:job.select]
        else:             items = [ w for w in reversed(sorted[(-1 * job.select):]) ]

        ret  = []
        data = []
        for item in items:
            idx   = item[0]
            perc  = item[1]
            addr  = job.data[idx]
            data.append({"addr": addr, "perc": perc})
            ret.append(addr)

        self.logger.event(f"PARENT[{job.addr}] CHOSE", [ f"{c}" for c in ret], verbosity=True)
        self.tree.n_add(ret)
        self.pool.n_remove(ret)

        if self.tree.full():
            self.logger.event("TREE COMPLETE", f"{self.tree.name}", verbosity=True)
            self.logger.tree(key=self.tree.name, data=self.tree.to_dict())

        self.orderQ.push(Order(flag=Flag.PARENT, addr=job.addr, data=ret))
        step = "ORDER"

        return step

    def mcast(self, job:Job):
        if len(job.floats) != len(job.data) != len(job.integers): 
            raise RuntimeError()

        data  = { "selected": {}, "data": [] }
        for perc, recv, addr in zip(job.floats, job.integers, job.data):
            d = { "addr": addr, "perc": perc, "recv": recv }
            data["data"].append(d)

        percs  = [f for f in job.floats]
        sorted = heapq.nlargest(len(percs), enumerate(percs), key=lambda x: x[1])

        idx  = sorted[0][0]
        perc = sorted[0][1]
        addr = job.data[idx]

        data["selected"]["addr"] = addr
        data["selected"]["perc"] = perc
        self.logger.event(f"MCAST PERFORMANCE[{self.tree.name}]", f"{addr}:{perc}", verbosity=True)
        self.logger.record(f"TREE[{self.tree.name}]", data=data)

        self.run = self.runs.pop()

        if self.run is None: 
            step = "LOG"
        else:
            self.logger.event(f"NEW RUN", self.run.name, verbosity=True)
            self.tree = Tree(name=self.run.name, root=self.root, fanout=2, depth=2)
            self.pool.reset()
            step = self.run.step

        return "LOG"

    def __str__(self):
        ret = "RUN: "
        if self.run is None: ret += f"NONE:NONE"
        else:                ret += f"{self.run.step}:{self.run.name}"
        return ret
