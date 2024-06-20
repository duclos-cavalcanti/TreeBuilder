from os import walk
from ..message   import *
from ..types     import Logger

import random 
import string
import subprocess

from abc        import ABC, abstractmethod
from typing     import TypedDict, List, Optional

class Element(TypedDict):
    addr: str 
    p90: float 
    p75: float 
    p50: float 
    p25: float 
    stddev: float 
    recv: int

class Parameters(TypedDict):
    select: int 
    rate: int
    duration: int
    packets: int

class Data(TypedDict):
    root: str
    key:  str
    data: List[Element]
    parameters: Parameters
    selected: List[str]

class Result():
    def __init__(self, key:str=""):
        self.data: Data = {
                "root": "",
                "key": key,
                "data": [],
                "parameters": {
                    "select": 0, 
                    "rate": 0,
                    "duration": 0,
                    "packets": 0,
                },
                "selected": []
        }

    def parse(self, job:Job) -> List[Element]:
        items = []
        self.data["root"] = job.addr
        for j,i in enumerate(range(0, len(job.floats), 5)):
            addr    = job.data[j]
            p90     = job.floats[i]
            p75     = job.floats[i + 1]
            p50     = job.floats[i + 2]
            p25     = job.floats[i + 3]
            stddev  = job.floats[i + 4]
            recv    = job.integers[j]
            items.append(self.element(addr, p90, p75, p50, p25, stddev, recv))

        self.data["data"].extend([ i.copy() for i in items ])
        return items

    def parameters(self, command:Command):
        ret:Parameters = {
                "select":   command.select, 
                "rate":     command.rate, 
                "duration": command.duration, 
                "packets":  command.duration * command.rate
        }
        self.data["parameters"] = ret

    def selected(self, arr:List[str]):
        for a in arr: self.data["selected"].append(a)

    def arrange(self, arr:List[Element]):
        for i,a in enumerate(arr):
            self.data["data"][i] = a

    def element(self, addr:str, 
                      p90:float=0.0, 
                      p75:float=0.0, 
                      p50:float=0.0, 
                      p25:float=0.0, 
                      stddev:float=0.0, 
                      recv:int=0):
        item:Element = {
                "addr": addr, 
                "p90": p90,
                "p75": p75,
                "p50": p50,
                "p25": p25,
                "stddev": stddev,
                "recv": recv
        }
        return item


class Plan():
    def __init__(self, rate:int, duration:int, fanout:int, depth:int, select:int, arr:List):
        self.rate       = rate
        self.duration   = duration
        self.fanout     = fanout
        self.depth      = depth
        self.select     = select
        self.arr        = [ a for a in arr ]

class Task(ABC):
    def __init__(self):
        self.command        = Command()
        self.job            = Job()
        self.dependencies   = []
        self.L              = Logger()

    def generate(self, length:int=10):
        ret = ''.join(random.choice(string.ascii_letters) for _ in range(length))
        return ret

    @abstractmethod
    def build(self, p:Plan) -> Command:
        pass

    @abstractmethod
    def handle(self, command:Command) -> Job:
        pass

    def run(self):
        try:
            p = subprocess.Popen(
                self.job.instr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = p.communicate()
            output = (stdout if stdout else stderr)

            data = [ s for s in output.split("\n") if s ]
            self.job.pid = p.pid
            self.job.ret = int(p.returncode)

        except Exception as e:
            data = [ f"ERROR: {e}" ]
            self.job.ret = -1

        finally:
            self.job.ClearField('data')
            self.job.data.extend(data)
            self.job.end = True

    @abstractmethod
    def resolve(self) -> Job:
        pass

    @abstractmethod
    def process(self, job:Job, strategy:dict) -> Result:
        pass

    def complete(self) -> bool:
        if not self.job.end:
            return False

        for d in self.dependencies:
            if not d.end: 
                return False

        return True

    def err(self) -> bool:
        ret = False
        if self.job.ret != 0:
            ret = True
            self.job.ClearField['data']
            self.job.data.append(self.job.addr)

        for d in self.dependencies:
            if d.ret != 0: 
                if not ret: self.job.ClearField['data']
                self.job.data.append(d.addr)
                ret = True

        return ret
