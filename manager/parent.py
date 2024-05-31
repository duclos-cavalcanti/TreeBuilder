from .node      import Node
from .message   import *
from .task      import Task
from .utils     import *

from typing import List

import zmq
import heapq
import logging

class Parent(Task):
    def make(self):
        N = Node(stype=zmq.REQ)
        if self.command.layer:
            self.job.instr = self.pinstr(self.command.data, self.command.rate, self.command.dur)
            for a in self.command.data:
                c = Command() 
                c.CopyFrom(self.command)
                c.addr = a
                c.layer = self.command.layer - 1
                c.ClearField('data')
                m = N.message(src=f"TASK[{Flag.Name(c.flag)}:{self.command.addr}]", dst=a, t=Type.COMMAND, mdata=Metadata(command=c))
                r = N.handshake(addr=a, m=m)
                d = N.verify(m, r, field="job")
                self.L.log(message=f"TASK[{Flag.Name(c.flag)}:{self.command.addr}] RECEIVED DEPENDENCY", level=logging.DEBUG)
                self.dependencies.append(d)
        else:
            self.job.instr = self.cinstr(self.command.addr, self.command.rate, self.command.dur)

        return self.copy()

    def cinstr(self, addr:str, rate:int, dur:int):
        addr = format_addr(addr)
        ret =  f"./bin/child -i {addr.split(':')[0]} -p {addr.split(':')[1]}"
        ret += f" -r {rate} -d {dur}"
        return ret

    def pinstr(self, addrs:List, rate:int, dur:int):
        addrs = [ format_addr(a) for a in addrs ]
        ret   =  f"./bin/parent -a "
        ret   += f" ".join(f"{a}" for a in addrs)
        ret   += f" -r {rate} -d {dur}"
        return ret

    def summarize(self) -> Job:
        if self.failed():
            return self.job

        total = self.command.rate * self.command.dur
        if self.command.layer == 0:
            recv  = int(self.job.data[0])
            perc  = float(self.job.data[1])
            
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

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

        return self.copy()

    def process(self, best:bool=True) -> List:
        addrs  = [a for a in self.job.data]
        percs  = [f for f in self.job.floats]
        recvs  = [i for i in self.job.integers]

        sorted = heapq.nsmallest(len(percs), enumerate(percs), key=lambda x: x[1])

        if best: items = sorted[:self.command.select]
        else:    items = [ w for w in reversed(sorted[(-1 * self.command.select):]) ]

        data = {
                "data": [{"addr": a, "perc": p, "recv": r} for a,p,r in zip(addrs, percs, recvs)], 
                "selected": []
        }
        ret  = []

        for item in items:
            idx   = item[0]
            perc  = item[1]
            addr  = addrs[idx]
            recv  = recvs[idx]
            data["selected"].append({"addr": addr, "perc": perc, "recv": recv})
            ret.append(addr)


        self.L.logd(message=f"PARENT JOB[{self.job.id}:{self.job.addr}] RESULT", d=data, level=logging.DEBUG)
        return ret
