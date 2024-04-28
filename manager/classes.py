from .zmqsocket import Message, MessageType, ReplySocket, RequestSocket, LOG_LEVEL

import time

class Node():
    def __init__(self):
        pass

    def set_message(self, m:Message, t:MessageType, id:int, data:str):
        ts = int(time.time_ns() / 1_000)
        m.id    = id
        m.ts    = ts
        m.type  = t
        m.data  = data

    def print_message(self, m:Message):
        print(f"{{")
        print(f"    ID: {m.id}")
        print(f"    TS: {m.ts}")
        print(f"    TYPE: {MessageType.Name(m.type)}")
        print(f"    DATA: {m.data}\n}}")

class Manager(Node):
    def __init__(self, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__()
        self.socket = ReplySocket(protocol="tcp", ip="*", port=port, LOG_LEVEL=LOG_LEVEL)

    def run(self):
        S = self.socket
        S.bind()

        try:
            i = 0
            while(True):
                r = Message()
                m = S.recv_message()
                self.print_message(m)
                self.set_message(r, MessageType.ACK, m.id, "NONE")
                S.send_message(r)

        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        S.close()



class Worker(Node):
    def __init__(self, ip:str, port:str, LOG_LEVEL=LOG_LEVEL.NONE):
        super().__init__()
        self.socket = RequestSocket(protocol="tcp", ip=ip, port=port, LOG_LEVEL=LOG_LEVEL)

    def run(self):
        S = self.socket
        S.connect()

        try:
            i = 0
            while(True):
                m = Message()
                self.set_message(m, MessageType.REPORT, i, "DATA")
                S.send_message(m)
                r = S.recv_message()
                self.print_message(r)
                time.sleep(1)
                i += 1
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        S.close()



