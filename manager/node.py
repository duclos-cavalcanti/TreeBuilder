from .message   import Message, MessageHandler
from .message   import Job, JobHandler
from .ds        import Timer

import zmq
import subprocess
import threading

from enum import Enum
from collections import OrderedDict
from typing import Callable

class LOG_LEVEL(Enum):
    NONE = 1 
    DEBUG = 2 
    ERROR = 3

class Node():
    def __init__(self, name:str, ip:str, port:str, stype:int, verbosity=LOG_LEVEL.NONE):
        self.name       = name.upper()
        self.hostaddr   = f"{ip}:{port}"
        self.ip         = ip
        self.port       = port
        self.tick       = 0

        self.verbosity  = verbosity

        self.context    = zmq.Context()
        self.socket     = self.context.socket(stype)
        self.guard      = self.context.socket(zmq.REQ)

        self.timer      = Timer()
        self.jobs       = OrderedDict()
        self.guards     = OrderedDict()

    def log(self, string:str):
        if (self.verbosity == LOG_LEVEL.NONE): 
            return 
        print(f"LOG::{self.name}: {string}")

    def format(self, addr:str):
        protocol="tcp"
        ip = addr.split(":")[0]
        port = addr.split(":")[1]
        return f"{protocol}://{ip}:{port}"

    def bind(self):
        protocol="tcp"
        ip = self.ip
        port = self.port
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

    def send_message(self, m:Message):
        self.socket.send(m.SerializeToString())
        return

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
        while True:
            self.timer.sleep_sec(2)
            if job.is_resolved(): break
            for idx, j in enumerate(job.deps):
                if not j.complete:
                    self.guard.connect(self.format(j.addr))

                    try:
                        # (self.tick, MessageType.REPORT, flag, j.to_arr(), j.addr, verbose=False)
                        self.send_message(Message(), self.guard)
                        r = self.recv_message(self.guard)
                        rjob = Job(arr=r.data)
                        job.deps[idx] = rjob

                    except RuntimeError as _:
                        self.guard.disconnect(self.format(j.addr))

                    else:
                        self.guard.disconnect(self.format(j.addr))

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
