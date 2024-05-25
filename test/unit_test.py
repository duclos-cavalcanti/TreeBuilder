import pytest
import ipdb

from manager import Tree, Node, LOG_LEVEL
from manager import Message, MessageType, MessageFlag

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
        n = Node(name="N0", ip="localhost", port="7070", type=zmq.REQ, LOG_LEVEL=LOG_LEVEL.DEBUG)
        n.socket.setsockopt(zmq.RCVTIMEO, 5000)
        n.connect(f"localhost:7071")

        m =  Message()
        m.id = 0 
        m.ts = n.timer.ts()
        m.type = Message::MessageType.COMMAND
        m.flag = MessageFlag.NONE

        try: 
            n.socket.send(m.SerializeToString())

        except zmq.Again: 
            print(f"SOCKET N0 TIMED OUT")

        finally:
            n.disconnect(f"localhost:7071")
            n.socket.close()
            return

    def callback_n1():
        n = Node(name="N0", ip="localhost", port="7071", type=zmq.REP, LOG_LEVEL=LOG_LEVEL.DEBUG)
        n.socket.bind(protocol="tcp", ip=n.ip, port=n.port)
        n.socket.setsockopt(zmq.RCVTIMEO, 5000)

        try: 
            m = n.recv_message()
            Q.put(m)

        except zmq.Again: 
            print(f"SOCKET N1 TIMED OUT")

        finally:
            n.socket.close()

    t0 = threading.Thread(target=callback_n0, args=())
    t1 = threading.Thread(target=callback_n1, args=())

    t0.start()
    t1.start()

    t0.join()
    t1.join()

    # test something was put into the Q
    assert not Q.empty()

    _ = Q.get_nowait()
