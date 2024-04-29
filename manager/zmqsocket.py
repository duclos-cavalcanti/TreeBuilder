import zmq
import time
import sys

from enum import Enum
from .message_pb2 import Message, MessageType

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
        self.context = zmq.Context()
        self.socket  = self.context.socket(type)

    def log(self, string:str):
        if (self.LOG_LEVEL == LOG_LEVEL.NONE): return 
        print(f"{string}")

    def bind(self, protocol:str, ip:str, port:str):
        format = f"{protocol}://{ip}:{port}"
        self.socket.bind(format)
        self.log(f"BOUND => {self.ip}:{self.port}")

    def connect(self, protocol:str, ip:str, port:str):
        format = f"{protocol}://{ip}:{port}"
        self.socket.connect(format)
        self.log(f"CONNECTED => {ip}:{port}")

    def disconnect(self, protocol:str, ip:str, port:str):
        format = f"{protocol}://{ip}:{port}"
        self.socket.disconnect(format)
        self.log(f"DISCONNECTED => {ip}:{port}")

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
        ret = self.send(data)
        return ret

    def expect_message(self, t:MessageType, id:int, data:str) -> bool:
        m = self.recv_message()
        if m.type == t and m.id == id and m.data == data: return True, m
        return False, m

class ReplySocket(Socket):
    def __init__(self, protocol:str, ip:str, port:str, LOG_LEVEL:LOG_LEVEL):
        super().__init__(protocol, ip, port, zmq.REP, LOG_LEVEL)

    def bind(self, *args, **kwargs):
        super().bind(*args, **kwargs)


class RequestSocket(Socket):
    def __init__(self, protocol:str, ip:str, port:str, LOG_LEVEL:LOG_LEVEL):
        super().__init__(protocol, ip, port, zmq.REQ, LOG_LEVEL)

    def connect(self, *args, **kwargs):
        super().connect(*args, **kwargs)
