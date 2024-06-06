from .message   import *
from .node      import Node
from .task      import Task
from .parent    import Parent
from .mcast     import Mcast
from .types     import Logger

import zmq
import threading
import subprocess
import logging

class Scheduler():
    def __init__(self, addr:str):
        self.addr       = addr
        self.tasks      = {}
        self.L          = Logger()

    def add(self, command:Command):
        if   command.flag == Flag.PARENT: task = Parent(command)
        elif command.flag == Flag.MCAST:  task = Mcast(command)
        else:                             raise RuntimeError()

        job = task.make()
        self.tasks[job.id] = { "task": task, "thread": self.launch(self.execute, args=(task,)) }

        self.L.log(message=f"DISPATCHED JOB[{job.id}:{job.addr}]")
        return job

    def report(self, job:Job):
        d = self.tasks.get(job.id)
        if d is None: 
            raise RuntimeError()

        task   = d["task"]
        thread = d["thread"]

        # if job and/or it's dependencies haven't finished
        if not task.complete() or thread.is_alive():
            return job
        else:
            ret = task.summarize()
            del self.tasks[job.id]
            del task 
            del thread

            self.L.log(message=f"FINALIZED JOB[{ret.id}:{ret.addr}]")
            self.L.debug(message=f"", data=ret)
            return ret

    def execute(self, t:Task):
        try:
            p = subprocess.Popen(
                t.job.instr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = p.communicate()

            data = [ s for s in (stdout if stdout else stderr).split("\n") if s ]
            t.job.pid = p.pid
            t.job.ret = int(p.returncode)

        except Exception as e:
            data = [ f"ERROR: {e}" ]
            t.job.ret = -1

        finally:
            t.job.ClearField('data')
            t.job.data.extend(data)
            t.job.end = True
            self.L.debug(message=f"DISPATCHED JOB[{t.job.id}:{t.job.addr}]", data=t.job)

        self.resolve(t)
        return

    def resolve(self, t:Task, sleep_sec:int=1):
        self.L.log(message=f"RESOLVING JOB[{t.job.id}:{t.job.addr}] DEPENDENCIES...")
        if len(t.dependencies) == 0: 
            return

        N = Node(stype=zmq.REQ)
        while True:
            N.timer.sleep_sec(sleep_sec)
            if t.complete(): 
                break
        
            for i, job in enumerate(t.dependencies):
                if job.end: continue 
        
                m = Message(id=0, ts=N.timer.ts(), src=f"SCHEDULER:{t.job.addr}", dst=job.addr, type=Type.REPORT, mdata=Metadata(job=job))
                r = N.handshake(job.addr, m)
                ret = N.verify(m, r, field="job")

                if ret.end: 
                    t.dependencies[i] = ret
                    self.L.log(message=f"RESOLVED DEPENDENCY[{i}][{job.id}:{job.addr}]")

    def launch(self, target, args=()):
        t = threading.Thread(target=target, args=args)
        t.start()
        return t

