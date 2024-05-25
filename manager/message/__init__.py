from .message_pb2 import Message, MessageType, MessageFlag
from .message_pb2 import Command, Report, Job, Error

import hashlib
import time
import sys

from typing import List

MessageType     = Message.MessageType
MessageMetadata = Message.MessageMetadata

class MessageHandler():
    def __init__(self, m:Message=Message()):
        self.m = m

    def message(self):
        return self.m

    def tag(self):
        self.m.ts = int(time.time_ns() / 1_000)
        return self.m

    def format(self, id:int, dst:str, src:str):
        self.m = Message()
        self.tag()
        self.m.id = id
        self.m.metadata.src = src
        self.m.metadata.dst = dst

        return m

    def fconnect(self, id:int, dst:str, src:str):
        self.m = self.format(id, dst, src)
        self.m.type = MessageType.CONNECT
        return self.m

    def fcommand(self, id:int, dst:str, src:str, command:Command):
        self.m = self.format(id, dst, src)
        self.m.type = MessageType.COMMAND
        self.m.mdata.command = command
        return self.m

    def inspect(self, r:Message, field:str=""):
        m = self.m

        mtype = self.m.type
        rtype = r.type

        try:
            if rtype != MessageType.ACK:
                raise RuntimeError()

            if m.mdata.src != r.mdata.dst or m.data.dst != r.data.src: 
                raise RuntimeError()

            if mtype == MessageType.ERR:
                raise RuntimeError()

            if field:
                if r.mdata.HasMsgField(f"{field}"):
                    if   field == "report":     return r.mdata.report
                    elif field == "command":    return r.mdata.command
                    elif field == "error":      return r.mdata.error
                    else:                       raise RuntimeError()

        except RuntimeError as e:
            print(r, file=sys.stderr)
            raise e

    def show(self, header:str=""):
        s = self.__str__()
        if header: s = f"{header}\n{s}"
        return s

    def __str__(self):
        s = self.m.__str__()
        s = f"\n{s}".split("\n")
        s = "\n\t".join(s)
        return s


class JobHandler():
    def __init__(self, job:Job):
        self.job = job

    def __str__(self):
        return super().__str__()

    def hash(self, string:str) -> str: 
        bytes = string.encode('utf-8')
        hash = hashlib.sha256(bytes)
        return hash.hexdigest()

    def is_resolved(self) -> bool: 
        deps = self.job.deps
        for d in deps:
            if d.end == False: 
                return False
        return True

    def concatenate(self) -> List: 
        arr = []
        deps = self.job.deps
        for d in deps:
            for o in d.out:
                arr.append(str(o))
        return arr
