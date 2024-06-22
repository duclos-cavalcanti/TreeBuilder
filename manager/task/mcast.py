from ..message      import *
from ..types        import TreeBuilder, Run, StrategyDict, ResultDict
from ..heuristic    import Heuristic
from .task          import Task

class Mcast(Task):
    def build(self, run:Run) -> Command:
        arr = run.tree.arr()
        tb  = TreeBuilder(arr=arr, depth=run.tree.d, fanout=run.tree.fanout) 
        ret = tb.mcast(rate=run.data["parameters"]["rate"], duration=run.data["parameters"]["duration"])

        c = Command()
        c.flag      = Flag.MCAST
        c.id        = self.generate()
        c.addr      = arr[0]
        c.layer     = run.tree.d
        c.depth     = run.tree.d
        c.fanout    = run.tree.fanout
        c.select    = 1
        c.rate      = run.data["parameters"]["rate"]
        c.duration  = run.data["parameters"]["duration"]
        c.instr.extend([ i for i in ret.buf ])
        c.data.extend([ a for a in arr   ])

        self.command = c
        return c

    def handle(self, command:Command):
        self.command   = command
        self.job.id    = command.id
        self.job.flag  = command.flag
        self.job.instr = command.instr[0]
        self.job.addr  = command.addr

        if command.layer:
            addrT   = TreeBuilder(arr=command.data,  depth=command.layer, fanout=command.fanout) 
            instrT  = TreeBuilder(arr=command.instr, depth=command.layer, fanout=command.fanout) 

            addrs   = command.data[1:(1+command.fanout)]
            data    = addrT.slice()
            instr   = instrT.slice()

            for addr, d, i in  zip(addrs, data, instr):
                c = Command()
                c.id     = command.id
                c.flag   = command.flag
                c.layer  = command.layer - 1
                c.fanout = command.fanout
                c.addr   = addr
                c.instr.extend(i)
                c.data.extend(d)
                self.dependencies.append(c)

        return self.job

    def resolve(self) -> Job:
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

            for d in self.dependencies:
                for daddr in d.data:     self.job.data.append(daddr)
                for drecv in d.integers: self.job.integers.append(drecv)
                for dperc in d.floats:   self.job.floats.append(dperc)

        self.L.debug(message=f"TASK RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)
        return self.job

    def process(self, job:Job, strategy:StrategyDict) -> ResultDict:
        if job.ret != 0:  
            raise RuntimeError("Failed Job")
    
        H = Heuristic(strategy, self.command, job)
        H.process(key="p90")

        self.L.debug(message=f"TASK[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=H.data)
        return H.data
