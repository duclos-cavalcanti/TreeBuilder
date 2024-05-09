import zmq
import sys

from .utils import LOG_LEVEL

class Socket():
    def __init__(self, name:str, protocol:str, ip:str, port:str, type, LOG_LEVEL:LOG_LEVEL):
        self.name = name
        self.protocol = protocol 
        self.ip = ip 
        self.port = port
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
        self.log(f"RECV[{self.i}] => {sz}")
        return ret

    def send(self, *args, **kwargs):
        ret = self.socket.send(*args, **kwargs)
        self.log(f"SENT[{self.i}]")
        return ret

    def recv_string(self, *args, **kwargs):
        return self.socket.recv_string(*args, **kwargs)

    def send_string(self, *args, **kwargs):
        return self.socket.send_string(*args, **kwargs)

class ReplySocket(Socket):
    def __init__(self, name:str, protocol:str, ip:str, port:str, LOG_LEVEL:LOG_LEVEL):
        super().__init__(name, protocol, ip, port, zmq.REP, LOG_LEVEL)

    def bind(self, *args, **kwargs):
        super().bind(*args, **kwargs)

    def send(self, *args, **kwargs):
        super().send(*args, **kwargs)
        self.i += 1


class RequestSocket(Socket):
    def __init__(self, name:str, protocol:str, ip:str, port:str, LOG_LEVEL:LOG_LEVEL):
        super().__init__(name, protocol, ip, port, zmq.REQ, LOG_LEVEL)

    def connect(self, *args, **kwargs):
        super().connect(*args, **kwargs)

    def recv(self, *args, **kwargs):
        ret = super().recv(*args, **kwargs)
        self.i += 1
        return ret
