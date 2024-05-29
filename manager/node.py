from .message   import *
from .utils     import *
from .ds        import Timer

import zmq
import sys

from typing import  Optional

class Node():
    def __init__(self, name:str, stype:int, verbosity=False):
        self.name       = name.upper()
        self.verbosity  = verbosity
        self.context    = zmq.Context()
        self.socket     = self.context.socket(stype)
        self.timer      = Timer()

    def log(self, string:str):
        if (self.verbosity): 
            print(f"LOG[{self.name}]: {string}")

    def format(self, addr:str):
        protocol="tcp"
        ip = addr.split(":")[0]
        port = addr.split(":")[1]
        return f"{protocol}://{ip}:{port}"

    def bind(self, protocol:str, ip:str, port:str):
        format = f"{protocol}://{ip}:{port}"
        self.socket.bind(format)

    def connect(self, addr:str):
        format = self.format(addr)
        self.socket.connect(format)

    def disconnect(self, addr:str):
        format = self.format(addr)
        self.socket.disconnect(format)

    def recv_message(self) -> Message:
        m = Message()
        m.ParseFromString(self.socket.recv())
        return m

    def send_message(self, m:Message) -> Message:
        self.socket.send(m.SerializeToString())
        return m

    def err_message(self, m:Message, desc:str):
        e = Message(id=m.id, ts=self.timer.ts(), type=Type.ERR, mdata=Metadata(error=Error(desc=desc)))
        return self.send_message(e)

    def handshake(self, addr:str, m:Message) -> Message:
        self.connect(addr)
        self.send_message(m)
        r = self.recv_message()
        self.disconnect(addr)
        return r

    def verify(self, m:Message, r:Message, field:str=""):
        try:
            if r.type != Type.ACK:
                raise RuntimeError()

            if field:
                if r.mdata.HasField(f"{field}"):
                    if   field == "job":        return r.mdata.job
                    elif field == "command":    return r.mdata.command
                    elif field == "error":      return r.mdata.error
                    else:                       raise RuntimeError()

        except RuntimeError as e:
            print_LR(m, r, "MSG => ", "RPL =>", f=sys.stderr)
            raise e
