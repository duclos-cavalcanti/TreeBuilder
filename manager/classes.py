from .zmqsocket   import LOG_LEVEL
from .message_pb2 import Message, MessageType, MessageFlag

from .node      import Node, Job
from .tree      import Tree
from .utils     import read_yaml, dict_to_arr

import zmq
import os
import time
import random

from typing import Callable

class Manager(Node):
    def __init__(self, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REQ, LOG_LEVEL)
        self.ip = ip 
        self.config     = read_yaml(os.path.join(os.getcwd(), "manager", "default.yaml"))
        self.workers    = self.config["addrs"][1:]
        self.pool       = self.workers
        self.rate       = self.config["rate"]
        self.duration   = self.config["duration"]
        self.K          = self.config["hyperparameter"]
        self.N          = int(self.config["nodes"])
        self.steps      = self.config["steps"]
        self.tree       = Tree(self.N)

    def print_node(self, n:dict, idx:int, header:str):
        print(f"{header}: {idx} => {n}")

    def step(self, action:str, desc:str) -> dict:
        d = {
            "action": action,
            "description": desc
        }
        return d

    def pop_step(self):
        if len(self.steps) == 0: return None
        s = self.steps[0]
        s["i"] = self.tick
        self.steps.pop(0)
        return s

    def push_step(self, s:dict):
        self.steps.append(s)

    def process_step(self, s:dict, callback:Callable):
        i   = s['i']
        act = s['action']
        dsc = s['description']
        self.print(f"STEP[{i}]: {act} => START    | {dsc}\t------>", prefix="\033[31m", suffix="\033[0m")
        callback()
        self.print(f"STEP[{i}]: {act} => COMPLETE | {dsc}\t<------", prefix="\033[92m", suffix="\033[0m")

    def select(self):
        pool = self.pool
        size = len(pool)
        idx = random.randint(0, size - 1)
        return idx

    def establish(self, targets:list=[]):
        if not targets: targets = self.workers
        for addr in targets:
            id = self.tick
            data = [f"{addr}"]
            self.connect(addr)
            self.handshake_connect(id, data, addr)
            self.disconnect(addr)

    def root(self):
        idx = self.select()
        root = self.pool[idx]
        self.pool.pop(idx)
        self.tree.set_root(root)
        self.print_node(root, idx, "CHOSEN")
        self.print_addrs(self.pool, "POOL")
        id = self.tick 
        data =  [ "2" ]
        data += [ self.rate ]
        data += [ self.duration ]
        data += self.pool
        self.connect(root)
        _, d = self.handshake_parent(id, data, root)
        job = Job(arr=d)
        self.push_job(job)
        self.print_jobs()
        self.disconnect(root)
        self.push_step(self.step(action="REPORT", desc="Check on external Jobs"))

    def report(self):
        time.sleep(1)
        j = self.pop_job()
        if not j:
            raise RuntimeError(f"MANAGER HAS NO EXTERNAL JOBS")
        addr = j.addr
        self.connect(addr)
        id = self.tick 
        data = j.to_arr()
        _, d = self.handshake_report(id, data, addr)
        self.disconnect(addr)
        ret = Job(arr=d)
        if ret.end == False:
            self.push_job(j)
            self.push_step(self.step(action="REPORT", desc="Check on external Jobs"))

    def run(self):
        try:
            while(True):
                step = self.pop_step()
                if not step: break
                match step["action"]:
                    case "CONNECT": self.process_step(step, self.establish)
                    case "ROOT":    self.process_step(step, self.root)
                    case "REPORT":  self.process_step(step, self.report)
                    case _:         raise NotImplementedError(f"ERR STEP: {step}")
                self.tick += 1

            print("FINISHED!")
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



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
        if len(m.data) <= 3 : 
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
        self.print_message(m, header="RECEIVED MESSAGE: ")
        self.send_message_ack(m, data=[f"{self.socket.ip}:{self.port}"])

    def commandACK(self, m:Message):
        self.print_message(m, header="RECEIVED MESSAGE: ")
        if   m.flag == MessageFlag.PARENT: self.parentACK(m)
        elif m.flag == MessageFlag.CHILD:  self.childACK(m)
        else:
            raise NotImplementedError(f"MESSAGE FLAG: {MessageFlag.Name(m.flag)}")

    def reportACK(self, m:Message):
        self.print_message(m, header="RECEIVED MESSAGE: ")
        ref_job = Job(arr=m.data)
        ok, j = self.check_jobs(ref_job)
        if not ok:
            raise RuntimeError(f"WORKER HAS NO JOBS TO REPORT ON")
        else: 
            j = ref_job
        self.send_message_ack(m, data=j.to_arr())

    def run(self):
        self.socket.bind("tcp", self.socket.ip, self.port)
        try:
            while(True):
                m = self.recv_message()
                match m.type:
                    case MessageType.CONNECT: self.connectACK(m)
                    case MessageType.COMMAND: self.commandACK(m)
                    case MessageType.REPORT:  self.reportACK(m)
                    case _:                   self.err_message(m, f"UNEXPECTED MSG: {MessageType.Name(MessageType.ACK)} | {m.id}")
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



