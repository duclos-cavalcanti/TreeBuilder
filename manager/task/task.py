from ..message      import *
from ..types        import Logger, Run, ResultDict

import random 
import string

from typing     import List, Tuple
from abc        import ABC, abstractmethod

class Task(ABC):
    def __init__(self):
        self.command        = Command()
        self.job            = Job()
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
            self.job.ClearField['data']
            self.job.data.append(self.job.addr)

        for d in self.deps:
            if d.ret != 0: 
                if not ret: self.job.ClearField['data']
                self.job.data.append(d.addr)
                ret = True

        return ret
