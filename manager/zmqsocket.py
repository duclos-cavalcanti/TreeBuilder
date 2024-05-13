import zmq
import sys

from .utils import LOG_LEVEL

class Socket():
    def __init__(self, name:str, type, LOG_LEVEL:LOG_LEVEL):
        self.name = name
        self.type = type
        self.context = zmq.Context()
        self.socket  = self.context.socket(type)
        self.i = 0
        self.LOG_LEVEL = LOG_LEVEL

    def log(self, string:str):
        if (self.LOG_LEVEL == LOG_LEVEL.NONE): return 
        print(f"{self.name}::{string}")


    def bind(self, protocol:str, ip:str, port:str):
        format = f"{protocol}://{ip}:{port}"
        self.socket.bind(format)
        self.log(f"BOUND => {ip}:{port}")

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
        self.log(f"CLOSED =>")

    def recv(self, *args, **kwargs):
        ret = self.socket.recv(*args, **kwargs)
        sz = sys.getsizeof(ret)
        if self.type != zmq.REP: self.log(f"RECV[{self.i}] => {sz}")
        return ret

    def send(self, *args, **kwargs):
        ret = self.socket.send(*args, **kwargs)
        if self.type != zmq.REQ: self.log(f"SENT[{self.i}]")
        return ret
