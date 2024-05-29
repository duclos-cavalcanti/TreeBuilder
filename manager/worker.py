from .node      import Node
from .message   import *
from .scheduler import Scheduler
from .utils     import *

import zmq

class Worker(Node):
    def __init__(self, ip:str, port:str, verbosity=False):
        super().__init__(f"WORKER:{ip}", stype=zmq.REP, verbosity=verbosity)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"
        self.tick       = 1

        self.buffer = []
        self.scheduler  = Scheduler(self.addr, self.buffer)

    def go(self):
        self.bind(protocol="tcp", ip=self.ip, port=self.port)
        try:
            while(True):
                m = self.recv_message()

                print_color(f"------> RECEIVED", color=RED)
                print(f"MSG => \n{m}")

                print_color(f"------>", color=YLW)
                match m.type:
                    case Type.CONNECT: r = self.connectACK(m)
                    case Type.COMMAND: r = self.commandACK(m)
                    case Type.REPORT:  r = self.reportACK(m)
                    case Type.ERR:     r = self.errorACK(m)
                    case _:                   raise NotImplementedError()

                print_color(f"<------", color=YLW)
                print(f"RPL => \n{r}")
                print_color(f"<------ PROCESSED", color=GRN)
                self.tick += 1

        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()

    def connectACK(self, m:Message):
        r = Message(id=m.id, src=self.addr, type=Type.ACK)
        return self.send_message(r)

    def commandACK(self, m:Message):
        if not m.mdata.HasField("command"): 
            error = Error(desc=f"COMMAND[{self.addr}] FORMAT ERR")
            e = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ERR, mdata=Metadata(error=error))
            return self.send_message(e)

        command = m.mdata.command
        job = self.scheduler.add(command, m.flag)

        r = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ACK, mdata=Metadata(job=job))
        return self.send_message(r)

    def reportACK(self, m:Message):
        if not m.mdata.HasField("job"): 
            error = Error(desc=f"REPORT[{self.addr}] FORMAT ERR")
            e = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ERR, mdata=Metadata(error=error))
            return self.send_message(e)
        
        job = m.mdata.job
        job, flag = self.scheduler.report(job)

        r = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ACK, flag=flag, mdata=Metadata(job=job))
        return self.send_message(r)

    def errorACK(self, m:Message):
        raise NotImplementedError()
