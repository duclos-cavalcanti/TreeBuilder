from ..message      import *
from ..types        import TreeBuilder, Run, ItemDict, ResultDict
from ..heuristic    import Heuristic
from .task          import Task

from typing     import List, Tuple

class Parent(Task):
    def build(self, run:Run, port:int=8080) -> Command:
        id      = self.generate()
        addr    = run.tree.next()
        arr     = [addr] + run.pool.slice()
        tb      = TreeBuilder(arr=arr, depth=1, fanout=len(arr[1:])) 
        ret     = tb.parent(rate=run.data["parameters"]["rate"], duration=run.data["parameters"]["duration"], id=id, port=port)

        c = Command()
        c.flag      = Flag.PARENT
        c.id        = id
        c.addr      = arr[0]
        c.layer     = 1
        c.depth     = 1
        c.fanout    = len(arr[1:])
        c.select    = run.tree.fanout
        c.rate      = run.data["parameters"]["rate"]
        c.duration  = run.data["parameters"]["duration"]
        c.instr.extend([ i for i in ret.buf ])
        c.data.extend([ a for a in arr   ])

        self.command = c
        return c

    def handle(self, command:Command) -> Tuple[Job, List[Command]]:
        commands    = []  
        if command.layer:
            for addr,i in zip(command.data[1:], command.instr[1:]):
                c = Command()
                c.id    = command.id
                c.flag  = command.flag
                c.layer = command.layer - 1
                c.addr  = addr
                c.instr.append(i)
                commands.append(c)

        return self.job, commands

    def process(self) -> Job:
        self.L.debug(message=f"TASK PRE-RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)

        if self.err():
            return self.job

        if self.job.layer == 0:
            recv  = int(self.job.data[0])
            p90   = float(self.job.data[1])
            p75   = float(self.job.data[2])
            p50   = float(self.job.data[3])
            p25   = float(self.job.data[4])
            dev   = float(self.job.data[5])
            
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            self.job.data.append(self.job.addr)
            self.job.integers.append(recv)
            self.job.floats.extend([p90, p75, p50, p25, dev])
        else: 
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            for d in self.deps:
                self.job.data.append(d.addr)
                self.job.integers.append(d.integers[0])
                for f in d.floats: self.job.floats.append(f)

        self.L.debug(message=f"TASK RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)
        return self.job

    def evaluate(self, job:Job, run:Run) -> ResultDict:
        if job.ret != 0:  
            raise RuntimeError("Failed Job")

        data:ResultDict = {
                "root": job.addr,
                "key": run.data["strategy"]["key"],
                "select": job.select, 
                "rate": job.rate,
                "duration": job.duration,
                "items": [],
                "selected": []
        }

        for j,i in enumerate(range(0, len(job.floats), 5)):
            item: ItemDict = {
                    "addr":     job.data[j],
                    "p90":      job.floats[i],
                    "p75":      job.floats[i + 1],
                    "p50":      job.floats[i + 2],
                    "p25":      job.floats[i + 3],
                    "stddev":   job.floats[i + 4],
                    "recv":     job.integers[j],
            }
            data["items"].append(item)

        H = Heuristic(data, run.data["strategy"])
        H.process()

        self.L.debug(message=f"TASK EVAL[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=H.data)
        return H.data
