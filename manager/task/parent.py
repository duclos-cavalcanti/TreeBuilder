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

        total = self.command.rate * self.command.duration
        if self.command.layer == 0:
            recv  = int(self.job.data[0])
            perc  = float(self.job.data[1])
            
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            self.job.data.append(self.command.addr)
            self.job.integers.append(recv)
            self.job.floats.append(perc)
        else: 
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            for d in self.dependencies:
                self.job.data.append(d.addr)
                self.job.integers.append(d.integers[0])
                self.job.floats.append(d.floats[0])

        self.L.debug(message=f"TASK RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)
        return self.job

    def process(self, job:Job, strategy:dict={}) -> dict:
        if job.ret != 0: raise RuntimeError()

        addrs  = [a for a in job.data]
        percs  = [f for f in job.floats]
        recvs  = [i for i in job.integers]

        sorted = heapq.nsmallest(len(percs), enumerate(percs), key=lambda x: x[1])

        if strategy["best"]: items = sorted[:self.command.select]
        else:                items = [ w for w in reversed(sorted[(-1 * self.command.select):]) ]

        data = {
                "root": self.command.addr,
                "data": [{"addr": a, "perc": p, "recv": r} for a,p,r in zip(addrs, percs, recvs)], 
                "selected": []
        }
        for item in items:
            idx   = item[0]
            perc  = item[1]
            addr  = addrs[idx]
            recv  = recvs[idx]
            data["selected"].append({"addr": addr, "perc": perc, "recv": recv})


        self.L.debug(message=f"TASK PROCESS[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=data)
        return data
