from .node      import Node
from .message   import *

from abc    import ABC, abstractmethod
from typing import List

import zmq
import subprocess
import threading
import hashlib
import heapq

def fport(port:str, diff:int) -> str: 
    ret = int(port) - diff
    return f"{ret}"

def faddr(addr:str, diff:int=1000) -> str: 
    split = addr.split(":")
    ip    = split[0]
    port  = fport(split[1], diff=diff)
    return f"{ip}:{port}"

class Handler(ABC):
    def __init__(self, command:Command, shbuffer:List):
        self.command      = command
        self.dependencies = []
        self.shbuffer     = shbuffer

    @abstractmethod
    def make(self):
        pass

    @abstractmethod
    def resolve(self) -> Job:
        pass

    def finished(self):
        for d in self.dependencies:
            if not d.end: 
                return False
        return True

class Mcast(Handler):
    def __init__(self, command:Command, shbuffer:List):
        super().__init__(command, shbuffer)

    def make(self):
        N = Node(name="TASK", stype=zmq.REQ)
        c = self.command
        children = self.shbuffer

        if not children:
            addr = faddr(c.addr)
            instr =  f"./bin/mcast -r {c.rate} -d {c.dur} -L"
            instr += f" -i {addr.split(':')[0]} -p {addr.split(':')[1]}"
            id = f"{c.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=c.addr, instr=instr)
        else:
            addr = faddr(c.addr)
            faddrs = [ faddr(a) for a in children ]
            instr =  f"./bin/mcast -a " + " ".join(f"{a}" for a in faddrs) + f" -r {c.rate} -d {c.dur}"
            instr += f" -i {addr.split(':')[0]} -p {addr.split(':')[1]}"
            instr += " -R" if c.layer == 0 else ""
            id = f"{c.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=c.addr, instr=instr)
            for a in children:
                c = Command(addr=a, layer=(c.layer + 1), select=c.select, rate=c.rate, dur=c.dur)
                m = Message(id=1, ts=N.timer.ts(), type=Type.COMMAND, flag=Flag.MCAST, mdata=Metadata(command=c))
                r = N.handshake(addr=a, m=m)
                d = N.verify(m, r, field="job")
                self.dependencies.append(d)

        self.job = job
        return job.id

    def resolve(self) -> Job:
        c = self.command
        job = self.job
        children = self.shbuffer

        if job.ret != 0:
            job.err = True
            return job

        for d in self.dependencies: 
            if d.ret != 0:
                job.err = True 
                return job
            print(f"ADDR[{d.addr}] => RES={d.output[0]}")

        if not children:
            addr = job.addr
            total = c.rate * c.dur
            recv = int(job.output[0])
            perc = float(job.output[1])

            job.ClearField('output')
            job.output.append(f"{addr}/{perc}")
            print(f"MCAST[{addr}] LEAF => PERC={perc} | RECV={recv}/{total}")
        else:
            percs    = [float(d.output[0].split("/")[1]) for d in self.dependencies]
            sorted   = heapq.nlargest(1, enumerate(percs), key=lambda x: x[1])
            idx = sorted[0][0]
            perc = sorted[0][1]
            addr = self.dependencies[idx].output[0].split("/")[0]
            job.ClearField('output')
            job.output.append(f"{addr}/{perc}")
            print(f"MCAST WORST LEAF OF {c.addr}: => {addr}: PERC={perc}")

        return job

class Parent(Handler):
    def __init__(self, command:Command, shbuffer:List):
        super().__init__(command, shbuffer)

    def make(self):
        N = Node(name="TASK", stype=zmq.REQ)
        c = self.command
        if c.layer == 0:
            faddrs = [ faddr(a) for a in c.addrs ]
            instr =  "./bin/parent -a " + " ".join(f"{a}" for a in faddrs) + f" -r {c.rate} -d {c.dur}"
            id = f"{c.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=c.addr, instr=instr)
            for a in c.addrs:
                c = Command(addr=a, layer=(c.layer + 1), select=c.select, rate=c.rate, dur=c.dur)
                m = Message(id=1, ts=N.timer.ts(), type=Type.COMMAND, flag=Flag.PARENT, mdata=Metadata(command=c))
                r = N.handshake(addr=a, m=m)
                d = N.verify(m, r, field="job")
                self.dependencies.append(d)

        else:
            faddrs = faddr(c.addr)
            instr = f"./bin/child -i {faddrs.split(':')[0]} -p {faddrs.split(':')[1]} -d {c.dur}"
            id = f"{c.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=c.addr, instr=instr)

        self.job = job
        return job.id

    def resolve(self) -> Job:
        c = self.command
        job = self.job

        if job.ret != 0:
            job.err = True
            return job

        for d in self.dependencies: 
            if d.ret != 0:
                job.err = True 
                return job
            print(f"ADDR[{d.addr}] => PERC={d.output[0]}")

        if c.layer:
            total = c.rate * c.dur
            recv = int(job.output[0])
            perc = float(job.output[1])
            
            job.ClearField('output')
            job.output.append(f"{perc}")
            
            print(f"CHILD[{job.addr}] => PERC={perc} | RECV={recv}/{total}")
            return job

        else: 
            percs = [float(d.output[0]) for d in self.dependencies]
            sorted = heapq.nsmallest(len(percs), enumerate(percs), key=lambda x: x[1])

            if c.largest: items = [ w for w in reversed(sorted[(-1 * c.select):]) ]
            else:         items = sorted[:c.select]

            res = []
            for item in items:
                idx   = item[0]
                perc  = item[1]
                addr = self.dependencies[idx].addr
                res.append(addr)

            job.ClearField('output')
            job.output.extend(res)

            self.shbuffer.clear()
            self.shbuffer.extend(res)

            print(f"PARENT[{job.addr}] CHOSE: {[a for a in job.output]}")
            return job

class Scheduler():
    def __init__(self, buffer:List):
        self.shbuffer   = buffer
        self.lock       = threading.Lock()
        self.threads    = {}
        self.jobs       = {}
        self.G  = self.launch(self.guard)

        self.map = {
            Flag.PARENT: Parent,
            Flag.MCAST:  Mcast,
            Parent: Flag.PARENT,
            Mcast:  Flag.MCAST,
        }


    def add(self, command:Command, flag:Flag):
        constructor = self.map.get(flag)
        if constructor is None:
            raise NotImplementedError()

        I = constructor(command, self.shbuffer)
        I.make()
        self.jobs[I.job.id]    = I
        self.threads[I.job.id] = self.launch(target=self.run, args=(I.job,))

        print(f"RUNNING[{I.job.addr}] => {I.job.instr}")
        return I.job

    def get(self, k, d:dict):
        ret = d.get(k)
        if ret is None:
            raise RuntimeError(f"KEY: {k} NOT FOUND IN {d}")
        else: 
            return ret

    def report(self, job:Job):
        T   = self.get(job.id,  self.threads)
        I   = self.get(job.id,  self.jobs)
        F   = self.get(type(I), self.map)

        # if thread is still running
        if T.is_alive():
            return job, F

        # if job Implementation has resolved dependencies
        if not I.finished():
            return job, F
        
        ret = I.resolve()
        with self.lock:
            del self.threads[job.id]
            del self.jobs[job.id]

        return ret, F

    def launch(self, target, args=()):
        t = threading.Thread(target=target, args=args)
        t.start()
        return t

    def run(self, job:Job):
        try:
            p = subprocess.Popen(
                job.instr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = p.communicate()
            output = [ s for s in (stdout if stdout else stderr).split("\n") if s ]

            job.pid = p.pid
            job.ret = int(p.returncode)

        except Exception as e:
            output = [ f"ERROR: {e}" ]
            job.ret = -1

        finally:
            job.ClearField('output')
            job.output.extend(output)
            job.end = True

        return job

    def guard(self):
        N = Node(name="SCHEDULER", stype=zmq.REQ)
        cnt = 0
        while True:
            N.timer.sleep_sec(5)
            if not self.jobs: 
                continue

            with self.lock:
                for _, I in self.jobs.items():
                    dependencies = I.dependencies
                    if not dependencies: 
                        continue

                    for i, job in enumerate(dependencies):
                        if job.end: continue 
                        m = Message(id=cnt, ts=N.timer.ts(), type=Type.REPORT, mdata=Metadata(job=job))
                        r = N.handshake(job.addr, m)
                        ret = N.verify(m, r, field="job")
                        if ret.end: 
                            dependencies[i].CopyFrom(ret)
            cnt += 1

