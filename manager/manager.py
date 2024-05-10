from .node      import Node, Job
from .tree      import Tree
from .utils     import LOG_LEVEL, read_yaml

import zmq
import os
import time
import random

from typing import Callable

class Manager(Node):
    def __init__(self, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REQ, LOG_LEVEL)
        self.ip = ip 
        self.config     = read_yaml(os.path.join(os.getcwd(), "manager", "default.yaml"))
        self.workers    = self.config["addrs"][1:]
        self.pool       = self.workers
        self.rate       = int(self.config["rate"])
        self.duration   = int(self.config["duration"])
        self.K          = self.config["hyperparameter"]
        self.N          = int(len(self.workers))
        self.steps      = self.config["steps"]
        self.tree       = Tree(self.N)

    def print_node(self, n:dict, idx:int, header:str):
        print(f"{header}: {idx} => {n}")

    def step(self, action:str, desc:str) -> dict:
        d = {
            "action": action,
            "description": desc
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

    def process_step(self, s:dict, callback:Callable):
        i   = s['i']
        act = s['action']
        dsc = s['description']
        self.print(f"------>", prefix="\033[31m", suffix="\033[0m")
        self.print(f"STEP[{i}]: {act} => START    | {dsc}", prefix="\033[31m", suffix="\033[0m")
        callback()
        self.print(f"STEP[{i}]: {act} => COMPLETE | {dsc}", prefix="\033[92m", suffix="\033[0m")
        self.print(f"<------", prefix="\033[92m", suffix="\033[0m")

    def select(self):
        pool = self.pool
        size = len(pool)
        idx = random.randint(0, size - 1)
        return idx

    def establish(self, targets:list=[]):
        if not targets: targets = self.workers
        for addr in targets:
            id = self.tick
            data = [addr, self.hostaddr]
            self.connect(addr)
            self.handshake_connect(id, data, addr)
            self.disconnect(addr)

    def root(self):
        idx = self.select()
        root = self.pool[idx]
        self.pool.pop(idx)
        self.tree.set_root(root)
        self.print_node(root, idx, "CHOSEN")
        self.print_addrs(self.pool, "POOL")
        id = self.tick 
        data =  [ "2" ]
        data += [ self.rate ]
        data += [ self.duration ]
        data += self.pool
        self.connect(root)
        self.handshake_parent(id, data, root)
        self.exec_job(Job(addr=self.hostaddr, command=f"sleep {1.2 * self.duration}s"))
        self.push_step(self.step(action="REPORT", desc="Check on external Jobs"))
        self.print_jobs()
        self.disconnect(root)

    def report(self):
        ok, j, end = self.check_jobs(ref_job)
        if not ok: raise RuntimeError(f"WORKER HAS NO JOBS TO REPORT ON")
        if end: self.print_job(j, header=f"JOB DONE:")
        addr = job.addr
        self.connect(addr)
        id = self.tick 
        r, d, ts = self.handshake_report(id, job.to_arr(), addr)
        ret = Job(arr=d)
        if ret.end == False:
            print(f"REPORTED JOB [{addr}] => INCOMPLETE")
            self.jobs[ts] = job
            self.push_step(self.step(action="REPORT", desc="Check on external Jobs"))
        else:
            print(f"REPORTED JOB [{addr}] => COMPLETE")
        self.print_message(r, header="REPORTED MESSAGE: ") 
        self.disconnect(addr)

    def run(self):
        try:
            while(True):
                step = self.pop_step()
                if not step: break
                match step["action"]:
                    case "CONNECT": self.process_step(step, self.establish)
                    case "ROOT":    self.process_step(step, self.root)
                    case "REPORT":  self.process_step(step, self.report)
                    case _:         raise NotImplementedError(f"ERR STEP: {step}")
                self.tick += 1

            print("FINISHED!")
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()