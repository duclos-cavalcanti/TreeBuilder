from ..message      import *
from ..types        import Run, ItemDict, ResultDict
from .task          import Task

from typing     import List, Tuple

class Lemon(Task):
    def build(self, run:Run) -> Command:
        c = Command()
        c.flag      = Flag.LEMON
        c.id        = self.generate()
        c.layer     = 1
        c.depth     = 1
        c.fanout    = 0
        c.rate      = 100
        c.duration  = 120
        c.stress    = run.data["parameters"]["stress"]
        return c

    def handle(self, command:Command) -> Tuple[Job, List[Command]]:
        self.job.stress = command.stress
        return self.job, []

    def process(self) -> Job:
        self.L.debug(message=f"TASK PRE-RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)

        if self.err():
            return self.job

        addrs = []
        medians = []
        recvs   = []

        for i in range(0, len(self.job.data), 3):
            addrs.append(str(self.job.data[i]))
            medians.append(float(self.job.data[i + 1]))
            recvs.append(int( self.job.data[i + 2]))

        self.job.ClearField('data')
        self.job.ClearField('integers')
        self.job.ClearField('floats')
        
        self.job.data.extend(addrs)
        self.job.integers.extend(recvs)
        self.job.floats.extend(medians)

        self.L.debug(message=f"TASK RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)
        return self.job

    def evaluate(self, job:Job, run:Run) -> ResultDict:
        if job.ret != 0:  
            raise RuntimeError(f"JOB FAILURE: {job}")

        data:ResultDict = {
                "id": job.id,
                "root": job.addr,
                "key": run.data["strategy"]["key"],
                "select": job.select, 
                "rate": job.rate,
                "duration": job.duration,
                "items": [],
                "selected": []
        }

        for i in range(len(job.floats)):
            item:ItemDict = {
                    "addr":     job.data[i],
                    "p90":      0.0,
                    "p75":      0.0,
                    "p50":      job.floats[i],
                    "p25":      0.0,
                    "stddev":   0.0,
                    "mean":     0.0,
                    "recv":     job.integers[i],
            }
            data["items"].append(item)

        self.L.debug(message=f"TASK EVAL[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=data)
        return data
