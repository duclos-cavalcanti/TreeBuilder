from .zmqsocket import Socket
from .message   import Message, MessageType, MessageFlag
from .ds        import Job, Timer, LOG_LEVEL

import zmq
import subprocess
import threading

from collections import OrderedDict
from typing import Callable

class Node():
    def __init__(self, name:str, ip:str, port:str, type, LOG_LEVEL=LOG_LEVEL.NONE):
        self.name       = name.upper()
        self.hostaddr   = f"{ip}:{port}"
        self.ip         = ip
        self.port       = port
        self.tick       = 0
        self.socket     = Socket(self.name, type, LOG_LEVEL=LOG_LEVEL)

        self.timer      = Timer()
        self.jobs = OrderedDict()
        self.guards = OrderedDict()

    def connect(self, addr:str):
        ip = addr.split(":")[0]
        port = addr.split(":")[1]
        self.socket.connect(protocol="tcp", ip=ip, port=port)

    def disconnect(self, addr:str):
        ip = addr.split(":")[0]
        port = addr.split(":")[1]
        self.socket.disconnect(protocol="tcp", ip=ip, port=port)

    def tag_message(self, id:int, t:MessageType, f:MessageFlag, data:list):
        m = Message()
        m.id    = id
        m.ts    = self.timer.ts()
        m.type  = t
        m.flag  = f
        if data: 
            for d in data: 
                m.data.append(str(d))
        return m

    def parse_message(self, m:Message):
        id   = m.id
        type = m.type
        flag = m.flag
        data = m.data
        return id, type, flag, data

    def recv_message(self) -> Message:
        m = Message()
        m.ParseFromString(self.socket.recv())
        return m

    def send_message(self, id:int, t:MessageType, flag:MessageFlag, data:list=[]):
        m = self.tag_message(id, t, flag, data)
        self.socket.send(m.SerializeToString())
        return m

    def ack_message(self, m:Message, data:list=[]):
        ack = self.tag_message(m.id, MessageType.ACK, m.flag, data)
        self.socket.send(ack.SerializeToString())
        return ack

    def err_message(self, m:Message, data:list=[]):
        r = self.tag_message(m.id, MessageType.ERR, m.flag, data)
        self.socket.send(r.SerializeToString())
        return r

    def print_message(self, m:Message, header:str="X"):
        lines = f"\n{m}".split("\n")
        lines = "\n\t".join(lines)
        print(f"MESSAGE[{header}]: {lines}")

    def exit_message(self, m:Message, s:str):
        self.print_message(m)
        raise RuntimeError(f"{s}")

    def handshake(self, id, type, flag, data, addr, verbose=True):
        self.send_message(id, type, flag, data=data)
        m = self.recv_message()

        if not (m.id == id and m.type == MessageType.ACK and m.flag == flag):
            self.exit_message(m, f"{MessageType.Name(type)}:{MessageFlag.Name(flag)} ACK ERR")

        if verbose: 
            print(f"{MessageType.Name(type)}[{MessageFlag.Name(flag)}] => {addr}")

        return m

    def _node(self, type, name:str="HELPER"):
        h = Node(f"{self.name}::{name}", self.ip, f"{int(self.port) + 1000}", type, self.socket.LOG_LEVEL)
        return h

    def _run(self, j:Job):
        print(f"RUNNING[{j.addr}] => {j.command}")
        try:
            p = subprocess.Popen(
                j.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            j.pid = p.pid
            stdout, stderr = p.communicate()
            j.ret = int(p.returncode)
            j.out = (stdout if stdout else stderr).split("\n")
            for i,o in enumerate(j.out):
                if o == "":
                    j.out.pop(i)

        except Exception as e:
            j.ret = -1
            j.out = [ f"ERROR: {e}" ]

        finally:
            j.end = True

        return j

    def _guard(self, job:Job, flag:MessageType):
        print(f"GUARDING[{job.id}] => DEPS={len(job.deps)}")
        n = self._node(zmq.REQ)
        while True:
            self.timer.sleep_sec(2)
            if job.is_resolved(): break
            for idx, j in enumerate(job.deps):
                if not j.complete:
                    n.connect(j.addr)
                    r = n.handshake(self.tick, MessageType.REPORT, flag, j.to_arr(), j.addr, verbose=False)
                    rjob = Job(arr=r.data)
                    job.deps[idx] = rjob
                    n.disconnect(j.addr)

        t, _ = self.find(job, dct=self.guards)
        del self.guards[t]

    def launch(self, target, args=()):
        t = threading.Thread(target=target, args=args)
        t.start()
        return t

    def exec(self, target:Callable, args=()) -> threading.Thread:
        t = self.launch(target=target, args=args)
        return t

    def find(self, rj:Job, dct={}):
        if not dct: dct = self.jobs
        for k, j in list(dct.items()):
            if rj.id == j.id:
                return k, j
        raise RuntimeError(f"{self.hostaddr} => No Job matching {rj.id}")
