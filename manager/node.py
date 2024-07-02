from .message   import *
from .types     import Timer, Logger

import zmq

from typing import Optional

class Node():
    def __init__(self, name:str, addr:str, stype:int, map:dict):
        self.name       = name.upper()
        self.addr       = addr
        self.map        = map
        self.context    = zmq.Context()
        self.socket     = self.context.socket(stype)
        self.timer      = Timer()
        self.tick       = 1
        self.L          = Logger()
    
    def ip(self, addr:str):
        ip = addr.split(":")[0]
        return ip

    def port(self, addr:str):
        port = addr.split(":")[1]
        return port

    def format(self, addr:str):
        protocol="tcp"
        ip = self.ip(addr)
        port = self.port(addr)
        return f"{protocol}://{ip}:{port}"

    def bind(self, protocol:str="tcp", ip:str="", port:str=""):
        if not ip:      ip = self.ip(self.addr)
        if not port:    port = self.port(self.addr)
        format = f"{protocol}://{ip}:{port}"
        self.socket.bind(format)

    def connect(self, addr:str):
        format = self.format(addr)
        self.socket.connect(format)

    def disconnect(self, addr:str):
        format = self.format(addr)
        self.socket.disconnect(format)

    def message(self, dst:str, id:Optional[int]=0, t=Type.ACK, mdata:Optional[Metadata]=None) -> Message:
        ref = f"{self.map[self.addr]}/{self.map[dst]}" 
        mdata = Metadata() if mdata is None else mdata
        m = Message(id=(self.tick if id else id), ts=self.timer.ts(), ref=ref, src=self.addr, dst=dst, type=t, mdata=mdata)
        return m

    def recv_message(self) -> Message:
        m = Message()
        m.ParseFromString(self.socket.recv())
        typ         = Type.Name(m.type)
        dst         = self.ip(m.dst)
        self.L.log(f"{typ}[{dst}] RECV")
        self.L.debug(f"{self.name} RECV", data=m)
        return m

    def send_message(self, m:Message) -> Message:
        self.socket.send(m.SerializeToString())
        typ         = Type.Name(m.type)
        dst         = self.ip(m.dst)
        self.L.log(f"{typ}[{dst}] SENT")
        self.L.debug(f"{self.name} SENT", data=m)
        self.tick   += 1
        return m

    def ack_message(self, m:Message, mdata:Optional[Metadata]=None):
        r = self.message(dst=m.src, t=Type.ACK, mdata=mdata, id=m.id)
        return self.send_message(r)

    def err_message(self, m:Message, desc:str):
        e = self.message(dst=m.src, ref=m.ref, t=Type.ERR, mdata=Metadata(error=Error(desc=desc)), id=m.id)
        return self.send_message(e)

    def handshake(self, m:Message, field:str="") -> Message:
        addr = m.dst
        self.connect(addr)
        _ = self.send_message(m)
        r = self.recv_message()
        self.disconnect(addr)

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
                    if   field == "job":        return r
                    elif field == "command":    return r
                    elif field == "error":      return r
                    else:                       raise RuntimeError()

            return r

        except RuntimeError as e:
            print(f"MESSAGE: {m}")
            print(f"REPLY: {r}")
            raise e
