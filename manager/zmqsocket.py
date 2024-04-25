import zmq
import time
import sys

from enum import Enum
from .message_pb2 import Message

class LOG_LEVEL(Enum):
    NONE = 1 
    DEBUG = 2 
    ERROR = 3

class Socket():
    def __init__(self, protocol:str, ip:str, port:str, type, LOG_LEVEL:LOG_LEVEL):
        self.LOG_LEVEL = LOG_LEVEL
        self.protocol = protocol 
        self.ip = ip 
        self.port = port
        self.format = f"{protocol}://{ip}:{port}"
        self.context = zmq.Context()
        self.socket  = self.context.socket(type)

    def log(self, string:str):
        if (self.LOG_LEVEL == LOG_LEVEL.NONE): return 
        print(f"{string}")

    def bind(self):
        self.socket.bind(self.format)
        self.log(f"BOUND => {self.ip}:{self.port}")

    def connect(self):
        self.socket.connect(self.format)
        self.log(f"CONNECTED => {self.ip}:{self.port}")

    def close(self):
        self.socket.close()
        self.log(f"CLOSED => {self.ip}:{self.port}")

    def recv(self, *args, **kwargs):
        ret = self.socket.recv(*args, **kwargs)
        sz = sys.getsizeof(ret)
        self.log(f"RECV => {sz}")
        return ret

    def send(self, *args, **kwargs):
        ret = self.socket.send(*args, **kwargs)
        self.log(f"SENT")
        return ret

    def recv_string(self, *args, **kwargs):
        return self.socket.recv_string(*args, **kwargs)

    def send_string(self, *args, **kwargs):
        return self.socket.send_string(*args, **kwargs)

    def recv_message(self) -> Message:
        m = Message()
        m.ParseFromString(self.recv())
        return m

    def send_message(self, m:Message):
        data = m.SerializeToString()
        return self.send(data)

    def set_message(self, m:Message, id:int, data:str):
        ts = int(time.time_ns() / 1_000)
        m.id    = id
        m.ts    = ts
        m.data  = data

class ReplySocket(Socket):
    def __init__(self, protocol:str, ip:str, port:str, LOG_LEVEL:LOG_LEVEL):
        super().__init__(protocol, ip, port, zmq.REP, LOG_LEVEL)

    def bind(self):
        super().bind()


class RequestSocket(Socket):
    def __init__(self, protocol:str, ip:str, port:str, LOG_LEVEL:LOG_LEVEL):
        super().__init__(protocol, ip, port, zmq.REQ, LOG_LEVEL)

    def connect(self):
        super().connect()
