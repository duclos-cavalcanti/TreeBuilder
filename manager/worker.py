from .message   import Message, MessageType, MessageFlag
from .node      import Node
from .ds        import Job, LOG_LEVEL
from .utils     import *

import heapq
import zmq

class Worker(Node):
    def __init__(self, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REP, LOG_LEVEL)
        self.best   = []
        self.worst  = []

    def child_job(self):
        C = f"./bin/child -i {self.ip} -p {int(self.port) - 1000}"
        J = Job(addr=self.hostaddr, command=C)
        self.jobs[self.exec(target=self._run, args=(J,))] = J
        return J

    def parent_job(self, sel:int, rate:int, dur:int, addrs:list):
        faddrs = []
        for a in addrs:
            split = a.split(":")
            ip    = split[0]
            port  = split[1]
            port  = str(int(port) - 1000)
            faddrs.append(f"{ip}:{port}")

        C = "./bin/parent -a " + " ".join(f"{a}" for a in faddrs) + f" -r {rate} -d {dur}"
        J = Job(addr=self.hostaddr, command=C, params=[sel, rate, dur])
        H = self._node(zmq.REQ)

        for addr in addrs:
            id = self.tick
            data = [addr, self.hostaddr]
            H.connect(addr)
            r = H.handshake(id, MessageType.COMMAND, MessageFlag.CHILD, data, addr)
            rjob = Job(arr=r.data)
            J.deps.append(rjob)
            H.disconnect(addr)

        self.jobs[self.exec(target=self._run, args=(J,))] = J
        self.guards[self.exec(target=self._guard, args=(J,))] = J

        return J

    def parent_resolve(self, job:Job):
        print("PARENT RESOLVE:")
        sel   = int(job.params[0])
        rate  = int(job.params[1])
        dur   = int(job.params[2])
        total = rate * dur

        if job.ret != 0:
            print(f"ERR: PARENT[{job.addr}]: RET={job.ret}")
            return job

        for dep in job.deps:
            if dep.ret != 0:
                print(f"ERR: ADDR[{dep.addr}]: RET={dep.ret}")
                job.ret = dep.ret
                return job

        percs = []
        for _, dep in enumerate(job.deps):
            print(f"ADDR[{dep.addr}]: PERC={float(dep.out[1])} | RECV={int(dep.out[0])}")
            percs.append(float(dep.out[1]))
 

        sorted   = heapq.nsmallest(len(job.deps), enumerate(percs), key=lambda x: x[1])
        n_best   = sorted[:sel]
        n_worst  = [ w for w in reversed(sorted[(-1 * sel):]) ]

        out = []
        for i, (best, worst) in enumerate(zip(n_best, n_worst)):
            best_i = best[0]
            best_v = best[1]
            worst_i = worst[0]
            worst_v = worst[1]

            b_addr = job.deps[best_i].addr
            w_addr = job.deps[worst_i].addr
            print(f"BEST[{i}]: {b_addr}/{best_v} | WRST[{i}]: {w_addr}/{worst_v}")

            self.best.append(b_addr)
            self.worst.append(w_addr)
            out.append(b_addr)

        job.out = out
        return job

    def commandACK(self, m:Message):
        id, _, flag, data = self.parse_message(m)
        match flag:
            case MessageFlag.PARENT: 
                if len(data) <= 3: 
                    self.err_message(m, "PARENT COMMAND ERR")
                sel   = int(data[0])
                rate  = int(data[1])
                dur   = int(data[2])
                addrs = data[3:]
                job = self.parent_job(sel, rate, dur, addrs)
                r = self.send_message(id=id, t=MessageType.ACK, flag=flag, data=job.to_arr())
                return r

            case MessageFlag.CHILD:  
                if len(data) < 2 or self.hostaddr != data[0]: 
                    self.err_message(m, "CHILD COMMAND ERR")
                job = self.child_job()
                r = self.send_message(id=id, t=MessageType.ACK, flag=flag, data=job.to_arr())
                return r

            case _:
                raise NotImplementedError(f"COMMAND FLAG: {MessageFlag.Name(flag)}")

    def reportACK(self, m:Message):
        id, _, flag, data = self.parse_message(m)
        t, job = self.find(Job(arr=data))
        job.complete = (job.end and job.is_resolved())
        if job.complete: 
            del self.jobs[t]

        if job.complete and flag == MessageFlag.MANAGER:
            job = self.parent_resolve(job)

        print(f"JOB[{job.id}] => END={job.end}")
        r = self.send_message(id=id, t=MessageType.ACK, flag=flag, data=job.to_arr())
        return r

    def connectACK(self, m:Message):
        id, _, flag, data = self.parse_message(m)
        if self.hostaddr != data[0]: 
            self.err_message(m, "CONNECT ERR")
        r = self.send_message(id=id, t=MessageType.ACK, flag=flag, data=[self.hostaddr])
        return r

    def go(self):
        self.socket.bind(protocol="tcp", ip=self.ip, port=self.port)
        try:
            while(True):
                r = Message()
                m = self.recv_message()
                print_color(f"------> RECEIVED", color=RED)
                self.print_message(m, header="RECV")

                match m.type:
                    case MessageType.CONNECT: r = self.connectACK(m)
                    case MessageType.COMMAND: r = self.commandACK(m)
                    case MessageType.REPORT:  r = self.reportACK(m)
                    case _:                   self.err_message(m, f"UNEXPECTED MSG: {MessageType.Name(MessageType.ACK)} | {m.id}")

                self.print_message(r, header="SENT")
                print_color(f"<------ PROCESSED", color=GRN)
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



