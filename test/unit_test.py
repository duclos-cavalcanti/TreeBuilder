import pytest
import zmq

from manager import Tree

def test_binary_tree():
    i = 0
    c = "child"
    fanout = 2
    max = 3

    t = Tree("root", fanout=fanout, max_height=max)
    for i in range(fanout * max):
        addr = f"{c}_{i}"
        assert True == t.add_leaf(addr)

    t.show()
    assert False == True

