from .node      import Node
from .message   import *
from .task      import Task
from .types     import Tree
from .utils     import *

from typing import List, Optional

import zmq
import heapq
import logging

class Mcast(Task):
    def make(self):
        N = Node(stype=zmq.REQ)
        if self.command.layer:
            if self.command.layer == self.command.depth: 
                self.job.instr = self.rinstr(self.command.addr, 
                                             self.command.data[1:1 + self.command.fanout], 
                                             self.command.rate, 
                                             self.command.dur)
            else:              
                self.job.instr = self.rinstr(self.command.addr, 
                                             self.command.data[1:1 + self.command.fanout], 
                                             self.command.rate, 
                                             self.command.dur)

            tree = Tree(name=f"SUBTREE:{self.command.data[0]}", 
                     root=self.command.data[0], 
                     fanout=self.command.fanout, 
                     depth=self.command.layer, 
                     arr=self.command.data[1:])

            data  = tree.slice()

            for i, a in enumerate(self.command.data[1:1 + self.command.fanout]):
                c = Command()
                c.CopyFrom(self.command)
                c.addr  = a
                c.layer = self.command.layer - 1
                c.ClearField('data')
                c.data.extend(data[i])
                m = N.message(src=f"MCAST_TASK:{self.command.addr}", dst=a, t=Type.COMMAND, mdata=Metadata(command=c))
                r = N.handshake(addr=a, m=m)
                d = N.verify(m, r, field="job")
                self.dependencies.append(d)

        else:
            self.job.instr =  self.linstr(self.command.addr, self.command.rate, self.command.dur)

        return self.copy()

    def linstr(self, addr:str, rate:int, dur:int):
        addr = format_addr(addr, diff=2000)
        ret  =  f"./bin/mcast -r {rate} -d {dur}"
        ret  += f" -i {addr.split(':')[0]} -p {addr.split(':')[1]}"
        ret  += f" -L"
        return ret

    def pinstr(self, addr:str, addrs:List, rate:int, dur:int):
        addr  = format_addr(addr, diff=2000)
        addrs = [ format_addr(a, diff=2000) for a in addrs ]
        ret   =   f"./bin/mcast -a "
        ret   +=  f" ".join(f"{a}" for a in addrs)
        ret   +=  f" -r {rate} -d {dur}"
        ret   +=  f" -i {addr.split(':')[0]} -p {addr.split(':')[1]}"
        return ret

    def rinstr(self, addr:str, addrs:List, rate:int, dur:int):
        ret =  self.pinstr(addr, addrs, rate, dur)
        ret += " -R"
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

        return self.copy()

    def process(self, job:Optional[Job]=None, strategy:dict={}) -> dict:
        if job is None:  job = self.job
        if job.ret != 0: raise RuntimeError()

        percs  = [f for f in job.floats]
        recvs  = [i for i in job.integers]
        addrs  = [a for a in job.data]

        sorted = heapq.nlargest(len(percs), enumerate(percs), key=lambda x: x[1])

        data = {
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
