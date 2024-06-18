from ..message import *
from ..task    import Task, Plan, Result
from ..types   import Tree, TreeBuilder

from typing import List, Optional

import heapq

class Parent(Task):
    def build(self, p:Plan) -> Command:
        tb  = TreeBuilder(arr=p.arr, depth=p.depth, fanout=p.fanout) 
        ret = tb.parent(rate=p.rate, duration=p.duration)

        c = Command()
        c.flag      = Flag.PARENT
        c.id        = self.generate()
        c.addr      = p.arr[0]
        c.layer     = p.depth
        c.depth     = p.depth
        c.fanout    = p.fanout
        c.select    = p.select
        c.rate      = p.rate
        c.duration  = p.duration
        c.instr.extend([ i for i in ret.buf ])
        c.data.extend([ a for a in p.arr   ])

        self.command = c
        return c

    def handle(self, command:Command):
        self.command   = command
        self.job.id    = command.id
        self.job.flag  = command.flag
        self.job.instr = command.instr[0]
        self.job.addr  = command.addr

        addrs = command.data[1:]
        instr = command.instr[1:]

        if command.layer:
            for addr,i in zip(addrs, instr):
                c = Command()
                c.id    = command.id
                c.flag  = command.flag
                c.layer = command.layer - 1
                c.addr  = addr
                c.instr.append(i)
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
                self.job.data.append(d.addr)
                self.job.integers.append(d.integers[0])
                for f in d.floats: self.job.floats.append(f)

        self.L.debug(message=f"TASK RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)
        return self.job

    def process(self, job:Job, strategy:dict) -> Result:
        if job.ret != 0:  
            raise RuntimeError("Failed Job")
    
        key    = strategy["key"]
        best   = strategy["best"]
        ret    = Result(key)
        items  = ret.parse(job)

        if key not in items[0]: 
            raise RuntimeError(f"Incorrect key:{key}")

        sorted = heapq.nsmallest(len(items), items, key=lambda x: x[key])
        if best: selected = [ s["addr"] for s in sorted[:self.command.select] ]
        else:    selected = [ s["addr"] for s in [ w for w in reversed(sorted[(-1 * self.command.select):]) ] ]

        ret.selected(selected)
        ret.parameters(self.command)
        ret.arrange(sorted)

        self.L.debug(message=f"TASK PROCESS[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=ret.data)
        return ret
