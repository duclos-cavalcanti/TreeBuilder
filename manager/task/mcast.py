from ..message   import *
from ..types     import TreeBuilder
from .task       import Task, Plan

from typing import List, Optional

import heapq

class Mcast(Task):
    def build(self, p:Plan) -> Command:
        tb  = TreeBuilder(arr=p.arr, depth=p.depth, fanout=p.fanout) 
        ret = tb.mcast(rate=p.rate, duration=p.duration)

        c = Command()
        c.flag      = Flag.MCAST
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
                for daddr in d.data:     self.job.data.append(daddr)
                for drecv in d.integers: self.job.integers.append(drecv)
                for dperc in d.floats:   self.job.floats.append(dperc)

        self.L.debug(message=f"TASK RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)
        return self.job

    def process(self, job:Job, strategy:dict={}) -> dict:
        if job.ret != 0: raise RuntimeError()

        addrs  = [a for a in job.data]
        percs  = [f for f in job.floats]
        recvs  = [i for i in job.integers]

        sorted = heapq.nlargest(len(percs), enumerate(percs), key=lambda x: x[1])

        data = {
                "root": self.command.addr,
                "data": [{"addr": a, "perc": p, "recv": r} for a,p,r in zip(addrs, percs, recvs)], 
                "selected": []
        }

        idx  = sorted[0][0]
        perc = sorted[0][1]
        addr = addrs[idx]
        recv  = recvs[idx]
        data["selected"].append({"addr": addr, "perc": perc, "recv": recv})

        self.L.debug(message=f"TASK[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=data)
        return data
