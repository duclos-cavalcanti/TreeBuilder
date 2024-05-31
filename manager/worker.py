from .node      import Node
from .message   import *
from .types     import Logger
from .scheduler import Scheduler

import zmq
import logging

class Worker(Node):
    def __init__(self, ip:str, port:str, verbosity=False):
        super().__init__(stype=zmq.REP)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"
        self.verbosity  = verbosity

        self.scheduler  = Scheduler(self.addr)
        self.L          = Logger(name=f"worker:{self.addr}")

    def go(self):
        self.bind(protocol="tcp", ip=self.ip, port=self.port)
        try:
            while(True):
                m = self.recv_message()

                self.L.state(f"RECV[{Type.Name(m.type)}]")
                self.L.logm(message="", m=m, level=logging.DEBUG)

                match m.type:
                    case Type.CONNECT: r = self.connectACK(m)
                    case Type.COMMAND: r = self.commandACK(m)
                    case Type.REPORT:  r = self.reportACK(m)
                    case Type.ERR:     r = self.errorACK(m)
                    case Type.LOG:     r = self.logACK(m)
                    case _:                   raise NotImplementedError()

                self.L.logm(message="SENT[{Type.Name(r.type)}]", m=r, level=logging.DEBUG)

        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")

        except Exception as e:
            raise e

        finally:
            self.L.flush()
            self.socket.close()

    def connectACK(self, m:Message):
        self.L.log(f"CONNECTION[{m.src}]")
        return self.ack_message(m)

    def commandACK(self, m:Message):
        if not m.mdata.HasField("command"): 
            return self.err_message(m, desc=f"COMMAND[{self.addr}] FORMAT ERR")

        c = m.mdata.command
        job = self.scheduler.add(c)

        self.L.log(f"COMMAND[{Flag.Name(c.flag)}][{m.src}] RECV")
        return self.ack_message(m, mdata=Metadata(job=job))

    def reportACK(self, m:Message):
        if not m.mdata.HasField("job"): 
            return self.err_message(m, desc=f"REPORT[{self.addr}] FORMAT ERR")
        
        job = m.mdata.job
        job = self.scheduler.report(job)

        self.L.log(f"REPORT[{Flag.Name(job.flag)}][{m.src}] RECV")
        return self.ack_message(m, mdata=Metadata(job=job))

    def errorACK(self, m:Message):
        raise NotImplementedError()

    def logACK(self, m:Message):
        self.L.log(f"LOG[{m.src}] RECV")
        self.L.flush()
        return self.ack_message(m)
