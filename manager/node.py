from .zmqsocket import ReplySocket, RequestSocket
from .message_pb2 import Message, MessageType, MessageFlag
from .utils import LOG_LEVEL

import zmq
import time
import subprocess
import threading
import hashlib

from typing import Tuple, List

class Job():
    def __init__(self, addr:str="", command:str="", m:Message=Message()):
        arr = m.data
        if len(arr) > 0:
            self.from_arr(arr)
        else:
            self.id         = self.hash(f"{addr}{command}")
            self.pid        = 0
            self.addr       = addr
            self.command    = command
            self.end        = False
            self.ret        = -1
            self.out        = "NONE"
        self.deps       = []

    def hash(self, string:str) -> str: 
        bytes = string.encode('utf-8')
        hash = hashlib.sha256(bytes)
        return hash.hexdigest()

    def print(self, header:str):
        print(f"{header}{{")
        print(f"\tID={self.id}")
        print(f"\tPID={self.pid}")
        print(f"\tADDR={self.addr}")
        print(f"\tCOMM={self.command}")
        print(f"\tEND={self.end}")
        print(f"\tRET={self.ret}")
        print(f"\tOUT={self.out}")
        if len(self.deps) > 0:
            print("DEPS: [")
            for d in self.deps:
                print(f"{{")
                print(f"\tID={d.id}")
                print(f"\tADDR={d.addr}")
                print(f"}}")
            print("]")
        print(f"}}")

    def to_arr(self) -> List:
        ret = []
        ret.append(f"{self.id}")
        ret.append(f"{self.pid}")
        ret.append(f"{self.addr}")
        ret.append(f"{self.command}")
        ret.append(f"{self.end}")
        ret.append(f"{self.ret}")
        ret.append(f"{self.out}")
        return ret

    def from_arr(self, arr:List):
        if len(arr) <= 6 : 
            raise RuntimeError(f"Array needed to create Job has incorrect length: {arr}")
        self.id         = arr[0]
        self.pid        = arr[1]
        self.addr       = arr[2]
        self.command    = arr[3]
        self.end        = True if arr[4] == "True" else False
        self.ret        = arr[5]
        self.out        = arr[6]

class Node():
    def __init__(self, name:str, ip:str, port:str, type, LOG_LEVEL=LOG_LEVEL.NONE):
        self.name       = name.upper()
        self.hostaddr   = f"{ip}:{port}"
        self.ip         = ip
        self.port       = port
        self.tick       = 0
        self.LOG_LEVEL  = LOG_LEVEL

        if type   == zmq.REP:   self.socket = ReplySocket(self.name, protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)
        elif type == zmq.REQ:   self.socket = RequestSocket(self.name, protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)
        else:                   raise NotImplementedError(f"ZMQSOCKET TYPE: {type}")

        self.jobs     = {}

    def timestamp(self) -> int: 
        return int(time.time_ns() / 1_000)

    def message(self, id:int, t:MessageType, f:MessageFlag, data:list):
        m = Message()
        m.id    = id
        m.ts    = self.timestamp()
        m.type  = t
        m.flag  = f
        if data: 
            for d in data: 
                m.data.append(str(d))
        return m

    def send_message(self, id:int, t:MessageType, f:MessageFlag=MessageFlag.NONE, data:list=[]):
        m = self.message(id, t, f, data)
        self.socket.send(m.SerializeToString())

    def send_message_ack(self, m:Message, data:list=[]):
        r = self.message(m.id, MessageType.ACK, m.flag, data)
        self.socket.send(r.SerializeToString())

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
        return m

    def handshake_report(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.REPORT, f=MessageFlag.NONE, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.NONE)
        if not ok: self.err_message(m, "REPORT ACK ERR")
        print(f"REPORT <= {addr}")
        return m

    def handshake_parent(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.COMMAND, f=MessageFlag.PARENT, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.PARENT)
        if not ok: self.err_message(m, "PARENT ACK ERR")
        print(f"MANAGER => PARENT[{addr}] => RUNNING PROCESS")
        return m

    def handshake_child(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.COMMAND, f=MessageFlag.CHILD, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.CHILD)
        if not ok: self.err_message(m, "CHILD ACK ERR")
        print(f"PARENT => CHILD[{addr}] => RUNNING PROCESS")
        return m

    def connect(self, target:str):
        ip = target.split(":")[0]
        port = target.split(":")[1]
        self.socket.connect("tcp", ip, port)

    def disconnect(self, target:str):
        ip = target.split(":")[0]
        port = target.split(":")[1]
        self.socket.disconnect("tcp", ip, port)

    def exec_job(self, job:Job) -> Job:
        def run_job(j:Job):
            print(f"RUNNING[{j.addr}] => {j.command}")
            try:
                p = subprocess.Popen(
                    j.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                j.pid = p.pid
                stdout, stderr = p.communicate()
                j.ret = p.returncode
                j.out = stdout if stdout else stderr
            except Exception as e:
                j.ret = -1
                j.out = f"Error occurred: {e}"
            finally:
                j.end = True

        t = threading.Thread(target=run_job, args=(job,))
        t.start()
        self.jobs[t] = job
        return job

    def check_jobs(self, rj:Job):
        ret = rj
        for t, j in list(self.jobs.items()):
            if rj.id == j.id:
                if not t.is_alive():
                    ret = j
                    del self.jobs[t]
                    return True, ret, True
                return True, ret, False
        return False, ret, False

    def print_jobs(self, header:str="JOBS: "):
        print(f"{header}{{")
        cnt = 0
        for t, j in list(self.jobs.items()):
            j.print(header=f"JOB[{cnt}]: ALIVE={t.is_alive()} => ")
            cnt += 1
        print(f"}}")

    def print_addrs(self, addrs:list, header:str):
        print(f"{header}: {{")
        for i,a in enumerate(addrs): print(f"\t{i} => {a}")
        print("}")

    def print_job(self, j:Job, header:str=""):
        j.print(header=header)

    def print_message(self, m:Message, header:str=""):
        print(f"{header}{{")
        print(f"    ID: {m.id}")
        print(f"    TS: {m.ts}")
        print(f"    TYPE: {MessageType.Name(m.type)}")
        print(f"    FLAG: {MessageFlag.Name(m.flag)}")
        print(f"    DATA: [")
        for d in m.data: print(f"         {d}")
        print(f"    ]\n}}")

    def print(self, text:str, prefix:str="", suffix:str=""):
        print(f"{prefix}{text}{suffix}")

    def err_message(self, m:Message, s:str):
        self.print_message(m, header="ERR MESSAGE: ")
        raise RuntimeError(f"{s}")



