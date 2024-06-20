from .message   import *
from .types     import Timer, Logger

import zmq

from typing import Optional

class Node():
    def __init__(self, name:str, stype:int):
        self.name       = name.upper()
        self.context    = zmq.Context()
        self.socket     = self.context.socket(stype)
        self.timer      = Timer()
        self.tick       = 1
        self.L          = Logger()

    def ip(self, addr:str):
        ip = addr.split(":")[0]
        return ip

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

    def message(self, src:str, dst:str, ref:str="", t=Type.ACK, mdata:Optional[Metadata]=None) -> Message:
        if not ref: ref = f"{self.name}:{src}"
        m = Message(id=self.tick, ts=self.timer.ts(), ref=ref, src=src, dst=dst, type=t)
        if not mdata is None: m.mdata.CopyFrom(mdata)
        return m

    def recv_message(self) -> Message:
        m = Message()
        m.ParseFromString(self.socket.recv())

        match m.type:
            case Type.CONNECT: self.L.log(f"CONNECT[{self.ip(m.src)}]: RECV")
            case Type.COMMAND: self.L.log(f"COMMAND[{Flag.Name(m.mdata.command.flag)}][{self.ip(m.mdata.command.addr)}]: RECV")
            case Type.REPORT:  self.L.log(f"REPORT[{Flag.Name(m.mdata.job.flag)}][{self.ip(m.mdata.job.addr)}] RECV")
            case Type.ACK:     pass
            case _:            self.L.log(f"{Type.Name(m.type)}[{self.ip(m.src)}] RECV")


        self.L.debug(f"{self.name} RECV", data=m)
        return m

    def send_message(self, m:Message) -> Message:
        self.socket.send(m.SerializeToString())
        self.tick += 1

        match m.type:
            case Type.CONNECT: self.L.log(f"CONNECT[{self.ip(m.dst)}]: SENT")
            case Type.COMMAND: self.L.log(f"COMMAND[{Flag.Name(m.mdata.command.flag)}][{self.ip(m.mdata.command.addr)}]: SENT")
            case Type.REPORT:  self.L.log(f"REPORT[{Flag.Name(m.mdata.job.flag)}][{self.ip(m.mdata.job.addr)}] SENT")
            case _:            self.L.log(f"{Type.Name(m.type)}[{self.ip(m.dst)}] SENT")

        self.L.debug(f"{self.name} SENT", data=m)
        return m

    def ack_message(self, m:Message, mdata:Optional[Metadata]=None):
        r = self.message(src=m.dst, dst=m.src, ref=m.ref, t=Type.ACK, mdata=mdata)
        r.id = m.id
        return self.send_message(r)

    def err_message(self, m:Message, desc:str):
        e = Message(id=m.id, ts=self.timer.ts(), type=Type.ERR, mdata=Metadata(error=Error(desc=desc)))
        return self.send_message(e)

    def handshake(self, m:Message) -> Message:
        self.connect(m.dst)
        self.send_message(m)
        r = self.recv_message()
        self.disconnect(m.dst)
        return r

    def verify(self, m:Message, r:Message, field:str=""):
        try:
            if r.id != m.id:
                raise RuntimeError()

            if r.src != m.dst:
                raise RuntimeError()

            if r.dst != m.src:
                raise RuntimeError()

            if r.type != Type.ACK:
                raise RuntimeError()

            if field:
                if r.mdata.HasField(f"{field}"):
                    if   field == "job":        return r.mdata.job
                    elif field == "command":    return r.mdata.command
                    elif field == "error":      return r.mdata.error
                    else:                       raise RuntimeError()

        except RuntimeError as e:
            print(f"MESSAGE: {m}")
            print(f"REPLY: {r}")
            raise e
