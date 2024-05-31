from .node      import Node
from .message   import *
from .scheduler import Scheduler
from .utils     import *
from .ds        import Logger

from google.protobuf.json_format import MessageToJson, MessageToDict

import zmq

class Worker(Node):
    def __init__(self, ip:str, port:str, verbosity=False):
        super().__init__(f"WORKER:{ip}", stype=zmq.REP, verbosity=verbosity)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"
        self.tick       = 1

        self.logger     = Logger(file=f"/volume/worker_{self.addr}.json")
        self.scheduler  = Scheduler(self.addr, self.logger)

        self.children = []

    def go(self):
        self.bind(protocol="tcp", ip=self.ip, port=self.port)
        try:
            while(True):
                m = self.recv_message()

                print_color(f"------> RECEIVED", color=RED)
                print(f"MSG => \n{m}")

                self.logger.event(f"MSG", MessageToDict(m))
                print_color(f"------>", color=YLW)

                match m.type:
                    case Type.CONNECT: r = self.connectACK(m)
                    case Type.COMMAND: r = self.commandACK(m)
                    case Type.REPORT:  r = self.reportACK(m)
                    case Type.ORDER:   r = self.orderACK(m)
                    case Type.ERR:     r = self.errorACK(m)
                    case Type.LOG:     r = self.logACK(m)
                    case _:                   raise NotImplementedError()

                self.logger.event(f"RPL", MessageToDict(r))
                print_color(f"<------", color=YLW)

                print(f"RPL => \n{r}")
                print_color(f"<------ PROCESSED", color=GRN)
                self.tick += 1

        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")

        except Exception as e:
            raise e

        finally:
            self.logger.dump()
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
        if command.flag == Flag.MCAST: command.data.extend([c for c in self.children])

        job = self.scheduler.add(command)
        r = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ACK, mdata=Metadata(job=job))
        return self.send_message(r)

    def reportACK(self, m:Message):
        if not m.mdata.HasField("job"): 
            error = Error(desc=f"REPORT[{self.addr}] FORMAT ERR")
            e = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ERR, mdata=Metadata(error=error))
            return self.send_message(e)
        
        job = m.mdata.job
        job = self.scheduler.report(job)

        r = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ACK, mdata=Metadata(job=job))
        return self.send_message(r)

    def orderACK(self, m:Message):
        if not m.mdata.HasField("order"): 
            error = Error(desc=f"ORDER[{self.addr}] FORMAT ERR")
            e = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ERR, mdata=Metadata(error=error))
            return self.send_message(e)

        order = m.mdata.order
        if order.flag == Flag.PARENT: 
            self.children = [a for a in order.data] if order.data else []
            self.logger.record(f"CHILDREN[{self.addr}]", [a for a in order.data], verbosity=True)
        else:                         
            raise NotImplementedError()

        r = Message(id=m.id, src=self.addr, ts=self.timer.ts(), type=Type.ACK)
        return self.send_message(r)

    def errorACK(self, m:Message):
        raise NotImplementedError()

    def logACK(self, m:Message):
        self.logger.dump()
        r = Message(id=m.id, src=self.addr, type=Type.ACK)
        return self.send_message(r)
