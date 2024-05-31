from .node      import Node
from .message   import *
from .ds        import Pool, Logger

from abc    import ABC, abstractmethod
from typing import List

from google.protobuf.json_format import MessageToJson, MessageToDict

import zmq
import subprocess
import threading

def fport(port:str, diff:int) -> str: 
    ret = int(port) - diff
    return f"{ret}"

def faddr(addr:str, diff:int=1000) -> str: 
    split = addr.split(":")
    ip    = split[0]
    port  = fport(split[1], diff=diff)
    return f"{ip}:{port}"

class Task(ABC):
    def __init__(self, command:Command, logger:Logger):
        self.t            = None
        self.logger       = logger
        self.dependencies = []

        self.command      = command
        self.job          = self.make()
        self.job.flag     = command.flag
        self.job.select   = command.select
        self.t            = self.launch(target=self.exec, args=())

    @abstractmethod
    def make(self) -> Job:
        pass

    @abstractmethod
    def resolve(self) -> Job:
        pass

    def complete(self):
        if not self.job.end:
            return False

        for d in self.dependencies:
            if not d.end: 
                return False

        return True

    def failed(self):
        arr = []
        if self.job.ret != 0:
            string = "\n".join(self.job.data)
            arr.append(string)

        for d in self.dependencies:
            if d.ret != 0: 
                self.job = d.ret
                string = "\n".join(d.data)
                arr.append(string)

        return (len(arr) > 0), arr

    def launch(self, target, args=()):
        t = threading.Thread(target=target, args=args)
        t.start()
        return t

    def exec(self):
        self.run(self.job)
        self.guard()

    def run(self, job:Job):
        try:
            p = subprocess.Popen(
                job.instr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = p.communicate()

            data = [ s for s in (stdout if stdout else stderr).split("\n") if s ]
            job.pid = p.pid
            job.ret = int(p.returncode)

        except Exception as e:
            data = [ f"ERROR: {e}" ]
            job.ret = -1

        finally:
            job.ClearField('data')
            job.data.extend(data)
            job.end = True

        return job

    def guard(self):
        if not self.dependencies: 
            return

        N = Node(name="GUARD", stype=zmq.REQ)
        while True:
            N.timer.sleep_sec(2)

            if self.complete(): 
                break

            for i, job in enumerate(self.dependencies):
                if job.end: continue 
                m = Message(id=0, ts=N.timer.ts(), src=f"GUARD:{self.command.addr}", type=Type.REPORT, mdata=Metadata(job=job))
                r = N.handshake(job.addr, m)
                ret = N.verify(m, r, field="job")
                if ret.end: self.dependencies[i].CopyFrom(ret)


class Mcast(Task):
    def make(self):
        if len(self.command.data) == 0:
            addr = faddr(self.command.addr, diff=2000)
            instr =  f"./bin/mcast -r {self.command.rate} -d {self.command.dur} -L"
            instr += f" -i {addr.split(':')[0]} -p {addr.split(':')[1]}"
            id = f"{self.command.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=self.command.addr, instr=instr)
        else:
            N = Node(name=f"MCAST", stype=zmq.REQ)
            addr = faddr(self.command.addr, diff=2000)
            faddrs = [ faddr(a, diff=2000) for a in self.command.data ]
            instr =  f"./bin/mcast -a " + " ".join(f"{a}" for a in faddrs) + f" -r {self.command.rate} -d {self.command.dur}"
            instr += f" -i {addr.split(':')[0]} -p {addr.split(':')[1]}"
            instr += " -R" if self.command.layer == 0 else ""
            id = f"{self.command.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=self.command.addr, instr=instr)
            for a in self.command.data:
                c = Command(flag=Flag.MCAST, addr=a, layer=(self.command.layer + 1), select=self.command.select, rate=self.command.rate, dur=self.command.dur)
                m = Message(id=1, ts=N.timer.ts(), src=f"MCAST:{self.command.addr}", type=Type.COMMAND, mdata=Metadata(command=c))
                r = N.handshake(addr=a, m=m)
                d = N.verify(m, r, field="job")
                self.dependencies.append(d)

        self.job = job
        return self.job

    def resolve(self) -> Job:
        failed, arr = self.failed() 
        if failed:
            self.job.ClearField('data')
            self.job.data.extend(arr)
            return self.job

        if len(self.command.data) == 0:
            total = self.command.rate * self.command.dur
            recv = int(self.job.data[0])
            perc = float(self.job.data[1])
            
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            self.job.data.append(self.command.addr)
            self.job.integers.append(recv)
            self.job.floats.append(perc)
            self.logger.record(f"MCAST LEAF[{self.command.addr}] JOB", data={ "total": total, "recv": recv, "perc": perc}, verbosity=False)
        else:
            total = self.command.rate * self.command.dur
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            data = {"total": total, "N": len(self.dependencies), "data": []}
            for d in self.dependencies:
                for daddr in d.data:     self.job.data.append(daddr)
                for drecv in d.integers: self.job.integers.append(drecv)
                for dperc in d.floats:   self.job.floats.append(dperc)
                data["data"].append({ "addrs": [ d for d in d.data ], "perc":  [ p for p in d.floats ], "recv":  [ r for r in d.integers ]})
            self.logger.record(f"MCAST PROXY{self.command.layer}[{self.command.addr}] JOB", data=data)

        return self.job

class Parent(Task):
    def make(self):
        if self.command.layer:
            faddrs = faddr(self.command.addr)
            instr = f"./bin/child -i {faddrs.split(':')[0]} -p {faddrs.split(':')[1]} -d {self.command.dur}"
            id = f"{self.command.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=self.command.addr, instr=instr)

        else:
            N = Node(name=f"PARENT", stype=zmq.REQ)
            faddrs = [ faddr(a) for a in self.command.data ]
            instr =  "./bin/parent -a " + " ".join(f"{a}" for a in faddrs) + f" -r {self.command.rate} -d {self.command.dur}"
            id = f"{self.command.addr}:{instr.split()[0]}"
            job = Job(id=id, addr=self.command.addr, instr=instr)
            for a in self.command.data:
                c = Command(flag=Flag.PARENT, addr=a, layer=(self.command.layer + 1), select=self.command.select, rate=self.command.rate, dur=self.command.dur)
                m = Message(id=1, ts=N.timer.ts(), src=f"PARENT:{self.command.addr}", type=Type.COMMAND, mdata=Metadata(command=c))
                r = N.handshake(addr=a, m=m)
                d = N.verify(m, r, field="job")
                self.dependencies.append(d)

        self.job = job
        return self.job

    def resolve(self) -> Job:
        failed, arr = self.failed() 
        if failed:
            self.job.ClearField('data')
            self.job.data.extend(arr)
            return self.job

        if self.command.layer:
            total = self.command.rate * self.command.dur
            recv = int(self.job.data[0])
            perc = float(self.job.data[1])
            
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            self.job.integers.append(recv)
            self.job.floats.append(perc)
            self.logger.record(f"CHILD[{self.command.addr}] JOB", data={ "total": total, "recv": recv, "perc": perc})
            return self.job

        else: 
            total = self.command.rate * self.command.dur
            self.job.ClearField('data')
            self.job.ClearField('integers')
            self.job.ClearField('floats')

            data = {"total": total, "N": len(self.dependencies), "data": []}
            for d in self.dependencies:
                self.job.data.append(d.addr)
                self.job.integers.append(d.integers[0])
                self.job.floats.append(d.floats[0])
                data["data"].append({"addr": d.addr, "perc": d.floats[0], "recv": d.integers[0]})

            self.logger.record(f"PARENT[{self.command.addr}] JOB", data=data)
            return self.job

class Scheduler():
    def __init__(self, addr:str, logger:Logger):
        self.addr       = addr
        self.logger     = logger
        self.jobs       = {}

        self.map = {
            Flag.PARENT: Parent,
            Flag.MCAST:  Mcast,
        }

    def add(self, command:Command):
        constructor = self.map.get(command.flag)
        if constructor is None:
            raise NotImplementedError()

        I = constructor(command, self.logger)
        self.jobs[I.job.id] = I
        self.logger.record(f"COMMAND[{command.addr}] {Flag.Name(command.flag)}", data=f"RUNNING: {I.job.instr}", verbosity=True)

        return I.job

    def report(self, job:Job):
        I = self.jobs.get(job.id)
        if I is None: 
            raise RuntimeError(f"JOB: {job.id} NOT FOUND IN SCHEDULER[{self.addr}]")

        # if job and it's dependencies haven't finished
        if not I.complete():
            return job

        ret  = I.resolve()

        del I.t
        del I
        del self.jobs[job.id]

        return ret
