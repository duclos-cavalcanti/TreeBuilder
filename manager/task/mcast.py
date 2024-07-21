from ..message      import *
from ..types        import TreeBuilder, Run, ItemDict, ResultDict
from .task          import Task

import heapq

from typing     import List, Tuple

class Mcast(Task):
    def build(self, run:Run) -> Command:
        id  = self.generate()
        arr = run.tree.arr()
        tb  = TreeBuilder(arr=arr, depth=run.tree.d, fanout=run.tree.fanout) 
        ret = tb.mcast(rate=run.data["parameters"]["rate"], duration=run.data["parameters"]["duration"], id=id)

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

    def handle(self, command:Command) -> Tuple[Job, List[Command]]:
        commands    = []  
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
            mean  = float(self.job.data[6])
            
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            self.job.data.append(self.job.addr)
            self.job.integers.append(recv)
            self.job.floats.extend([p90, p75, p50, p25, dev, mean])
        else:
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            for d in self.deps:
                for daddr in d.data:     self.job.data.append(daddr)
                for drecv in d.integers: self.job.integers.append(drecv)
                for dperc in d.floats:   self.job.floats.append(dperc)

        self.L.debug(message=f"TASK RESOLVE[{Flag.Name(self.job.flag)}][{self.job.id}:{self.job.addr}]", data=self.job)
        return self.job

    def evaluate(self, job:Job, run:Run) -> ResultDict:
        if job.ret != 0:  
            raise RuntimeError("Failed Job")

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

        for j,i in enumerate(range(0, len(job.floats), 6)):
            item: ItemDict = {
                    "addr":     job.data[j],
                    "p90":      job.floats[i],
                    "p75":      job.floats[i + 1],
                    "p50":      job.floats[i + 2],
                    "p25":      job.floats[i + 3],
                    "stddev":   job.floats[i + 4],
                    "mean":     job.floats[i + 5],
                    "recv":     job.integers[j],
            }
            data["items"].append(item)

        sorted = heapq.nlargest(len(data["items"]),  data["items"], key=lambda x, k="p90": x[k])
        data["selected"] = [ s["addr"] for s in sorted[:1] ]

        for i in range(len(data["items"])):
            data["items"][i] = sorted[i]

        self.L.debug(message=f"TASK EVAL[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=data)
        return data
