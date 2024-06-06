from .node      import Node
from .message   import *
from .types     import Logger
from .scheduler import Scheduler

import zmq

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

                match m.type:
                    case Type.CONNECT: self.connectACK(m)
                    case Type.COMMAND: self.commandACK(m)
                    case Type.REPORT:  self.reportACK(m)
                    case Type.ERR:     self.errorACK(m)
                    case _:                   raise NotImplementedError()

        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")

        except Exception as e:
            raise e

        finally:
            self.L.flush()
            self.socket.close()

    def connectACK(self, m:Message):
        return self.ack_message(m)

    def commandACK(self, m:Message):
        if not m.mdata.HasField("command"): 
            return self.err_message(m, desc=f"COMMAND[{self.addr}] FORMAT ERR")

        c = m.mdata.command
        job = self.scheduler.add(c)
        return self.ack_message(m, mdata=Metadata(job=job))

    def reportACK(self, m:Message):
        if not m.mdata.HasField("job"): 
            return self.err_message(m, desc=f"REPORT[{self.addr}] FORMAT ERR")
        
        job = m.mdata.job
        job = self.scheduler.report(job)
        return self.ack_message(m, mdata=Metadata(job=job))

    def errorACK(self, m:Message):
        raise NotImplementedError()
