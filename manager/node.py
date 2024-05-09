from .zmqsocket import ReplySocket, RequestSocket, LOG_LEVEL
from .message_pb2 import Message, MessageType, MessageFlag

import zmq
import time
import subprocess
import threading
import hashlib

from typing import Tuple, List

class Job():
    def __init__(self, addr:str="", command:str="", arr:list=[]):
        if len(arr) > 0:
            self.from_arr(arr)
        else:
            self.id         = self.hash(f"{addr}{command}")
            self.pid        = 0
            self.addr       = addr
            self.command    = command
        self.end        = False
        self.ret        = -1
        self.out        = ""

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
        print(f"}}")

    def to_arr(self) -> List:
        ret = []
        ret.append(f"{self.id}")
        ret.append(f"{self.pid}")
        ret.append(f"{self.addr}")
        ret.append(f"{self.command}")
        return ret

    def from_arr(self, arr:List):
        if len(arr) <= 3 : 
            raise RuntimeError(f"Array needed to create Job has incorrect length: {arr}")
        self.id         = arr[0]
        self.pid        = arr[1]
        self.addr       = arr[2]
        self.command    = arr[3]

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

        self.external_jobs = []
        self.jobs = {}

    def message(self, id:int, t:MessageType, f:MessageFlag, data:list):
        m = Message()
        m.id    = id
        m.ts    = int(time.time_ns() / 1_000)
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
        d = m.data
        print(f"ESTABLISHED => {addr}")
        return m, d

    def handshake_report(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.REPORT, f=MessageFlag.NONE, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.NONE)
        if not ok: 
            self.err_message(m, "REPORT ACK ERR")
        d = m.data
        print(f"REPORT <= {addr}")
        return m, d

    def handshake_parent(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.COMMAND, f=MessageFlag.PARENT, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.PARENT)
        if not ok: self.err_message(m, "PARENT ACK ERR")
        d = m.data
        print(f"MANAGER => PARENT[{addr}] => RUNNING '{d[-1]}'")
        return m, d

    def handshake_child(self, id:int, data:list, addr:str):
        self.send_message(id, MessageType.COMMAND, f=MessageFlag.CHILD, data=data)
        ok, m = self.expect_message(id, MessageType.ACK, MessageFlag.CHILD)
        if not ok: self.err_message(m, "CHILD ACK ERR")
        d = m.data
        print(f"PARENT => CHILD[{addr}] => RUNNING '{d[-1]}'")
        return m, d

    def connect(self, target:str):
        ip = target.split(":")[0]
        port = target.split(":")[1]
        self.socket.connect("tcp", ip, port)

    def disconnect(self, target:str):
        ip = target.split(":")[0]
        port = target.split(":")[1]
        self.socket.disconnect("tcp", ip, port)

    def pop_job(self):
        if len(self.external_jobs) == 0: 
            return None 
        j = self.external_jobs[0]
        self.external_jobs.pop(0)
        return j

    def push_job(self, job:Job):
        self.external_jobs.append(job)

    def exec_job(self, job:Job) -> Job:
        def run_job(j:Job):
            print(f"RUNNING[{job.addr}] => {job.command}")
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
        ret = Job()
        for t, j in list(self.jobs.items()):
            if rj.id == j.id:
                ret = j
                if not t.is_alive():
                    del self.jobs[t]
                return True, ret
        return False, ret

    def print_jobs(self, header:str="JOBS: "):
        print(f"{header}{{")
        cnt = 0
        for t, j in list(self.jobs.items()):
            j.print(header=f"RUNNING[{cnt}] = {t.is_alive()}:")
            cnt += 1

        for i,j in enumerate(self.external_jobs):
            j.print(header=f"[EXTERNAL {i}]:")

    def print_addrs(self, addrs:list, header:str):
        print(f"{header}: {{")
        for i,a in enumerate(addrs): print(f"\t{i} => {a}")
        print("}")

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



