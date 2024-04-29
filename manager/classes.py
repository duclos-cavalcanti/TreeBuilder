from .zmqsocket import Message, MessageType, ReplySocket, RequestSocket, LOG_LEVEL
from .utils     import read_yaml

import os
import time

class Node():
    def __init__(self):
        self.tick = 0
        pass

    def set_message(self, m:Message, t:MessageType, id:int, data:str):
        ts = int(time.time_ns() / 1_000)
        m.id    = id
        m.ts    = ts
        m.type  = t
        m.data  = data
        return m

    def print_message(self, m:Message, header:str=""):
        print(f"{header}{{")
        print(f"    ID: {m.id}")
        print(f"    TS: {m.ts}")
        print(f"    TYPE: {MessageType.Name(m.type)}")
        print(f"    DATA: {m.data}\n}}")

    def err_message(self, m:Message, s:str):
        self.print_message(m, header="ERR MESSAGE:")
        raise RuntimeError(f"{s}")

class Manager(Node):
    def __init__(self, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__()
        self.socket = RequestSocket(protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)

    def read_config(self, path:str=""):
        if not path:
            path = os.path.join(os.getcwd(), "manager", "scripts", "default.yaml")
        self.config     = read_yaml(path)
        self.addrs      = self.config["addrs"]
        self.workers    = self.addrs[1:]
        self.K          = self.config["hyperparameter"]
        self.n_nodes    = int(self.config["nodes"])
        self.steps      = self.config["steps"]

    def fetch_step(self):
        if len(self.steps) == 0: return None
        s = self.steps[0]
        self.steps = self.steps[1:]
        self.tick += 1
        s["i"] = self.tick
        return s

    def connect(self, step, targets:list=[]):
        if not targets: 
            targets = self.workers

        for addr in targets:
            ip = addr.split(":")[0]
            port = addr.split(":")[1]
            self.socket.connect("tcp", ip, port)
            print(f"CONNECTED => {ip}:{port}")

        for addr in targets:
            id = self.tick
            data = f"{addr.split(':')[0]}:{addr.split(':')[1]}"
            self.socket.send_message(self.set_message(Message(), MessageType.CONNECT, id, data))
            ok, r = self.socket.expect_message(MessageType.ACK, id, data)
            if not ok: self.err_message(r, f"EXPECTED MSG: ACK | {id}")

        print(f"-- STEP[{step['i']}]: CONNECT => COMPLETE --")

    def noop(self, step):
        i = 0
        limit = int(step["val"])
        while i < limit:
            time.sleep(1)
            print("SLEEPING...")
            i += 1
        print(f"-- STEP[{step['i']}]: SLEEP => COMPLETE --")

    def run(self, config_path:str=""):
        self.read_config(config_path)
        S = self.socket

        try:
            while(True):
                step = self.fetch_step()
                if not step: break
                match step["action"]:
                    case "CONNECT": self.connect(step)
                    case "SLEEP":   self.noop(step)
                    case _:         raise NotImplementedError(f"ERR STEP[{step.i}]: {step.action}")

            print("FINISHED!")
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        S.close()



class Worker(Node):
    def __init__(self, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__()
        self.socket = ReplySocket(protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)

    def ack_connect(self, m:Message):
        id = m.id
        data = f"{self.socket.ip}:{self.socket.port}"
        self.socket.send_message(self.set_message(Message(), MessageType.ACK, id, data))

    def run(self):
        self.socket.bind("tcp", "*", self.socket.port)

        try:
            while(True):
                m = self.socket.recv_message()
                self.print_message(m)
                match m.type:
                    case MessageType.CONNECT: self.ack_connect(m)
                    case _:                   
                        id = m.id
                        t = MessageType.Name(MessageType.ACK)
                        self.err_message(m, f"UNEXPECTED MSG: {t} | {id}")
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



