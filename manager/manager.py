from .node      import Node
from .message   import *
from .ds        import Logger, SQueue, Pool, Tree
from .runner    import Runner
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
        self.root       = self.workers[0]
        self.nodes      = self.workers[1:]

        self.K          = float(self.plan["hyperparameter"])
        self.rate       = int(self.plan["rate"])
        self.dur        = int(self.plan["duration"])

        self.stepQ      = SQueue(arr=["CONNECT"])
        self.jobsQ      = SQueue()

        self.logger     = Logger(file="/volume/manager.json")
        self.runner     = Runner(root=self.root, pool=Pool(self.nodes, self.K, len(self.nodes)), runs=self.plan["runs"], logger=self.logger)

    def go(self):
        try:
            while(True):
                step = self.stepQ.pop()
                if not step: break

                print_color(f"------>", color=RED)
                print_color(f"STEP[{self.tick}]: {step} => START", color=RED, end='')
                print_color(f" [{self.runner}]", color=YLW)

                match step:
                    case "CONNECT": self.establish()
                    case "REPORT":  self.report()
                    case "PARENT":  self.parent()
                    case "MCAST":   self.mcast()
                    case "RAND":    self.rand()
                    case "ORDER":   self.order()
                    case "LOG":     self.log()
                    case _:         raise NotImplementedError()

                print_color(f"STEP[{self.tick}]: {step} => COMPLETE", color=GRN)
                print_color(f"<------", color=GRN)
                self.tick += 1

            print("FINISHED!")

        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")

        except Exception as e:
            self.log()
            raise e

        finally:
            self.socket.close()
            self.logger.dump()

    def establish(self):
        for addr in self.workers:
            m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.CONNECT)
            r = self.handshake(addr, m)
            self.verify(m, r)
        self.logger.event("ESTABLISHED", [ addr for addr in self.workers ] , verbosity=True)

        step = self.runner.run.step
        self.stepQ.push(step)

    def order(self):
        o, step = self.runner.order()
        m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.ORDER, mdata=Metadata(order=o))
        r = self.handshake(o.addr, m)
        self.verify(m, r)
        self.stepQ.push(step)

    def report(self):
        job = self.jobsQ.pop()
        if job is None: 
            raise RuntimeError()

        m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.REPORT, mdata=Metadata(job=job))
        r = self.handshake(job.addr, m)
        ret = self.verify(m, r, field="job")

        self.logger.event(f"REPORT[{Flag.Name(ret.flag)}]", f"ID={ret.id} FINISHED={ret.end}", verbosity=True)
        if not ret.end:
            self.jobsQ.push(ret)
            step = "REPORT"
        else:
            self.logger.event(f"REPORT[{Flag.Name(ret.flag)}]", MessageToDict(ret))
            step = self.runner.resolve(job=ret)

        self.stepQ.push(step)
        self.timer.sleep_sec(1)

    def parent(self):
        addr = self.runner.tree.next()
        c = Command(flag=Flag.PARENT, addr=addr, layer=0, select=self.runner.tree.fanout, rate=self.rate, dur=self.dur, data=self.runner.pool.slice(verbose=True))
        m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        self.logger.event(f"COMMAND[{Flag.Name(c.flag)}]", MessageToDict(c), verbosity=True)
        ret = self.verify(m, r, field="job")
        self.jobsQ.push(ret)

        step = "REPORT"
        self.stepQ.push(step)

    def mcast(self):
        addr = self.runner.tree.root.id
        c = Command(flag=Flag.MCAST, addr=addr, layer=0, select=1, rate=self.rate, dur=self.dur)
        m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        self.logger.event(f"COMMAND[{Flag.Name(c.flag)}]", MessageToDict(c), verbosity=True)
        ret = self.verify(m, r, field="job")
        self.jobsQ.push(ret)

        step = "REPORT"
        self.stepQ.push(step)

    def rand(self):
        pass

    def log(self):
        for addr in self.workers:
            m = Message(id=self.tick, ts=self.timer.ts(), src=self.addr, type=Type.LOG)
            r = self.handshake(addr, m)
            self.verify(m, r)

        self.logger.event("LOGGED", [ addr for addr in self.workers ] , verbosity=True)
