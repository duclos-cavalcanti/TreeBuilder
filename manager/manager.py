from .message_pb2 import Message, MessageType, MessageFlag
from .node      import Node
from .job       import Job
from .tree      import Tree
from .utils     import LOG_LEVEL
from .utils     import *

import zmq
import random
import time
import yaml


class Manager(Node):
    def __init__(self, config:str, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REQ, LOG_LEVEL)
        self.ip = ip 

        with open(config, 'r') as file:
            self.config = yaml.safe_load(file)

        self.workers    = self.config["addrs"][1:]
        self.pool       = self.workers
        self.rate       = int(self.config["rate"])
        self.duration   = int(self.config["duration"])
        self.K          = self.config["hyperparameter"]
        self.N          = int(len(self.workers))
        self.steps      = self.config["steps"]
        self.tree       = Tree(total=self.N)

    @staticmethod
    def step(action:str, desc:str) -> dict:
        d = {
            "action": action,
            "description": desc,
            "data": 0
        }
        return d

    def pop_step(self):
        if len(self.steps) == 0: return None
        s = self.steps[0]
        s["i"] = self.tick
        self.steps.pop(0)
        return s

    def push_step(self, s:dict):
        self.steps.append(s)

    def select(self):
        pool = self.pool
        size = len(pool)
        idx = random.randint(0, size - 1)
        addr = self.pool[idx]
        self.pool.pop(idx)
        print(f"CHOSEN: {idx} => {addr}")
        print_arr(arr=self.pool, header="POOL")
        return addr, self.pool

    def establish(self):
        for addr in self.workers:
            id = self.tick
            data = [addr, self.hostaddr]
            self.connect(addr)
            r = self.handshake(id, MessageType.CONNECT, MessageFlag.NONE, data, addr)
            self.disconnect(addr)

    def root(self):
        root, children = self.select()
        self.tree.set_node(root, 0)
        F = self.tree.next_layer(0)
        id = self.tick 
        data =  [ F, self.rate, self.duration ] + children
        self.connect(root)
        r = self.handshake(id, MessageType.COMMAND, MessageFlag.PARENT, data, root)
        job = Job(arr=r.data)
        self.jobs[self.future_ts(1)] = job
        self.disconnect(root)
        self.push_step(self.step(action="REPORT", desc="Check on external Jobs"))

    def report(self):
        trigger_ts, job = self.jobs.popitem()
        self.sleep_to(trigger_ts)
        self.connect(job.addr)
        r = self.handshake(self.tick, MessageType.REPORT, MessageFlag.MANAGER, job.to_arr(), job.addr)
        rjob = Job(arr=r.data)
        self.disconnect(job.addr)

        if rjob.end == False:
            print(f"REPORT <= {job.addr}: INCOMPLETE")
            self.print_message(r)
            self.push_step(self.step(action="REPORT", desc="Check on external Jobs"))
            self.jobs[self.future_ts(1)] = rjob
        else:
            print(f"REPORT <= {job.addr}: COMPLETED")
            self.print_message(r)
            # self.push_step(self.step(action="TREE", desc="Check on external Jobs"))

    def go(self):
        try:
            while(True):
                step = self.pop_step()
                if not step: break

                i   = step['i']
                act = step['action']
                dsc = step['description']
                print_color(f"------>", color=RED)
                print_color(f"STEP[{i}]: {act} => START    | {dsc}", color=RED)

                match act:
                    case "CONNECT": self.establish()
                    case "ROOT":    self.root()
                    case "REPORT":  self.report()
                    case _:         raise NotImplementedError(f"ERR STEP: {step}")

                print_color(f"STEP[{i}]: {act} => COMPLETE | {dsc}", color=GRN)
                print_color(f"<------", color=GRN)
                self.tick += 1

            print("FINISHED!")
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()
