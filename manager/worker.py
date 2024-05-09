from .zmqsocket   import LOG_LEVEL
from .message_pb2 import Message, MessageType, MessageFlag

from .node      import Node, Job
import zmq

from typing import Callable

class Worker(Node):
    def __init__(self, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REP, LOG_LEVEL)

    def child_command(self) -> str:
        c = f"./bin/child -i {self.ip} -p {int(self.port) - 1000}"
        return f"sleep 10 && echo {self.hostaddr}"

    def childACK(self, m:Message):
        data = m.data
        if len(data) < 2 : 
            self.err_message(m, "CHILD COMMAND ERR")

        if self.hostaddr != data[1]: 
            self.err_message(m, "CHILD COMMAND ERR")

        job = Job(addr=self.hostaddr, 
                  command=self.child_command())
        self.exec_job(job)
        self.print_jobs()
        self.send_message_ack(m, data=job.to_arr())

    def parent_command(self, addrs, rate, dur) -> str:
        c = "./bin/parent -a " + " ".join(f"{a}" for a in addrs) + f" -r {rate} -d {dur}"
        return f"sleep 10 && echo {self.hostaddr}"

    def parentACK(self, m:Message):
        data = m.data
        if len(m.data) <= 3: 
            self.err_message(m, "PARENT COMMAND ERR")

        sel   = int(data[0])
        rate  = int(data[1])
        dur   = int(data[2])
        addrs = data[3:]
        nodes = []
        self.print_addrs(addrs, f"CHILDREN => SELECT {sel}")
        for i, addr in enumerate(addrs):
            n = Node(f"{self.name}::PARENT", self.ip, f"{int(self.port) + 1000 + i}", zmq.REQ, self.LOG_LEVEL)
            id = self.tick
            data = [f"{addr}"]
            n.connect(addr)
            _ = n.handshake_connect(id, data, addr)
            nodes.append(n)

        for n, addr in zip(nodes, addrs):
            id = self.tick
            data = [self.hostaddr , addr]
            _, d = n.handshake_child(id, data, addr)
            self.push_job(Job(arr=d))
            n.disconnect(addr)

        job = Job(addr=self.hostaddr,
                  command=self.parent_command(addrs, rate, dur))
        self.exec_job(job)
        self.print_jobs()
        self.send_message_ack(m, data=job.to_arr())

    def connectACK(self, m:Message):
        self.print_message(m, header="M: ")
        self.send_message_ack(m, data=[f"{self.socket.ip}:{self.port}"])

    def commandACK(self, m:Message):
        self.print_message(m, header="M: ")
        if   m.flag == MessageFlag.PARENT: self.parentACK(m)
        elif m.flag == MessageFlag.CHILD:  self.childACK(m)
        else:
            raise NotImplementedError(f"MESSAGE FLAG: {MessageFlag.Name(m.flag)}")

    def reportACK(self, m:Message):
        self.print_message(m, header="M: ")
        ref_job = Job(arr=m.data)
        ok, j, end = self.check_jobs(ref_job)
        if not ok: raise RuntimeError(f"WORKER HAS NO JOBS TO REPORT ON")
        if end: self.print_job(j, header=f"JOB DONE:")
        self.send_message_ack(m, data=j.to_arr())

    def process_message(self, m:Message, callback:Callable):
        self.print(f"------>", prefix="\033[31m", suffix="\033[0m")
        self.print(f"MESSAGE[{m.id}]: {MessageType.Name(m.type)} => RECEIVED", prefix="\033[31m", suffix="\033[0m")
        callback(m)
        self.print(f"MESSAGE[{m.id}]: {MessageType.Name(m.type)} => PROCESSED", prefix="\033[92m", suffix="\033[0m")
        self.print(f"<------", prefix="\033[92m", suffix="\033[0m")

    def run(self):
        self.socket.bind("tcp", self.socket.ip, self.port)
        try:
            while(True):
                m = self.recv_message()
                match m.type:
                    case MessageType.CONNECT: self.process_message(m, self.connectACK)
                    case MessageType.COMMAND: self.process_message(m, self.commandACK)
                    case MessageType.REPORT:  self.process_message(m, self.reportACK)
                    case _:                   self.err_message(m, f"UNEXPECTED MSG: {MessageType.Name(MessageType.ACK)} | {m.id}")
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



