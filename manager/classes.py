from .zmqsocket import Message, MessageType, ReplySocket, RequestSocket, LOG_LEVEL

import time

class Node():
    def __init__(self):
        pass

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
                m = S.recv_message()
                r = Message()
                S.set_message(r, MessageType.ACK, m.id, "NONE")
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
                S.set_message(m, MessageType.REPORT, i, "DATA")
                S.send_message(m)
                _ = S.recv_message()
                time.sleep(1)
                i += 1
        except KeyboardInterrupt:
            print("\n-------------------")
            print("Manually Cancelled!")
        S.close()



