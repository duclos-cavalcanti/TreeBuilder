from .node      import Node
from .message   import *
from .types     import DQueue, SQueue, Pool, Tree, Logger
from .parent    import Parent
from .mcast     import Mcast

import zmq
import yaml
import logging

class Manager(Node):
    def __init__(self, plan:str, ip:str, port:str, verbosity=False):
        super().__init__(stype=zmq.REQ)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"
        self.verbosity  = verbosity

        with open(plan, 'r') as file: self.plan = yaml.safe_load(file)
        self.workers    = self.plan["addrs"][1:]
        self.root       = self.workers[0]
        self.nodes      = self.workers[1:]

        self.K          = float(self.plan["hyperparameter"])
        self.rate       = int(self.plan["rate"])
        self.dur        = int(self.plan["duration"])

        self.stepQ      = SQueue(arr=["PARENT"])
        self.pool       = Pool(self.nodes, self.K, len(self.nodes))
        self.tasks      = DQueue()
        self.tree       = Tree(name="BEST", root=self.root, fanout=2, depth=2)
        self.L          = Logger(name=f"manager:{self.addr}")

    def go(self):
        try:
            self.establish()

            while(True):
                step = self.stepQ.pop()

                if not step: 
                    self.log()
                    break

                self.L.state(f"STEP[{step}][{self.tick}]")
                match step:
                    case "PARENT":  self.parent()
                    case "MCAST":   self.mcast()
                    case "RAND":    self.rand()
                    case "REPORT":  self.report()
                    case "LOG":     self.log()
                    case _:         raise NotImplementedError()

            self.L.log("FINISHED!")

        except KeyboardInterrupt:
            self.L.log("MANUALLY CANCELLED!")

        except Exception as e:
            raise e

        finally:
            self.L.flush()
            self.socket.close()

    def establish(self):
        for addr in self.workers:
            m = self.message(src=self.addr, dst=addr, t=Type.CONNECT)
            r = self.handshake(addr, m)
            self.verify(m, r)
        self.L.log(f"CONECTION: SUCCESS")
        self.L.log(f"{[a for a in self.workers]}", level=logging.DEBUG)

    def parent(self):
        addr = self.tree.next()
        id=self.id()
        c = Command(flag=Flag.PARENT, id=id, addr=addr, layer=1, select=self.tree.fanout, rate=self.rate, dur=self.dur, data=self.pool.slice())
        m = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        job  = self.verify(m, r, field="job")

        self.tasks.push(id, Parent(c, job))
        self.stepQ.push("REPORT")

        self.L.log(f"COMMAND[{Flag.Name(c.flag)}][{addr}]: SENT")
        self.L.logm(f"SENT", m=m, level=logging.DEBUG)
        self.L.logm(f"RECV", m=r, level=logging.DEBUG)

    def mcast(self):
        data = self.tree.ids()
        addr = self.tree.root.id
        id=self.id()
        c = Command(flag=Flag.MCAST, id=id, addr=addr, layer=self.tree.d, select=1, rate=self.rate, dur=self.dur, depth=self.tree.d, fanout=self.tree.fanout, data=data)
        m = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        job = self.verify(m, r, field="job")

        self.tasks.push(id, Mcast(c, job))
        self.stepQ.push("REPORT")

        self.L.log(f"COMMAND[{Flag.Name(c.flag)}][{addr}]: SENT")
        self.L.logm(f"SENT", m=m, level=logging.DEBUG)
        self.L.logm(f"RECV", m=r, level=logging.DEBUG)

    def rand(self):
        pass

    def report(self):
        id, task = self.tasks.pop()

        job = task.copy()
        m = self.message(src=self.addr, dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
        r = self.handshake(job.addr, m)
        ret = self.verify(m, r, field="job")

        self.L.log(f"REPORT[{Flag.Name(job.flag)}][{job.addr}]: COMPLETE={ret.end}")
        self.L.logm(f"SENT", m=m, level=logging.DEBUG)
        self.L.logm(f"RECV", m=r, level=logging.DEBUG)

        if not ret.end:
            self.tasks.push(id, task)
            self.stepQ.push("REPORT")
            self.timer.sleep_sec(5)
        else:
            if ret.ret != 0: 
                raise RuntimeError()

            task.job.CopyFrom(ret)

            if ret.flag == Flag.PARENT:
                result = task.process()
                self.tree.n_add(result)
                self.pool.n_remove(result)
                self.L.record(f"PARENT[{ret.addr}]: SELECTED {[c for c in result]}")

                if self.tree.full(): 
                    self.stepQ.push("MCAST")
                    self.L.log(message=f"TREE {self.tree}", level=logging.DEBUG)
                else:                
                    self.stepQ.push("PARENT")

            if ret.flag == Flag.MCAST:
                ret = task.process()
                print(ret)

    def log(self):
        for addr in self.workers:
            m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.LOG)
            r = self.handshake(addr, m)
            self.verify(m, r)
        self.L.log(f"LOGGED: SUCCESS")
        self.L.log(f"{[a for a in self.workers]}", level=logging.DEBUG)
        self.stepQ.push(None)
