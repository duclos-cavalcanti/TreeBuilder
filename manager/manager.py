from .message       import *
from .types         import Logger, Run, ResultDict, ItemDict
from .node          import Node
from .lemondrop     import LemonDrop
from .task          import Task, Parent, Mcast, Lemon
from .utils         import *

from queue          import Queue
from typing         import List, Generator, Tuple

import zmq
import time

class Manager():
    def __init__(self, name:str, ip:str, port:str, workers:List, map:dict):
        self.node       = Node(name=name, addr=f"{ip}:{port}", stype=zmq.REQ, map=map)
        self.workers    = workers
        self.map        = map
        self.tasks      = Queue()
        self.L          = Logger(name=f"{name}:{ip}")

    def establish(self):
        self.L.state(f"STATE[ESTABLISH]")
        for addr in self.workers:
            m = self.node.message(dst=addr, t=Type.CONNECT)
            _ = self.node.handshake(m)

    def build(self, run) -> Generator[Tuple[ResultDict, float], None, None]:
        i = 0
        n = ( (run.tree.nmax - 1) / run.tree.fanout ) 
        while(not run.tree.full()):
            self.L.state(f"STATE[BUILD[{i + 1} / {n}]")
            start = time.time()
            result = self.parent(run)
            yield result, (time.time() - start)
            i += 1

    def evaluate(self, run):
        self.L.state(f"STATE[EVALUATION]")
        start = time.time()
        result = self.mcast(run)
        return result, (time.time() - start)

    def lemon(self, run:Run, buffer:int=5, port:int=6060, interval:int=1) -> Generator[Tuple[ResultDict, float], None, None]:
        self.L.state(f"STATE[LEMON]")
        start = time.time()
        tasks = []
        ts  = self.node.timer.future_ts(buffer)
        for addr in self.workers:
            task    = Lemon()
            c       = task.build(run)
            c.addr  = addr
            c.instr.append(f"./bin/lemon -i {self.node.ip(addr)} -p {port} -s default -f {ts}")
            m       = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
            r       = self.node.handshake(m, field="job")
            job     = r.mdata.job
            if job.ret != 0: raise RuntimeError(f"JOB FAILURE: {job}")
            task.job.CopyFrom(job)
            tasks.append(task)

        for task in tasks:
            result  = self.report(task, run, interval=interval)
            yield result, (time.time() - start)

    def rebuild(self, run:Run, parent:str, children:List[str]) -> ResultDict:
        self.L.state(f"STATE[REBUILD]")
        addr = parent
        arr  = [addr] + run.pool.slice() + children
        task = Parent()
        c    = task.build(run, arr)
        m    = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.node.handshake(m, field="job")
        job  = r.mdata.job
        if job.ret != 0: raise RuntimeError(f"JOB FAILURE: {job}")
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def parent(self, run:Run) -> ResultDict:
        self.L.state(f"STATE[PARENT]")
        addr = run.tree.next()
        arr  = [addr] + run.pool.slice()
        task = Parent()
        c    = task.build(run, arr)
        m    = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.node.handshake(m, field="job")
        job  = r.mdata.job
        if job.ret != 0: raise RuntimeError(f"JOB FAILURE: {job}")
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def mcast(self, run:Run) -> ResultDict:
        self.L.state(f"STATE[MCAST]")
        addr = run.tree.root.id
        arr  = run.tree.arr()
        task = Mcast()
        c    = task.build(run, arr)
        m    = self.node.message(dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r    = self.node.handshake(m, field="job")
        job  = r.mdata.job
        if job.ret != 0: raise RuntimeError(f"JOB FAILURE: {job}")
        task.job.CopyFrom(job)
        ret  = self.report(task, run)
        return ret

    def rand(self, run) -> Generator[ResultDict, None, None]:
        self.L.state(f"STATE[RAND]")
        while(not run.tree.full()):
            data:ResultDict = {
                "id": f"rand-{run.tree.root.id}",
                "root": run.tree.next(),
                "key": run.data["strategy"]["key"],
                "select": 1, 
                "rate": run.data["parameters"]["rate"],
                "duration": run.data["parameters"]["duration"],
                "items": [],
                "selected": [ run.pool.select() for _ in range(run.tree.fanout) ]
            }
            yield data

    def report(self, task:Task, run:Run, interval:int=1) -> ResultDict:
        self.L.state(f"STATE[REPORT]")
        start    = time.time()
        duration = task.job.duration
        while True:
            job     = task.job
            m       = self.node.message(dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
            r       = self.node.handshake(m, field="job")
            rjob    = r.mdata.job

            if rjob.end: return task.evaluate(rjob, run)
            else:        self.node.timer.sleep_sec(interval)

            diff = time.time() - start
            if (diff) > (3*duration): 
                raise RuntimeError(f"NODE[{rjob.addr}] EXCEEDED REPORT LIMIT: {diff} > 3 * {duration}")

    def flush(self):
        self.L.state(f"STATE[FLUSH]")

        for addr in self.workers:
            m = self.node.message(dst=addr, t=Type.LOG)
            _ = self.node.handshake(m)
