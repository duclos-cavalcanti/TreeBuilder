import pytest
import ipdb

from manager import *

import zmq
import threading

from queue import Queue

def test_tree():
    i = 0
    c = "c"
    fanout = 2
    depth = 3

    t = Tree("r_0", fanout=fanout, depth=depth)
    max = t._max()

    print()
    for i in range(max - 1):
        addr = f"{c}_{i}"

        cur = t.peak()
        parent = "___" if not cur.parent else cur.parent.id
        qprev = t._state()

        # test addition of node to tree
        result = t.add(addr)
        assert True == result

        q = t._state()

        # print(f"ADD_LEAF({addr}): {result}")
        # print(f"\tQUEUE:{qprev} => {q}")
        # print(f"\tNODE[{cur.id}] => PARENT[{parent}] | CHILDREN: {[child.id for child in cur.children]}")

    t.show()

    # test if tree correctly reached complete state
    assert max == t.n

    # test if all leaves have the same depth equal to the one instructed
    assert any(t.depth(node) == depth for node in t.leaves())

    # test if tree refuses to add node beyond max
    assert False == t.add("wrong")

def test_node():
    Q = Queue()

    def callback_n0():
        N = Node(name="REQ", stype=zmq.REQ, verbosity=True)
        N.socket.setsockopt(zmq.RCVTIMEO, 5000)
        N.connect(f"localhost:8090")

        c = Command(addr="FOOBAR", layer=(10), select=12, rate=5, dur=4)
        m = Message(id=1, ts=N.timer.ts(), type=Type.COMMAND, flag=Flag.PARENT, mdata=Metadata(command=c))

        try: 
            N.send_message(m)

        except zmq.Again: 
            print(f"SOCKET N0 TIMED OUT")

        finally:
            N.disconnect(f"localhost:8090")
            N.socket.close()
            return

    def callback_n1():
        N = Node(name="REP", stype=zmq.REP, verbosity=True)
        N.bind(protocol="tcp", ip="localhost", port="8090")
        N.socket.setsockopt(zmq.RCVTIMEO, 5000)

        try: 
            m = N.recv_message()
            Q.put(m)

        except zmq.Again: 
            print(f"SOCKET N1 TIMED OUT")

        finally:
            N.socket.close()

    t0 = threading.Thread(target=callback_n0, args=())
    t1 = threading.Thread(target=callback_n1, args=())

    t0.start()
    t1.start()

    t0.join()
    t1.join()

    # test something was put into the Q
    assert not Q.empty()

    m = Q.get_nowait()
    print(m)
