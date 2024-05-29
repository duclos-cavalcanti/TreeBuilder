from .node      import Node
from .message   import *
from .ds        import SQueue, Pool, Tree
from .utils     import *

import zmq
import yaml

class Manager(Node):
    def __init__(self, plan:str, ip:str, port:str, verbosity=False):
        super().__init__(name="MANAGER:{ip}", stype=zmq.REQ, verbosity=verbosity)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"
        self.tick       = 1

        with open(plan, 'r') as file: self.plan = yaml.safe_load(file)
        self.workers    = self.plan["addrs"][1:]
        self.rate       = int(self.plan["rate"])
        self.dur        = int(self.plan["duration"])

        self.pool       = Pool(self.workers, float(self.plan["hyperparameter"]), int(len(self.workers)))
        self.jobsQ      = SQueue()
        self.stepQ      = SQueue(arr=[s["action"] for s in self.plan["steps"]])
        self.tree       = Tree(root=self.pool.select(verbose=True), fanout=2, depth=2)

    def go(self):
        try:
            while(True):
                step = self.stepQ.pop()
                if not step: break

                print_color(f"------>", color=RED)
                print_color(f"STEP[{self.tick}]: {step} => START", color=RED)

                match step:
                    case "CONNECT": self.establish()
                    case "REPORT":  self.report()
                    case "PARENT":  self.parent()
                    case "MCAST":   self.mcast()
                    case _:         raise NotImplementedError()

                print_color(f"STEP[{self.tick}]: {step} => COMPLETE", color=GRN)
                print_color(f"<------", color=GRN)
                self.tick += 1

            print("FINISHED!")
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()

    def establish(self):
        for addr in self.workers:
            m = Message(id=self.tick, ts=self.timer.ts(), type=Type.CONNECT)
            r = self.handshake(addr, m)
            self.verify(m, r)
            print(f"ESTABLISHED => {addr}")

    def report(self):
        job = self.jobsQ.pop()
        if job is None: 
            raise RuntimeError()

        m = Message(id=self.tick, ts=self.timer.ts(), type=Type.REPORT, mdata=Metadata(job=job))
        r = self.handshake(job.addr, m)
        ret = self.verify(m, r, field="job")
        print(f"REPORT ON JOB => \n{ret}")

        if job.id != ret.id:
            raise RuntimeError("INCORRECT JOB REPORT")

        if job.err == True:
            raise RuntimeError("JOB ERR")

        if not ret.end:
            self.jobsQ.push(ret)
            self.stepQ.push("REPORT")
        else:
            if r.flag == Flag.PARENT:
                self.tree.n_add(ret.output)
                self.pool.n_remove(ret.output)
                if self.tree.full(): 
                    self.tree.show(header="TREE COMPLETE")
                    self.stepQ.push("MCAST")
                else:
                    self.stepQ.push("PARENT")

            if r.flag == Flag.MCAST:
                result = rjob.output[0]
                addr = result.split("/")[0]
                perc = result.split("/")[1]
                print(f"MCAST PERFORMANCE: LEAF[{addr}] => {perc}")

        self.timer.sleep_sec(5)

    def parent(self):
        addr = self.tree.next()
        c = Command(addr=addr, layer=0, select=self.tree.fanout, rate=self.rate, dur=self.dur, largest=False, addrs=self.pool.slice(verbose=True))
        m = Message(id=self.tick, ts=self.timer.ts(), type=Type.COMMAND, flag=Flag.PARENT, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        print(f"PARENT COMMAND => \n{c}")

        ret = self.verify(m, r, field="job")
        self.jobsQ.push(ret)
        self.stepQ.push("REPORT")

    def mcast(self):
        addr = self.tree.root.id
        c = Command(addr=addr, layer=0, select=1, rate=self.rate, dur=self.dur, largest=True)
        m = Message(id=self.tick, ts=self.timer.ts(), type=Type.COMMAND, flag=Flag.MCAST, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        print(f"MCAST COMMAND => \n{c}")

        ret = self.verify(m, r, field="job")
        self.jobsQ.push(ret)
        self.stepQ.push("REPORT")
