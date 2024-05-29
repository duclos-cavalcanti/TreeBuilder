from .node      import Node
from .message   import *
from .ds        import Logger, SQueue, Pool, Tree
from .utils     import *

from google.protobuf.json_format import MessageToJson, MessageToDict

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
        self.pool       = Pool(self.workers, float(self.plan["hyperparameter"]), int(len(self.workers)))
        self.root       = self.pool.select(verbose=True)
        self.nodes      = [p for p in self.pool.pool]

        self.rate       = int(self.plan["rate"])
        self.dur        = int(self.plan["duration"])
        
        self.jobsQ      = SQueue()

        self.runQ       = SQueue(arr=[r for r in self.plan["runs"]])
        self.run        = self.runQ.pop()

        self.stepQ      = SQueue(arr=["CONNECT", self.run['type']])
        self.tree       = Tree(name=self.run["name"], root=self.root, fanout=2, depth=2)

        self.logger     = Logger(file="/volume/LOG.JSON")

    def go(self):
        self.logger.write(key="pool", data=self.pool.to_dict())
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

        finally:
            self.socket.close()
            self.logger.dump()

    def establish(self):
        for addr in self.workers:
            m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.CONNECT)
            r = self.handshake(addr, m)
            self.verify(m, r)
        self.logger.event("ESTABLISHED", [ addr for addr in self.workers ] , verbosity=True)

    def report(self):
        job = self.jobsQ.pop()
        if job is None: 
            raise RuntimeError()

        m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.REPORT, mdata=Metadata(job=job))
        r = self.handshake(job.addr, m)
        ret = self.verify(m, r, field="job")
        print(f"REPORT ON JOB => \n{ret}")

        if job.id != ret.id:
            raise RuntimeError("INCORRECT JOB REPORT")

        if job.err is True:
            raise RuntimeError("JOB ERR")

        if not ret.end:
            self.jobsQ.push(ret)
            self.stepQ.push("REPORT")
        else:
            self.logger.event(f"REPORT[{Flag.Name(r.flag)}]", MessageToDict(ret), verbosity=True)

            if r.flag == Flag.PARENT:
                self.tree.n_add(ret.output)
                self.pool.n_remove(ret.output)
                self.logger.event(f"PARENT[{ret.addr}]", [ f"{child}" for child in ret.output], verbosity=True)

                if self.tree.full(): 
                    self.logger.event("TREE COMPLETE", f"{self.tree.name}", verbosity=True)
                    self.logger.tree(key=self.tree.name, data=self.tree.to_dict())
                    self.stepQ.push("MCAST")
                else:                
                    self.stepQ.push("PARENT")

            if r.flag == Flag.MCAST:
                addr = ret.output[0].split("/")[0]
                perc = ret.output[0].split("/")[1]
                data = {
                    "leaf": addr,
                    "perc": perc
                }
                self.logger.event(f"MCAST PERFORMANCE[{self.tree.name}]", f"{addr}:{perc}", verbosity=True)
                self.logger.record(f"TREE[{self.tree.name}]", data=data)
                self.run = self.runQ.pop()

                if not self.run is None: 
                    self.tree = Tree(name=self.run["name"], root=self.root, fanout=2, depth=2)
                    self.pool.reset(self.nodes)
                    self.stepQ.push(self.run['type'])
                    self.logger.event(f"NEW RUN", self.run, verbosity=True)

        self.timer.sleep_sec(5)

    def parent(self):
        addr = self.tree.next()
        c = Command(addr=addr, layer=0, select=self.tree.fanout, rate=self.rate, dur=self.dur, largest=self.run['largest'], addrs=self.pool.slice(verbose=True))
        m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.COMMAND, flag=Flag.PARENT, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        self.logger.event(f"COMMAND[{Flag.Name(m.flag)}]", MessageToDict(c), verbosity=True)

        ret = self.verify(m, r, field="job")
        self.jobsQ.push(ret)
        self.stepQ.push("REPORT")

    def mcast(self):
        addr = self.tree.root.id
        c = Command(addr=addr, layer=0, select=1, rate=self.rate, dur=self.dur, largest=True)
        m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.COMMAND, flag=Flag.MCAST, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        self.logger.event(f"COMMAND[{Flag.Name(m.flag)}]", MessageToDict(c), verbosity=True)

        ret = self.verify(m, r, field="job")
        self.jobsQ.push(ret)
        self.stepQ.push("REPORT")

    def rand(self):
        raise NotImplementedError()
