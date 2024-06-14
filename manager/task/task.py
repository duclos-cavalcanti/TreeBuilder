from ..message   import *
from ..types     import Logger

import random 
import string

from abc        import ABC, abstractmethod
from typing     import TypedDict, List, Optional

class Result(TypedDict):
    selected: List[int]

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

    @abstractmethod
    def resolve(self) -> Job:
        pass

    @abstractmethod
    def process(self, job:Job, strategy:dict={}) -> dict:
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
