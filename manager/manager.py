from .message   import Message, MessageType, MessageFlag
from .node      import Node
from .ds        import Job, Tree, DictionaryQueue, LOG_LEVEL
from .utils     import *

import zmq
import random
import yaml


class Manager(Node):
    def __init__(self, config:str, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REQ, LOG_LEVEL)

        with open(config, 'r') as file:
            self.config = yaml.safe_load(file)

        self.workers    = self.config["addrs"][1:]
        self.pool       = self.workers
        self.rate       = int(self.config["rate"])
        self.duration   = int(self.config["duration"])
        self.K          = self.config["hyperparameter"]
        self.N          = int(len(self.workers))

        self.reportsQ   = DictionaryQueue()
        self.stepQ      = DictionaryQueue()
        for d in self.config["steps"]: self.stepQ.push(d)

        self.tree       = Tree(root=self.select())

    def slice(self, param:int=0):
        return self.pool

    def select(self):
        pool = self.pool
        size = len(pool)
        idx = random.randint(0, size - 1)
        addr = self.pool[idx]
        self.pool.pop(idx)
        print(f"CHOSEN: {idx} => {addr}")
        print_arr(arr=self.pool, header="POOL")
        return addr

    def establish(self):
        for addr in self.workers:
            id = self.tick
            data = [addr, self.hostaddr]
            self.connect(addr)
            r = self.handshake(id, MessageType.CONNECT, MessageFlag.NONE, data, addr)
            self.disconnect(addr)

    def parent(self):
        parent, n_children = self.tree.next()
        children = self.slice()
        id = self.tick 
        data =  [ n_children, self.rate, self.duration ] + children
        self.connect(parent)
        r = self.handshake(id, MessageType.COMMAND, MessageFlag.PARENT, data, parent)
        rjob = Job(arr=r.data)
        self.disconnect(parent)
        self.reportsQ.push(self.reportsQ.make(job=rjob, ts=self.timer.future_ts(2)))
        self.stepQ.push(self.stepQ.make(action="REPORT", desc="Get reports on running jobs"))

    def report(self):
        report = self.reportsQ.pop()
        ts  = report["ts"]
        job = report["job"]
        self.timer.sleep_to(ts)
        self.connect(job.addr)
        r = self.handshake(self.tick, MessageType.REPORT, MessageFlag.MANAGER, job.to_arr(), job.addr)
        rjob = Job(arr=r.data)
        self.disconnect(job.addr)

        print(f"REPORT COMPLETE={rjob.complete}")
        if not rjob.complete:
            self.stepQ.push(self.stepQ.make(action="REPORT", desc="Get reports on running jobs"))
            self.reportsQ.push(self.reportsQ.make(job=rjob, ts=self.timer.future_ts(2)))
        else:
            for addr in rjob.out: self.tree.add(addr)
            self.stepQ.push(self.stepQ.make(action="PARENT", desc="Choose next node for tree."))
            _ = self.stepQ.pop()

    def go(self):
        try:
            while(True):
                step = self.stepQ.pop()
                if not step: break

                act = step['action']
                dsc = step['desc']
                print_color(f"------>", color=RED)
                print_color(f"STEP[{self.tick}]: {act} => START: {dsc}", color=RED)

                match act:
                    case "CONNECT": self.establish()
                    case "PARENT":  self.parent()
                    case "REPORT":  self.report()
                    case _:         raise NotImplementedError(f"ERR STEP: {step}")

                print_color(f"STEP[{self.tick}]: {act} => COMPLETE: {dsc}", color=GRN)
                print_color(f"<------", color=GRN)
                self.tick += 1

            print("FINISHED!")
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()
