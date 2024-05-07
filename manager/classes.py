from .zmqsocket   import LOG_LEVEL
from .message_pb2 import Message, MessageType, MessageFlag

from .node      import Node
from .tree      import Tree
from .utils     import read_yaml

import zmq
import os
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

    def fetch_step(self):
        if len(self.steps) == 0: return None
        s = self.steps[0]
        s["i"] = self.tick
        self.steps.pop(0)
        return s

    def process_step(self, s:dict, callback:Callable):
        self.print(f"-- STEP[{s['i']}]: {s['action']} => START --", prefix="\033[31m", suffix="\033[0m")
        callback()
        self.print(f"-- STEP[{s['i']}]: {s['action']} => COMPLETE --", prefix="\033[92m", suffix="\033[0m")

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
            self.send_message(id, MessageType.CONNECT, f=MessageFlag.NONE, data=data)
            self.expect_message(id, MessageType.ACK, MessageFlag.NONE, data)
            self.disconnect(addr)
            print(F"ESTABLISHED => {addr}")

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
        self.send_message(id, MessageType.COMMAND, f=MessageFlag.PARENT, data=data)
        self.expect_message(id, MessageType.ACK, MessageFlag.PARENT, [])

    def run(self):
        try:
            while(True):
                step = self.fetch_step()
                if not step: break
                match step["action"]:
                    case "CONNECT": self.process_step(step, self.establish)
                    case "ROOT":    self.process_step(step, self.root)
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

    def parent(self, data:list):
        sel   = int(data[0])
        rate  = int(data[1])
        dur   = int(data[2])
        addrs = data[3:]
        self.print_addrs(addrs, f"CHILDREN => SELECT {sel}")
        pnode = Node(f"{self.name}::PARENT", self.ip, "8081", zmq.REQ, self.LOG_LEVEL)
        for addr in addrs:
            id = self.tick
            data = [f"{addr}"]
            pnode.connect(addr)
            pnode.send_message(id, MessageType.CONNECT, f=MessageFlag.NONE, data=data)
            pnode.expect_message(id, MessageType.ACK, MessageFlag.NONE, data)
            pnode.send_message(id, MessageType.COMMAND, f=MessageFlag.CHILD, data=data)
            pnode.expect_message(id, MessageType.ACK, MessageFlag.CHILD, data)
            print(f"ACKNOWLEDGED => {addr}=CHILD")
            pnode.disconnect(addr)
        pnode.socket.close()
        command = f"./bin/parent -a {addrs} -r {rate} -d {dur}"
        print(f"RUNNING => {command}")

    def child(self, command:str):
        print(f"RUNNING => {command}")

    def connectACK(self, m:Message):
        self.print_message(m)
        id = m.id
        data = [f"{self.socket.ip}:{self.socket.port}"]
        self.send_message(id, MessageType.ACK, f=MessageFlag.NONE, data=data)

    def commandACK(self, m:Message):
        self.print_message(m)
        if m.flag == MessageFlag.PARENT:
            self.parent(m.data)
            id = m.id
            data = []
            self.send_message(id, MessageType.ACK, f=m.flag, data=data)

        elif m.flag == MessageFlag.CHILD:
            command = f"./bin/child -i {self.ip} -p {int(self.socket.port) - 1000}"
            self.child(command)
            id = m.id
            data = [f"{command}"]
            self.send_message(id, MessageType.ACK, f=MessageFlag.CHILD, data=data)

        else:
            id = m.id
            data = []
            self.send_message(id, MessageType.ACK, f=m.flag, data=data)

    def run(self):
        self.socket.bind("tcp", self.socket.ip, self.socket.port)
        try:
            while(True):
                m = self.recv_message()
                match m.type:
                    case MessageType.CONNECT: self.connectACK(m)
                    case MessageType.COMMAND: self.commandACK(m)
                    case _:                   self.err_message(m, f"UNEXPECTED MSG: {MessageType.Name(MessageType.ACK)} | {m.id}")
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



