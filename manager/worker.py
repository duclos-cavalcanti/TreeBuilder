from .message   import *
from .types     import Logger
from .node      import Node
from .task      import Task, Parent, Mcast

import zmq
import threading
import subprocess

class Controller(Node):
    def __init__(self, name:str, ip:str, port:str):
        super().__init__(name=name, stype=zmq.REQ)
        self.addr       = f"{ip}:{port}"
        self.task       = None
        self.job        = None
        self.thread     = None

    def start(self, command:Command):
        if   command.flag == Flag.PARENT: Constructor = Parent
        elif command.flag == Flag.MCAST:  Constructor = Mcast
        else:                             raise RuntimeError()

        self.task   = Constructor(command)
        self.job    = self.task.make()

        self.L.log(message=f"STARTED JOB[{self.job.id}:{self.job.addr}]")
        self.thread = threading.Thread(target=self.execute, args=(self.task,))
        self.thread.start()

        return self.job

    def report(self, job:Job):
        if self.job is None or self.task is None: 
            raise RuntimeError()

        if job.id != self.job.id:
            raise RuntimeError()

        # if job and/or it's dependencies haven't finished
        if not self.task.complete() or self.thread.is_alive():
            return job
        else:
            ret = self.task.resolve()
            self.task   = None
            self.job    = None
            self.thread = None

            self.L.log(message=f"FINISHED JOB[{ret.id}:{ret.addr}]")
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

        self.collect(t)

    def collect(self, t:Task):
        if len(t.dependencies) == 0: 
            return

        while True:
            self.timer.sleep_sec(1)

            if t.complete(): 
                break
        
            for i, job in enumerate(t.dependencies):
                if job.end: continue 
        
                m   = self.message(src=self.addr, dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
                r   = self.handshake(m)
                ret = self.verify(m, r, field="job")

                if ret.end: 
                    t.dependencies[i] = ret
                    self.L.log(message=f"COLLECTED DEPENDENCY[{i}][{job.id}:{job.addr}]")


class Worker(Node):
    def __init__(self, name:str, ip:str, port:str):
        super().__init__(name=name, stype=zmq.REP)
        self.addr       = f"{ip}:{port}"
        self.controller = Controller(name="CONTROLLER", ip=ip, port=port)
        self.L          = Logger(name=f"{name}:{ip}")

    def go(self):
        self.bind(protocol="tcp", ip=self.ip, port=self.port)
        self.L.state(f"{self.name} UP")
        try:
            while(True):
                m = self.recv_message()
                self.L.state(f"STATE[{Type.Name(m.type)}]")

                match m.type:
                    case Type.CONNECT: self.connectACK(m)
                    case Type.COMMAND: self.commandACK(m)
                    case Type.REPORT:  self.reportACK(m)
                    case Type.ERR:     self.errorACK(m)
                    case _:                   raise NotImplementedError()

        except Exception as e:
            self.L.log("INTERRUPTED!")
            raise e

        finally:
            self.L.flush()
            self.socket.close()

    def connectACK(self, m:Message):
        return self.ack_message(m)

    def commandACK(self, m:Message):
        if not m.mdata.HasField("command"): 
            return self.err_message(m, desc=f"COMMAND[{self.ipaddr(self.addr)}] FORMAT ERR")

        if not self.controller.task is None:
            return self.err_message(m, desc=f"COMMAND[{self.ipaddr(self.addr)}] WORKER BUSY ERR")

        c = m.mdata.command
        job = self.controller.start(c)
        return self.ack_message(m, mdata=Metadata(job=job))

    def reportACK(self, m:Message):
        if not m.mdata.HasField("job"): 
            return self.err_message(m, desc=f"REPORT[{self.addr}] FORMAT ERR")
        
        job = m.mdata.job
        job = self.controller.report(job)
        return self.ack_message(m, mdata=Metadata(job=job))

    def errorACK(self, m:Message):
        raise NotImplementedError()
