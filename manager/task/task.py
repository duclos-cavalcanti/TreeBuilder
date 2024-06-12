from ..message   import *
from ..types     import Logger

from abc        import ABC, abstractmethod
from typing     import TypedDict, List, Optional

class TaskResult(TypedDict):
    selected: List[int]

class Task(ABC):
    def __init__(self, command:Command, job:Optional[Job]=None):
        self.command      = command
        self.dependencies = []

        if job is None: self.job = Job(id=command.id, flag=command.flag, addr=command.addr)
        else:           self.job = job

        self.L = Logger()

    def copy(self) -> Job:
        ret = Job()
        ret.CopyFrom(self.job)
        return ret

    @abstractmethod
    def make(self) -> Job:
        pass

    @abstractmethod
    def resolve(self) -> Job:
        pass

    @abstractmethod
    def process(self, job:Optional[Job]=None, strategy:dict={}) -> dict:
        pass

    def complete(self) -> bool:
        if not self.job.end:
            return False

        for d in self.dependencies:
            if not d.end: 
                return False

        return True

    def failed(self) -> bool:
        arr = []
        if self.job.ret != 0:
            string = "\n".join(self.job.data)
            arr.append(string)

        for d in self.dependencies:
            if d.ret != 0: 
                self.job = d.ret
                string = "\n".join(d.data)
                arr.append(string)

        failed = (len(arr) > 0)
        if failed:
            self.job.ClearField('data')
            self.job.data.extend(arr)

        return failed
