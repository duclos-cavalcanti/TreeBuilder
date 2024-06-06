from .node      import Node
from .message   import *
from .types     import Pool, Tree, Logger
from .parent    import Parent
from .mcast     import Mcast

from queue      import Queue, SimpleQueue
from typing     import List

import zmq

class Manager(Node):
    class Run():
        def __init__(self, run:dict, params:dict, root:str, nodes:List):
            self.name       = run["name"]
            self.strategy   = run["strategy"]
            self.K          = params["hyperparameter"]
            self.rate       = params["rate"]
            self.dur        = params["duration"]
            self.pool       = Pool([n for n in nodes], self.K, len(nodes))
            self.tree       = Tree(name=self.name, root=root, fanout=params["fanout"], depth=params["depth"])

    def __init__(self, plan:dict, ip:str, port:str, verbosity=False):
        super().__init__(stype=zmq.REQ)
        self.ip         = ip
        self.port       = port
        self.addr       = f"{ip}:{port}"
        self.verbosity  = verbosity

        self.plan       = plan
        self.workers    = self.plan["addrs"][1:]
        self.runQ       = SimpleQueue()
        self.tasks      = SimpleQueue()
        self.L          = Logger(name=f"manager:{self.addr}")

        for run in plan["runs"]: 
            self.runQ.put(self.Run(run, plan["params"], self.workers[0], self.workers[1:]))

    def go(self):
        try:
            self.establish()
            self.L.record(f"CONNECTED[{len(self.workers)}]")

            while(not self.runQ.empty()):
                self.run = self.runQ.get_nowait()
                self.L.record(f"RUN[{self.run.name}]")

                while(not self.run.tree.full()):
                    if self.run.name == "RAND": 
                        data = self.rand()
                    else:
                        self.parent()
                        data = self.report()

                    root  = data["root"]
                    addrs = [ d["addr"] for d in data["selected"] ]
                    self.run.tree.n_add(addrs)
                    self.run.pool.n_remove(addrs)
                    self.L.record(f"TREE[{self.run.tree.name}] SELECTION[{self.run.tree.n}/{self.run.tree.max}]: PARENT[{root}] => CHILDREN {[c for c in addrs]}")
                    self.L.debug(message=f"{self.run.tree}")

                self.mcast()
                data = self.report()
                self.L.record(f"TREE[{self.run.tree.name}] PERFORMANCE[{data['selected'][0]['addr']}]: {data['selected'][0]['perc']}")
                self.L.stats(message=f"{self.run.tree}")

            self.L.log("FINISHED!")

        except Exception as e:
            self.L.log("INTERRUPTED!")
            raise e

        finally:
            self.L.flush()
            self.socket.close()

    def establish(self):
        for addr in self.workers:
            m = self.message(src=self.addr, dst=addr, t=Type.CONNECT)
            r = self.handshake(addr, m)
            self.verify(m, r)

    def parent(self) -> Command:
        addr = self.run.tree.next()
        c = Command(flag=Flag.PARENT, id=self.id(), addr=addr, layer=1, select=self.run.tree.fanout, rate=self.run.rate, dur=self.run.dur, data=self.run.pool.slice())
        m = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        job  = self.verify(m, r, field="job")
        self.tasks.put(Parent(c, job))
        return c

    def mcast(self) -> Command:
        data = self.run.tree.ids()
        addr = data[0]
        c = Command(flag=Flag.MCAST, id=self.id(), addr=addr, layer=self.run.tree.d, select=1, rate=self.run.rate, dur=self.run.dur, depth=self.run.tree.d, fanout=self.run.tree.fanout, data=data)
        m = self.message(src=self.addr, dst=addr, t=Type.COMMAND, mdata=Metadata(command=c))
        r = self.handshake(addr, m)
        job = self.verify(m, r, field="job")
        self.tasks.put(Mcast(c, job))
        return c

    def rand(self) -> dict:
        data = { "root": self.run.tree.next(), "selected": [] }
        for _ in range(self.run.tree.fanout): 
            addr = self.run.pool.select()
            data["selected"].append({"addr": addr})
            self.run.pool.pool.append(addr)
        return data

    def report(self, dur:int=5) -> dict:
        task = self.tasks.get_nowait()
        while True:
            job = task.copy()
            m = self.message(src=self.addr, dst=job.addr, t=Type.REPORT, mdata=Metadata(job=job))
            r = self.handshake(job.addr, m)
            rjob = self.verify(m, r, field="job")
            if rjob.end: return task.process(rjob, self.run.strategy)
            else:        self.timer.sleep_sec(dur)
