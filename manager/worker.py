from .message   import *
from .types     import Logger
from .node      import Node
from .task      import Task, Parent, Mcast, Lemon

import zmq
import threading
import subprocess
import time

from typing     import List, Dict, Tuple
from threading  import Thread

class Worker():
    def __init__(self, name:str, ip:str, port:str, manager:str, map:dict):
        self.node                                       = Node(name=name, addr=f"{ip}:{port}", stype=zmq.REP, map=map)
        self.req                                        = Node(name=name, addr=f"{ip}:{port}", stype=zmq.REQ, map=map)
        self.manager                                    = manager
        self.map                                        = map
        self.tasks: Dict[str, Tuple[Task, Thread]]      = {}
        self.errors                                     = []
        self.L                                          = Logger(name=f"{name}:{ip}")

    def run(self, job:Job):
        self.L.log(message=f"STARTED JOB[{job.id}:{job.addr}]")
        start  = time.time()
        stress = None
        if job.stress:
            self.L.log(message=f"ADDING STRESS TO JOB[{job.id}:{job.addr}]")
            command = f"stress-ng --cpu $(nproc) --cpu-load 80"
            stress = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            p = subprocess.Popen(
                job.instr, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            stdout, stderr = p.communicate()
            output = (stdout if stdout else stderr)
            data = [ s for s in output.split("\n") if s ]

            job.pid = p.pid
            job.ret = int(p.returncode)
    
        except Exception as e:
            data = [ f"ERROR: {e}" ]
            job.ret = -1
    
        finally:
            job.ClearField('data')
            job.data.extend(data)
            job.end = True
            if stress:
                stress.kill()

        end = time.time()
        self.L.log(message=f"FINISHED JOB[{job.id}:{job.addr}] TOOK {end - start} SECONDS")
        return job

    def scatter(self, arr:List[Command]) -> List[Job]:
        ret = []
        if len(arr) == 0: 
            return ret

        for item in arr:
            c = Command()
            c.CopyFrom(item)
            m       = self.req.message(dst=c.addr, t=Type.COMMAND, mdata=Metadata(command=c))
            r       = self.req.handshake(m=m, field="job")
            rjob    = r.mdata.job
            ret.append(rjob)
            self.L.log(message=f"SCATTERED JOB[{rjob.id}:{rjob.addr}]")

        return ret

    def gather(self, arr:List[Job], interval:int=1):
        if len(arr) == 0: 
            return

        completed = [ False ] * len(arr)

        while True:
            self.req.timer.sleep_sec(interval)

            if all(completed): 
                break

            for i, job in enumerate(arr):
                if job.end: continue

                m       = self.req.message(dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
                r       = self.req.handshake(m, field="job")
                rjob    = r.mdata.job

                if rjob.end: 
                    arr[i].CopyFrom(rjob)
                    completed[i] = True 
                    self.L.log(message=f"GATHERED JOB[{i}][{rjob.id}:{rjob.addr}]")
        return

    def launch(self, task:Task):
        def callback(t:Task):
            self.run(t.job)
            self.gather(t.deps)

        t = threading.Thread(target=callback, args=(task,))
        t.start()

        id              = task.job.id
        self.tasks[id]  = (task, t)

    def schedule(self, command:Command):
        if   command.flag == Flag.PARENT: Constructor = Parent
        elif command.flag == Flag.MCAST:  Constructor = Mcast
        elif command.flag == Flag.LEMON:  Constructor = Lemon
        else:                             raise RuntimeError()

        task              = Constructor(command)
        job, commands     = task.handle(command)
        
        try:
            jobs = self.scatter(commands)
            if jobs: task.deps.extend(jobs)
            self.launch(task)

        except Exception as e:
            job.ret = -1

        return job

    def connectACK(self, m:Message):
        return self.node.ack_message(m)

    def commandACK(self, m:Message):
        if not m.mdata.HasField("command"): 
            return self.node.err_message(m, desc=f"COMMAND[{self.addr}] FORMAT ERR")

        c = m.mdata.command
        job = self.schedule(c)
        return self.node.ack_message(m, mdata=Metadata(job=job))

    def reportACK(self, m:Message):
        if not m.mdata.HasField("job"): 
            return self.node.err_message(m, desc=f"REPORT[{self.addr}] FORMAT ERR")
        
        job = m.mdata.job
        if job.id not in self.tasks:
            raise RuntimeError()

        task, t = self.tasks[job.id]

        if t.is_alive() or not task.complete():
            return self.node.ack_message(m, mdata=Metadata(job=job))

        ret = task.process()
        self.tasks.pop(job.id)

        return self.node.ack_message(m, mdata=Metadata(job=ret))

    def errorACK(self, m:Message):
        raise RuntimeError()

    def logACK(self, m:Message):
        return self.node.ack_message(m)

    def start(self):
        self.node.bind()
        while(True):
            m = self.node.recv_message()
            self.L.state(f"STATE[{Type.Name(m.type)}]")

            match m.type:
                case Type.CONNECT:  self.connectACK(m)
                case Type.COMMAND:  self.commandACK(m)
                case Type.REPORT:   self.reportACK(m)
                case Type.ERR:      self.errorACK(m)
                case Type.LOG:      self.logACK(m)
                case _:             raise NotImplementedError()
            
            if m.type == Type.LOG: break

