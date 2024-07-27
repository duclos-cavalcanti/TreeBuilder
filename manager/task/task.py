from ..message      import *
from ..types        import Logger, Run, StrategyDict, ResultDict

import random 
import string

from typing     import List, Tuple, Optional
from abc        import ABC, abstractmethod

class Task(ABC):
    def __init__(self, command:Optional[Command]=None):
        self.job = Job()
        if not command is None:        
            self.job.id       = command.id
            self.job.flag     = command.flag
            self.job.addr     = command.addr
            self.job.layer    = command.layer
            self.job.select   = command.select
            self.job.rate     = command.rate
            self.job.duration = command.duration
            self.job.instr    = command.instr[0]

        self.deps           = []
        self.L              = Logger()

    def generate(self, length:int=10):
        ret = ''.join(random.choice(string.ascii_letters) for _ in range(length))
        return ret

    @abstractmethod
    def build(self, run:Run) -> Command:
        pass

    @abstractmethod
    def handle(self, command:Command) -> Tuple[Job, List[Command]]:
        pass

    @abstractmethod
    def process(self) -> Job:
        pass

    @abstractmethod
    def evaluate(self, job:Job, run:Run) -> ResultDict:
        pass

    def complete(self) -> bool:
        if not self.job.end:
            return False

        for d in self.deps:
            if not d.end: 
                return False

        return True

    def err(self) -> bool:
        ret = False
        if self.job.ret != 0:
            ret = True
            self.job.ClearField('data')
            self.job.data.append(self.job.addr)

        for d in self.deps:
            if d.ret != 0: 
                if not ret: self.job.ClearField('data')
                self.job.ret = d.ret
                self.job.data.append(d.addr)
                ret = True

        return ret
