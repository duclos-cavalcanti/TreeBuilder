from .message       import *
from .types         import Logger, ResultDict, ItemDict
from .node          import Node
from .task          import Task, Parent, Mcast, Rand
from .utils         import *

from queue          import Queue
from typing         import List

import zmq

class Manager():
    def __init__(self, name:str, ip:str, port:str, workers:List, map:dict):
        self.node       = Node(name=name, addr=f"{ip}:{port}", stype=zmq.REQ, map=map)
        self.rep        = Node(name=name, addr=f"{ip}:{port}", stype=zmq.REP, map=map)
        self.workers    = workers
        self.map        = map
        self.tasks      = Queue()
        self.L          = Logger(name=f"{name}:{ip}")
        self.L.record(f"{name.upper()} UP")

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
            m = self.node.message(dst=addr, t=Type.CONNECT)
            _ = self.node.handshake(m)
        self.L.record(f"CONNECTED[{len(self.workers)}]")

    def parent(self, run) -> ResultDict:
        addr = run.tree.next()
        task = Parent()
        c    = task.build(run)
        m    = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.node.handshake(m, field="job")
        job  = r.mdata.job
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def mcast(self, run) -> ResultDict:
        addr = run.tree.root.id
        task = Mcast()
        c    = task.build(run)
        m    = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.node.handshake(m, field="job")
        job  = r.mdata.job
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def rand(self, run) -> ResultDict:
        task = Rand()
        data = task.evaluate(Job(), run)
        return data

    def lemon(self, run) -> ResultDict:
        raise NotImplementedError()

    def report(self, task:Task, run, interval:int=1) -> ResultDict:
        while True:
            job     = task.job
            m       = self.node.message(dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
            r       = self.node.handshake(m, field="job")
            rjob    = r.mdata.job

            if rjob.end: return task.evaluate(rjob, run)
            else:        self.node.timer.sleep_sec(interval)
