from .message   import Message, MessageType, MessageMetadata, MessageHandler
from .message   import Command, Report, Job, JobHandler
from .node      import Node, LOG_LEVEL
from .ds        import SQueue, Pool, Tree
from .utils     import *

import zmq
import yaml


class Manager(Node):
    def __init__(self, plan:str, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REQ, LOG_LEVEL)

        with open(plan, 'r') as file:
            self.plan = yaml.safe_load(file)

        self.workers    = self.plan["addrs"][1:]
        self.rate       = int(self.plan["rate"])
        self.dur        = int(self.plan["duration"])

        self.pool       = Pool(self.workers, float(self.plan["hyperparameter"]), int(len(self.workers)))
        self.reportsQ   = SQueue()
        self.stepQ      = SQueue(arr=self.plan["steps"])
        self.tree       = Tree(root=self.pool.select(verbose=True), fanout=2, depth=2)

    def establish(self):
        for addr in self.workers:
            h = MessageHandler()
            h.fconnect(id=self.tick, dst=addr, src=self.hostaddr)
            self.connect(addr)
            self.send_message(h.message())
            r = self.recv_message()
            h.inspect(r)
            self.disconnect(addr)

    def parent(self):
        parent = self.tree.next()
        c = Command()
        c.flag = Command.CommandFlag.PARENT
        c.layer = 0
        c.select = self.tree.fanout
        c.data = self.rate 
        c.dur = self.dur
        c.addrs.extend([ c for c in self.pool.slice(verbose=True)])
        h = MessageHandler()
        h.fcommand(id=self.tick, dst=parent, src=self.hostaddr, command=c, flag=MessageType.PARENT)
        self.connect(parent)
        self.send_message(h.message())
        r = self.recv_message()
        self.disconnect(parent)
        report = h.inspect(r, field="report")
        report.ts = self.timer.future_ts(2)
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
