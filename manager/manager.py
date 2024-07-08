from .message       import *
from .types         import Logger, Run, ResultDict, ItemDict
from .node          import Node
from .lemondrop     import LemonDrop
from .task          import Task, Parent, Mcast, Rand, Lemon
from .utils         import *

from queue          import Queue
from typing         import List, Generator

import zmq

class Manager():
    def __init__(self, name:str, ip:str, port:str, workers:List, map:dict):
        self.node       = Node(name=name, addr=f"{ip}:{port}", stype=zmq.REQ, map=map)
        self.rep        = Node(name=name, addr=f"{ip}:{port}", stype=zmq.REP, map=map)
        self.workers    = workers
        self.map        = map
        self.tasks      = Queue()
        self.L          = Logger(name=f"{name}:{ip}")

    def build(self, run) -> Generator[ResultDict, None, None]:
        i = 0
        while(not run.tree.full()):
            self.L.state(f"STATE[BUILD[{i}]")
            if   run.data["name"] == "RAND":   result = self.rand(run)
            else:                              result = self.parent(run)
            yield result
            i += 1

    def evaluate(self, run):
        self.L.state(f"STATE[EVALUATION]")
        result = self.mcast(run)
        return result

    def establish(self):
        self.L.state(f"STATE[ESTABLISH]")
        for addr in self.workers:
            m = self.node.message(dst=addr, t=Type.CONNECT)
            _ = self.node.handshake(m)

    def parent(self, run:Run) -> ResultDict:
        self.L.state(f"STATE[PARENT]")
        addr = run.tree.next()
        task = Parent()
        c    = task.build(run)
        m    = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.node.handshake(m, field="job")
        job  = r.mdata.job
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def mcast(self, run:Run) -> ResultDict:
        self.L.state(f"STATE[MCAST]")
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
        self.L.state(f"STATE[RAND]")
        task = Rand()
        data = task.evaluate(Job(), run)
        return data

    def lemon(self, run:Run, buffer:int=5, port:int=6060) -> Generator[ResultDict, None, None]:
        self.L.state(f"STATE[LEMON]")
        tasks = []
        ts  = self.node.timer.future_ts(buffer)
        for addr in self.workers:
            task    = Lemon()
            c       = task.build(run)
            c.addr  = addr
            c.instr.append(f"./bin/lemon -i {self.node.ip(addr)} -p {port} -s docker -f {ts}")
            m       = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
            r       = self.node.handshake(m, field="job")
            job     = r.mdata.job
            task.job.CopyFrom(job)
            tasks.append(task)

        for i,task in enumerate(tasks):
            result  = self.report(task, run)
            yield result

    def report(self, task:Task, run:Run, interval:int=1) -> ResultDict:
        self.L.state(f"STATE[REPORT]")
        while True:
            job     = task.job
            m       = self.node.message(dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
            r       = self.node.handshake(m, field="job")
            rjob    = r.mdata.job

            if rjob.end: return task.evaluate(rjob, run)
            else:        self.node.timer.sleep_sec(interval)
