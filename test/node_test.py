import pytest
import ipdb

from manager import *

import zmq
import threading

from queue import Queue

N0_ADDR=f"localhost:8091"
N1_ADDR=f"localhost:8090"

L = Logger()

class TestNodeClass:
    Q = Queue()

    def test(self):
        t0 = self.launch(self.sender)
        t1 = self.launch(self.receiver)

        t0.join()
        t1.join()

        # test something was put into the Q
        assert not self.Q.empty()

        mtx = self.Q.get_nowait()
        mrx = self.Q.get_nowait()

        assert mtx == mrx

    def sender(self):
        N = Node(stype=zmq.REQ)
        N.socket.setsockopt(zmq.RCVTIMEO, 5000)
        L.log(message=f"SENDER NODE UP")

        N.connect(N1_ADDR)
        L.log(message=f"SENDER NODE CONNECTED")

        m = N.message(src=N0_ADDR, dst=N1_ADDR, t=Type.CONNECT)
        self.Q.put(m)

        try: 
            N.send_message(m)
            L.logm("SENT MESSAGE:", m)

            N.recv_message()
            L.log(message=f"RECV ACK")

        except zmq.Again: 
            L.log(message=f"SENDER TIMED OUT")

        finally:
            N.disconnect(N1_ADDR)
            N.socket.close()
            return

    def receiver(self):
        N = Node(stype=zmq.REP)
        N.socket.setsockopt(zmq.RCVTIMEO, 5000)
        L.log(message=f"RECEIVER NODE UP")

        N.bind(protocol="tcp", ip=N1_ADDR.split(":")[0], port=N1_ADDR.split(":")[1])
        L.log(message=f"RECEIVER NODE BOUND")

        try: 
            m = N.recv_message()
            L.logm("RECV MESSAGE:", m)

            self.Q.put(m)
            N.ack_message(m)
            L.log(message=f"SENT ACK")

        except zmq.Again: 
            L.log(message=f"RECEIVER TIMED OUT")

        finally:
            N.socket.close()

    def launch(self, target, args=()):
        t = threading.Thread(target=target, args=args)
        t.start()
        return t
