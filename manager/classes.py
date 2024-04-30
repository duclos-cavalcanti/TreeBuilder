from .zmqsocket import Message, MessageType, MessageFlag, Socket, ReplySocket, RequestSocket, LOG_LEVEL
from .tree      import Tree
from .utils     import read_yaml

import zmq
import os
import time
import random

from typing import Callable, Tuple

class Node():
    def __init__(self, name:str, ip:str, port:str, type, LOG_LEVEL=LOG_LEVEL.NONE):
        self.name = name.upper()
        self.ip = ip
        self.tick = 0
        self.LOG_LEVEL = LOG_LEVEL

        if type   == zmq.REP:   self.socket = ReplySocket(self.name, protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)
        elif type == zmq.REQ:   self.socket = RequestSocket(self.name, protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)
        else:                   raise NotImplementedError(f"TYPE: {type}")

    def message(self, id:int, t:MessageType, f:MessageFlag, data:list):
        m = Message()
        m.id    = id
        m.ts    = int(time.time_ns() / 1_000)
        m.type  = t
        m.flag  = f
        if data: 
            for d in data: 
                m.data.append(d)
        return m

    def send_message(self, id:int, t:MessageType, f:MessageFlag=MessageFlag.NONE, data:list=[]):
        self.socket.send_message(self.message(id, t, f, data))

    def recv_message(self):
        return self.socket.recv_message()

    def expect_message(self, id:int, t:MessageType, f:MessageFlag, data:list) -> Tuple[bool, Message]:
        m = self.recv_message()
        if (m.id   == id and 
            m.type == t  and
            m.flag == f  and
            m.data == data): 
            return True, m
        return False, m

    def connect(self, target:str):
        ip = target.split(":")[0]
        port = target.split(":")[1]
        self.socket.connect("tcp", ip, port)

    def disconnect(self, target:str):
        ip = target.split(":")[0]
        port = target.split(":")[1]
        self.socket.disconnect("tcp", ip, port)

    def print(self, text:str, prefix:str="", suffix:str=""):
        print(f"{prefix}{text}{suffix}")

    def print_addrs(self, addrs:list, header:str):
        print(f"{header}: {{")
        for i,a in enumerate(addrs): print(f"\t{i} => {a}")
        print("}")

    def print_message(self, m:Message, header:str=""):
        print(f"{header}{{")
        print(f"    ID: {m.id}")
        print(f"    TS: {m.ts}")
        print(f"    TYPE: {MessageType.Name(m.type)}")
        print(f"    FLAG: {MessageFlag.Name(m.flag)}")
        print(f"    DATA: [")
        for d in m.data: print(f"         {d}")
        print(f"    ]\n}}")

    def err_message(self, m:Message, s:str):
        self.print_message(m, header="ERR MESSAGE: ")
        raise RuntimeError(f"{s}")

class Manager(Node):
    def __init__(self, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REQ, LOG_LEVEL)
        self.ip = ip 
        self.config     = read_yaml(os.path.join(os.getcwd(), "manager", "default.yaml"))
        self.workers    = self.config["addrs"][1:]
        self.pool       = self.workers
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
        data = [ "2" ]
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

    def parent(self, children:list, f:int):
        print("PARENT")
        pnode = Node(f"{self.name}::PARENT", self.ip, "8081", zmq.REQ, self.LOG_LEVEL)
        for c in children:
            id = self.tick
            data = [f"{c}"]
            pnode.connect(c)
            pnode.send_message(id, MessageType.CONNECT, f=MessageFlag.NONE, data=data)
            pnode.expect_message(id, MessageType.ACK, MessageFlag.NONE, data)
            pnode.disconnect(c)
        pnode.socket.close()

    def connectACK(self, m:Message):
        self.print_message(m)
        id = m.id
        data = [f"{self.socket.ip}:{self.socket.port}"]
        self.send_message(id, MessageType.ACK, f=MessageFlag.NONE, data=data)

    def commandACK(self, m:Message):
        self.print_message(m)
        if m.flag == MessageFlag.PARENT:
            f = int(m.data[0])
            children = m.data[1:]
            self.print_addrs(children, f"CHILDREN => SELECT {f}")
            self.parent(children, f)

        id = m.id
        data = []
        self.send_message(id, MessageType.ACK, f=m.flag, data=data)

    def run(self):
        self.socket.bind("tcp", self.socket.ip, self.socket.port)
        try:
            while(True):
                m = self.socket.recv_message()
                match m.type:
                    case MessageType.CONNECT: self.connectACK(m)
                    case MessageType.COMMAND: self.commandACK(m)
                    case _:                   self.err_message(m, f"UNEXPECTED MSG: {MessageType.Name(MessageType.ACK)} | {m.id}")
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



