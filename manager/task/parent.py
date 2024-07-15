from ..message      import *
from ..types        import TreeBuilder, Run, StrategyDict, ResultDict
from ..heuristic    import Heuristic
from .task          import Task

from typing     import List, Tuple

class Parent(Task):
    def build(self, run:Run) -> Command:
        id      = self.generate()
        addr    = run.tree.next()
        arr     = [addr] + run.pool.slice()
        tb      = TreeBuilder(arr=arr, depth=1, fanout=len(arr[1:])) 
        ret     = tb.parent(rate=run.data["parameters"]["rate"], 
                            duration=run.data["parameters"]["duration"], 
                            id=id)

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
        self.command   = command
        self.job.id    = command.id
        self.job.flag  = command.flag
        self.job.instr = command.instr[0]
        self.job.addr  = command.addr

        addrs       = command.data[1:]
        instr       = command.instr[1:]
        commands    = []  

        if command.layer:
            for addr,i in zip(addrs, instr):
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

        if self.command.layer == 0:
            recv  = int(self.job.data[0])
            p90   = float(self.job.data[1])
            p75   = float(self.job.data[2])
            p50   = float(self.job.data[3])
            p25   = float(self.job.data[4])
            dev   = float(self.job.data[5])
            
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            self.job.data.append(self.command.addr)
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

        H = Heuristic(run.data["strategy"], self.command, job)
        H.process()

        self.L.debug(message=f"TASK EVAL[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=H.data)
        return H.data
