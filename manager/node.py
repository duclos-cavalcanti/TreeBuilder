from .zmqsocket import Socket
from .message_pb2 import Message, MessageType, MessageFlag
from .job import Job, Report
from .utils import LOG_LEVEL

import zmq
import time
import subprocess
import threading

from typing import Callable

class Node():
    def __init__(self, name:str, ip:str, port:str, type, LOG_LEVEL=LOG_LEVEL.NONE):
        self.name       = name.upper()
        self.hostaddr   = f"{ip}:{port}"
        self.ip         = ip
        self.port       = port
        self.tick       = 0
        self.socket = Socket(self.name, type, LOG_LEVEL=LOG_LEVEL)

        self.jobs = {}
        self.reports = []

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
        m.ts    = self.timestamp()
        m.type  = t
        m.flag  = f
        if data: 
            for d in data: 
                m.data.append(str(d))
        return m

    def recv_message(self) -> Message:
        m = Message()
        m.ParseFromString(self.socket.recv())
        return m

    def send_message(self, id:int, t:MessageType, flag:MessageFlag, data:list=[]):
        m = self.tag_message(id, t, flag, data)
        self.socket.send(m.SerializeToString())

    def err_message(self, m:Message, s:str):
        self.print_message(m, header="ERR MESSAGE: ")
        raise RuntimeError(f"{s}")

    def handshake(self, id, type, flag, data, addr):
        self.send_message(id, type, flag, data=data)
        m = self.recv_message()
        if not (m.id == id and m.type == MessageType.ACK and m.flag == flag):
            self.err_message(m, f"{MessageType.Name(type)}:{MessageFlag.Name(flag)} ACK ERR")
        print(f"{MessageType.Name(type)}[{MessageFlag.Name(flag)}] => {addr}")
        return m

    def _helper(self, type, name:str="HELPER"):
        h = Node(f"{self.name}::{name}", self.ip, f"{int(self.port) + 1000}", type, self.socket.LOG_LEVEL)
        return h

    def _launch(self, target, args=()):
        t = threading.Thread(target=target, args=args)
        t.start()
        return t

    def _run(self, j:Job):
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
            j.out = f"ERROR: {e}"
        finally:
            j.end = True
        return j

    def _alarm(self, j:Job, addr:str, rid:str):
        ret = self._run(j)
        n = self._helper(zmq.REQ)
        n.connect(addr)
        data = [ rid ] + ret.to_arr()
        n.send_message(id=self.tick, 
                          t=MessageType.REPORT, 
                          flag=MessageFlag.NONE, 
                          data=data)
        n.recv_message()
        t, _ = self.find(ret)
        del self.jobs[t]
        n.disconnect(addr)

    def exec(self, job:Job, target:Callable, args=()) -> Job:
        print(f"RUNNING[{job.addr}] => {job.command}")
        t = self._launch(target=target, args=args)
        self.jobs[t] = job
        return job

    def find(self, rj:Job):
        for k, j in list(self.jobs.items()):
            if rj.id == j.id:
                return k, j
        raise RuntimeError(f"{self.hostaddr} => does not have job matching {rj.id}")

    def pop_report(self):
        if len(self.reports) == 0:
            raise RuntimeError(f"{self.hostaddr} does not have pending reports")

        arr = self.reports[0]
        rid = arr[0]
        r = arr[1]
        self.reports.pop(0)
        return rid, r

    def push_report(self, rid:str, r:Report):
        self.reports.append([rid, r])

    def find_report(self, rid:str, job:Job):
        if len(self.reports) == 0:
            raise RuntimeError(f"{self.hostaddr} does not have pending reports")
        for idx, arr in enumerate(self.reports):
            _rid = arr[0]
            report = arr[1]
            if rid == _rid and job.id == report.job.id:
                return idx, report
        raise RuntimeError(f"{self.hostaddr} does not have matching reports to {rid}")

    def sleep_to(self, trigger_ts:int): 
        future = trigger_ts
        now = self.timestamp()
        if future > now: 
            self.sleep(future - now)
        else:
            print(f"TRIGGER EXPIRED={future} < NOW={now}")

    def sleep(self, dur_us:int): 
        print(f"SLEEPING UNTIL {self.timestamp() + dur_us}")
        time.sleep(self.usec_to_sec(dur_us))
        print(f"AWAKE: {self.timestamp()}")

    def sec_to_usec(self, sec:int) -> int:
        return (sec * 1_000_000)
    
    def usec_to_sec(self, usec:int) -> int:
        return int(usec / 1_000_000)
    
    def timestamp(self) -> int: 
        return int(time.time_ns() / 1_000)

    @staticmethod
    def parse_message(m:Message):
        id   = m.id
        type = m.type
        flag = m.flag
        data = m.data
        return id, type, flag, data

    @staticmethod
    def print_message( m:Message, header:str=""):
        print(f"{header}{{")
        print(f"    ID: {m.id}")
        print(f"    TS: {m.ts}")
        print(f"    TYPE: {MessageType.Name(m.type)}")
        print(f"    FLAG: {MessageFlag.Name(m.flag)}")
        print(f"    DATA: [")
        for d in m.data: print(f"         {d}")
        print(f"    ]\n}}")
