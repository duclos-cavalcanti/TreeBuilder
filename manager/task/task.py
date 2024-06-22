from ..message      import *
from ..types        import Logger, Run, StrategyDict, ResultDict

import random 
import string
import subprocess

from abc        import ABC, abstractmethod

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
    def build(self, run:Run) -> Command:
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
    def process(self, job:Job, strategy:StrategyDict) -> ResultDict:
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
