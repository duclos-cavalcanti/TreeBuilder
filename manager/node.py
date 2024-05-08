from .zmqsocket import ReplySocket, RequestSocket, LOG_LEVEL
from .message_pb2 import Message, MessageType, MessageFlag

import zmq
import time

from typing import  Tuple

class Node():
    def __init__(self, name:str, ip:str, port:str, type, LOG_LEVEL=LOG_LEVEL.NONE):
        self.name = name.upper()
        self.ip   = ip
        self.port = port
        self.tick = 0
        self.LOG_LEVEL = LOG_LEVEL

        if type   == zmq.REP:   self.socket = ReplySocket(self.name, protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)
        elif type == zmq.REQ:   self.socket = RequestSocket(self.name, protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)
        else:                   raise NotImplementedError(f"ZMQSOCKET TYPE: {type}")

    def message(self, id:int, t:MessageType, f:MessageFlag, data:list):
        m = Message()
        m.id    = id
        m.ts    = int(time.time_ns() / 1_000)
        m.type  = t
        m.flag  = f
        if data: 
            for d in data: 
                m.data.append(str(d))
        return m

    def send_message(self, id:int, t:MessageType, f:MessageFlag=MessageFlag.NONE, data:list=[]):
        m = self.message(id, t, f, data)
        data = m.SerializeToString()
        self.socket.send(data)

    def send_message_ack(self, m:Message, data:list=[]):
        r = self.message(m.id, MessageType.ACK, m.flag, data)
        data = r.SerializeToString()
        self.socket.send(data)

    def recv_message(self) -> Message:
        m = Message()
        m.ParseFromString(self.socket.recv())
        return m

    def expect_message(self, id:int, t:MessageType, f:MessageFlag) -> Tuple[bool, Message]:
        m = self.recv_message()
        if (m.id   == id and 
            m.type == t  and
            m.flag == f):
            return True, m
        return False, m

    def handshake_connect(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.CONNECT, f=MessageFlag.NONE, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.NONE)
        if not ok or addr != m.data[0]: self.err_message(m, "CONNECT ACK ERR")
        print(f"ESTABLISHED => {addr}")
        ret = m.data
        return ret

    def handshake_parent(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.COMMAND, f=MessageFlag.PARENT, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.PARENT)
        if not ok: self.err_message(m, "PARENT ACK ERR")
        print(f"PARENT => {addr}")
        ret = m.data
        return ret

    def handshake_child(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.COMMAND, f=MessageFlag.CHILD, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.CHILD)
        if not ok: self.err_message(m, "CHILD ACK ERR")
        print(f"CHILD => {addr}")
        ret = m.data
        return ret

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


