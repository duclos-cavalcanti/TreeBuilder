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
        J = Job(addr=self.hostaddr, command=C)
        self.jobs[self.exec(target=self._run, args=(J,))] = J
        return J

    def parent_job(self, sel:int, rate:int, dur:int, addrs:list):
        faddrs = []
        for a in addrs:
            split = a.split(":")
            ip    = split[0]
            port  = split[1]
            port  = str(int(port) - 1000)
            faddrs.append(f"{ip}:{port}")

        C = "./bin/parent -a " + " ".join(f"{a}" for a in faddrs) + f" -r {rate} -d {dur}"
        J = Job(addr=self.hostaddr, command=C, param=sel)
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

    def parent_resolve(self, job:Job):
        print(job)
        sel = job.param
        output = job.out
        job.out = output[:2]
        job.out[1] = f"{sel}"
        return job

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
        t, job = self.find(Job(arr=data))
        job.complete = (job.end and job.is_resolved())
        if job.complete: 
            job.concatenate()
            del self.jobs[t]

        if job.complete and flag == MessageFlag.MANAGER:
            job = self.parent_resolve(job)

        print(f"JOB[{job.id}] => END={job.end}")
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



