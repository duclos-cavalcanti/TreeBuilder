from .message   import Message, MessageType, MessageFlag
from .node      import Node
from .ds        import Job, LOG_LEVEL
from .utils     import *

import heapq
import zmq

class Worker(Node):
    def __init__(self, name:str, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__(name, ip, port, zmq.REP, LOG_LEVEL)
        self.children  = []

    def child_job(self, rate:int, dur:int):
        C = f"./bin/child -i {self.ip} -p {int(self.port) - 1000} -d {dur}"
        J = Job(addr=self.hostaddr, command=C, params=[rate, dur])
        self.jobs[self.exec(target=self._run, args=(J,))] = J
        return J

    def child_resolve(self, m:Message, job:Job):
        print("CHILD RESOLVE:")

        total = job.params[0] * job.params[1]
        recv = int(job.out[0])
        perc = float(job.out[1])

        job.out = []
        job.out.append(perc)

        print(f"CHILD[{job.addr}] => PERC={perc} | RECV={recv}/{total} | RET={job.ret}")
        return job, self.ack_message(m, data=job.to_arr())

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
            data = [addr, self.hostaddr, rate, dur]
            H.connect(addr)
            r = H.handshake(id, MessageType.COMMAND, MessageFlag.CHILD, data, addr)
            rjob = Job(arr=r.data)
            J.deps.append(rjob)
            H.disconnect(addr)

        self.jobs[self.exec(target=self._run, args=(J,))] = J
        self.guards[self.exec(target=self._guard, args=(J, MessageFlag.CHILD))] = J

        return J

    def parent_resolve(self, m:Message, job:Job):
        print("PARENT RESOLVE:")
        sel   = int(job.params[0])
        rate  = int(job.params[1])
        dur   = int(job.params[2])

        if job.ret != 0: 
            return job, self.err_message(m, data=[f"PARENT[{job.addr}] JOB[{job.id}] FAILED"])

        for dep in job.deps: 
            if dep.ret != 0:
                return job, self.err_message(m, data=[f"PARENT'S CHILD[{dep.addr}] JOB[{dep.id}] FAILED"])

        percs    = [float(p) for p in job.concatenate()]
        sorted   = heapq.nsmallest(len(percs), enumerate(percs), key=lambda x: x[1])
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

            self.children.append(b_addr)
            out.append(b_addr)

        job.out = out
        return job, self.ack_message(m, data=job.to_arr())

    def mcast_job(self, id:int, rate:int, dur:int):
        C = f"./bin/mcast -r {rate} -d {dur}"

        # root and proxies
        if len(self.children) > 0: 
            f_children = []
            for c in self.children:
                split = c.split(":")
                ip = split[0]
                port = split[1]
                f_children.append(f"{ip}:{int(port) - 1000}")

            C += " -a " + " ".join(f"{c}" for c in f_children)
            if id == 0: 
                C += f" -R"
            else:
                C += f" -i {self.ip} -p {int(self.port) - 1000}"

            J = Job(addr=self.hostaddr, command=C, params=[id, rate, dur])
            H = self._node(zmq.REQ)

            id += 1
            for addr in self.children:
                data = [id , rate, dur]
                H.connect(addr)
                r = H.handshake(self.tick, MessageType.COMMAND, MessageFlag.MCAST, data, addr)
                rjob = Job(arr=r.data)
                J.deps.append(rjob)
                H.disconnect(addr)

            self.jobs[self.exec(target=self._run, args=(J,))] = J
            self.guards[self.exec(target=self._guard, args=(J, MessageFlag.MCAST))] = J

        # leaves
        else:
            C += f" -i {self.ip} -p {int(self.port) - 1000} -L"
            J = Job(addr=self.hostaddr, command=C, params=[id, rate, dur])
            self.jobs[self.exec(target=self._run, args=(J,))] = J

        return J

    def mcast_resolve(self, m:Message, job:Job):
        params = job.params
        id = params[0]
        data = []

        if job.params[0] == 0 and job.ret != 0:
            return job, self.err_message(m, data=[f"MCAST[{job.addr}] JOB[{job.id}] FAILED"])

        if len(self.children) > 0:
            for dep in job.deps: 
                if dep.ret != 0:
                    job.ret = dep.ret
                    return job, self.ack_message(m, data=job.to_arr())
                print(f"ADDR[{dep.addr}] => RES={dep.out[0]}")

            percs    = [float(p.split("/")[1]) for p in job.concatenate()]
            sorted   = heapq.nlargest(1, enumerate(percs), key=lambda x: x[1])
            out = []
            idx = sorted[0][0]
            perc = sorted[0][1]
            addr = job.deps[idx].out[0].split("/")[0]
            out.append(f"{addr}/{perc}")
            print(f"MCAST WORST LEAF OF {self.ip}:{self.port}: => {addr}: PERC={perc}")
            job.out = out
            return job, self.ack_message(m, data=job.to_arr())
        else:
            total = job.params[1] * job.params[2]
            recv = int(job.out[0])
            perc = float(job.out[1])

            job.out = []
            job.out.append(f"{job.addr}/{perc}")
            print(f"MCAST[{job.addr}] LEAF => PERC={perc} | RECV={recv}/{total} | RET={job.ret}")
            return job, self.ack_message(m, data=job.to_arr())

    def commandACK(self, m:Message):
        id, _, flag, data = self.parse_message(m)
        match flag:
            case MessageFlag.PARENT: 
                if len(data) <= 3: 
                    self.exit_message(m, "PARENT COMMAND ERR")
                sel   = int(data[0])
                rate  = int(data[1])
                dur   = int(data[2])
                addrs = data[3:]
                job = self.parent_job(sel, rate, dur, addrs)
                r = self.ack_message(m, data=job.to_arr())
                return r

            case MessageFlag.CHILD:  
                if len(data) < 4 or self.hostaddr != data[0]: 
                    self.exit_message(m, "CHILD COMMAND ERR")
                job = self.child_job(rate=int(data[2]), dur=int(data[3]))
                r = self.ack_message(m, data=job.to_arr())
                return r

            case MessageFlag.MCAST:  
                if len(data) < 3: 
                    self.exit_message(m, "MCAST COMMAND ERR")
                id    = int(data[0])
                rate  = int(data[1])
                dur   = int(data[2])
                job = self.mcast_job(id, rate, dur)
                r = self.ack_message(m, data=job.to_arr())
                return r

            case _:
                raise NotImplementedError(f"COMMAND FLAG: {MessageFlag.Name(flag)}")

    def reportACK(self, m:Message):
        _, _, flag, data = self.parse_message(m)
        t, job = self.find(Job(arr=data))
        job.complete = (job.end and job.is_resolved())
        if job.complete: 
            del self.jobs[t]
            match flag:
                case MessageFlag.PARENT: 
                    job, r = self.parent_resolve(m, job)
                    return r

                case MessageFlag.CHILD:  
                    job, r = self.child_resolve(m, job)
                    return r

                case MessageFlag.MCAST:  
                    job, r = self.mcast_resolve(m, job)
                    return r

                case _:
                    raise RuntimeError()
        else:
            return self.ack_message(m, data=job.to_arr())


    def connectACK(self, m:Message):
        _, _, _, data = self.parse_message(m)
        if len(data) < 2 or self.hostaddr != data[0]: 
            self.exit_message(m, "CONNECT ERR")

        self.manageraddr = data[1]
        return self.ack_message(m, data=[self.hostaddr])

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
                    case _:                   self.exit_message(m, f"UNEXPECTED MSG: {MessageType.Name(MessageType.ACK)} | {m.id}")

                self.print_message(r, header="SENT")
                print_color(f"<------ PROCESSED", color=GRN)
                self.tick += 1


        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        self.socket.close()



