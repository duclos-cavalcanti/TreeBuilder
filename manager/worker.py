from .zmqsocket   import LOG_LEVEL
from .message_pb2 import Message, MessageType, MessageFlag

from .node      import Node
from .job       import Job
from .utils     import LOG_LEVEL
from .utils     import *

import zmq

class Worker(Node):
    def __init__(self, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REP, LOG_LEVEL)

    def child_job(self):
        C = f"./bin/child -i {self.ip} -p {int(self.port) - 1000}"
        C=f"sleep 10 && echo CHILD DONE"
        J = Job(addr=self.hostaddr, command=C)
        self.jobs[self.exec(target=self._run, args=(J,))] = J
        return J

    def parent_job(self, sel:int, rate:int, dur:int, addrs:list):
        C = "./bin/parent -a " + " ".join(f"{a}" for a in addrs) + f" -r {rate} -d {dur}"
        C = f"sleep 10 && echo PARENT DONE"
        J = Job(addr=self.hostaddr, command=C)
        H = self._helper(zmq.REQ)

        for addr in addrs:
            id = self.tick
            data = [addr, self.hostaddr]
            H.connect(addr)
            r = H.handshake(id, MessageType.COMMAND, MessageFlag.CHILD, data, addr)
            rjob = Job(arr=r.data)
            J.deps.append(rjob)
            H.disconnect(addr)

        self.jobs[self.exec(target=self._run, args=(J,))] = J
        self.guards[self.exec(target=self._guard, args=(J,))] = J

        return J

    def commandACK(self, m:Message):
        id, _, flag, data = self.parse_message(m)
        match flag:
            case MessageFlag.PARENT: 
                if len(data) <= 3: 
                    self.err_message(m, "PARENT COMMAND ERR")
                sel   = int(data[0])
                rate  = int(data[1])
                dur   = int(data[2])
                addrs = data[3:]
                job = self.parent_job(sel, rate, dur, addrs)
                self.send_message(id=id, t=MessageType.ACK, flag=flag, data=job.to_arr())

            case MessageFlag.CHILD:  
                if len(data) < 2 or self.hostaddr != data[0]: 
                    self.err_message(m, "CHILD COMMAND ERR")
                job = self.child_job()
                self.send_message(id=id, t=MessageType.ACK, flag=flag, data=job.to_arr())

            case _:
                raise NotImplementedError(f"COMMAND FLAG: {MessageFlag.Name(flag)}")

    def reportACK(self, m:Message):
        id, _, flag, data = self.parse_message(m)
        if flag == MessageFlag.MANAGER:
            rjob = Job(arr=data)
            t, job = self.find(rjob)
            job.end = (not t.is_alive() and job.is_resolved())
            if job.end: 
                del self.jobs[t]
                del t
                t, _ = self.find(rjob, dct=self.guards)
                del self.guards[t]
                del t

            print(f"JOB[{job.id}] => COMPLETE={job.end}")
            self.send_message(id=id, t=MessageType.ACK, flag=flag, data=job.to_arr())
        else:
            t, job = self.find(Job(arr=data))
            if not t.is_alive(): 
                del self.jobs[t]
                del t

            print(f"JOB[{job.id}] => COMPLETE={job.end}")
            self.send_message(id=id, t=MessageType.ACK, flag=flag, data=job.to_arr())

    def connectACK(self, m:Message):
        id, _, flag, data = self.parse_message(m)
        if self.hostaddr != data[0]: 
            self.err_message(m, "CONNECT ERR")
        self.send_message(id=id, t=MessageType.ACK, flag=flag, data=[self.hostaddr])

    def go(self):
        self.socket.bind(protocol="tcp", ip=self.ip, port=self.port)
        try:
            while(True):
                m = self.recv_message()
                print_color(f"------>", color=RED)
                print_color(f"MESSAGE[{m.id}]: {MessageType.Name(m.type)} => RECEIVED", color=RED)

                self.print_message(m)
                match m.type:
                    case MessageType.CONNECT: self.connectACK(m)
                    case MessageType.COMMAND: self.commandACK(m)
                    case MessageType.REPORT:  self.reportACK(m)
                    case _:                   self.err_message(m, f"UNEXPECTED MSG: {MessageType.Name(MessageType.ACK)} | {m.id}")

                print_color(f"MESSAGE[{m.id}]: {MessageType.Name(m.type)} => PROCESSED", color=GRN)
                print_color(f"<------", color=GRN)
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



