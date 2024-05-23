from .message   import Message, MessageType, MessageFlag
from .node      import Node
from .ds        import Pool, Tree, Job, DictionaryQueue, LOG_LEVEL
from .utils     import *

import zmq
import yaml


class Manager(Node):
    def __init__(self, config:str, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REQ, LOG_LEVEL)

        with open(config, 'r') as file:
            self.config = yaml.safe_load(file)

        self.manageraddr = self.config["addrs"][0]
        self.workers    = self.config["addrs"][1:]
        self.rate       = int(self.config["rate"])
        self.duration   = int(self.config["duration"])

        self.pool       = Pool(self.workers, float(self.config["hyperparameter"]), int(len(self.workers)))
        self.reportsQ   = DictionaryQueue()
        self.stepQ      = DictionaryQueue(dict_arr=self.config["steps"])
        self.tree       = Tree(root=self.pool.select(verbose=True), fanout=2, depth=2)

    def establish(self):
        for addr in self.workers:
            id = self.tick
            data = [addr, self.hostaddr]
            self.connect(addr)
            r = self.handshake(id, MessageType.CONNECT, MessageFlag.NONE, data, addr)
            self.disconnect(addr)

    def parent(self):
        if not self.tree.next(): raise RuntimeError()
        parent = self.tree.next()
        n_children = self.tree.fanout
        children = self.pool.slice(verbose=True)
        id = self.tick 
        data =  [ n_children, self.rate, self.duration ] + children
        self.connect(parent)
        r = self.handshake(id, MessageType.COMMAND, MessageFlag.PARENT, data, parent)
        rjob = Job(arr=r.data)
        self.disconnect(parent)
        self.reportsQ.push(self.reportsQ.make(job=rjob, ts=self.timer.future_ts(2), flag=MessageFlag.PARENT))
        self.stepQ.push(self.stepQ.make(action="REPORT", desc="Get reports on running jobs"))

    def mcast(self):
        root = self.tree.root.id
        data =  [ 0, self.rate, self.duration ]
        self.connect(root)
        r = self.handshake(self.tick, MessageType.COMMAND, MessageFlag.MCAST, data, root)
        rjob = Job(arr=r.data)
        self.disconnect(root)
        self.reportsQ.push(self.reportsQ.make(job=rjob, ts=self.timer.future_ts(2), flag=MessageFlag.MCAST))
        self.stepQ.push(self.stepQ.make(action="REPORT", desc="Get reports on running jobs"))

    def report(self):
        report = self.reportsQ.pop()
        ts  = report["ts"]
        job = report["job"]
        flag = report["flag"]
        self.timer.sleep_to(ts)
        self.connect(job.addr)
        r = self.handshake(self.tick, MessageType.REPORT, flag, job.to_arr(), job.addr)
        rjob = Job(arr=r.data)
        self.disconnect(job.addr)

        print(f"REPORT COMPLETE={rjob.complete}")
        if not rjob.complete:
            self.stepQ.push(self.stepQ.make(action="REPORT", desc="Get reports on running jobs"))
            self.reportsQ.push(self.reportsQ.make(job=rjob, ts=self.timer.future_ts(2), flag=flag))
        else:
            if job.ret != 0: raise RuntimeError()
            if flag == MessageFlag.PARENT:
                self.tree.n_add(rjob.out)
                self.pool.n_remove(rjob.out)

                if self.tree.full():
                    self.pool.show(header="REMAINING ELEMENTS")
                    self.tree.show(header="TREE COMPLETE")
                    self.stepQ.push(self.stepQ.make(action="MCAST", desc="Get multicast results from tree"))
                else:
                    self.stepQ.push(self.stepQ.make(action="PARENT", desc="Choose next node for tree."))
            elif flag == MessageFlag.MCAST:
                res = rjob.out[0]
                addr = res.split("/")[0]
                perc = res.split("/")[1]
                print(f"MCAST PERFORMANCE: LEAF[{addr}] => {perc}")
                self.tree.show()
            else:
                raise RuntimeError()

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
                    case "MCAST":   self.mcast()
                    case _:         raise NotImplementedError(f"ERR STEP: {step}")

                print_color(f"STEP[{self.tick}]: {act} => COMPLETE: {dsc}", color=GRN)
                print_color(f"<------", color=GRN)
                self.tick += 1

            print("FINISHED!")
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()
