import pytest
import ipdb

from manager import Tree

def test_binary_tree():
    i = 0
    c = "c"
    fanout = 2
    depth = 3

    t = Tree("r_0", fanout=fanout, depth=depth)
    max = t._max()
    print()

    for i in range(max - 1):
        cur = t.peak()
        parent = "___" if not cur.parent else cur.parent.id
        _q = t.state()

        addr = f"{c}_{i}"
        result = t.add(addr)

        q = t.state()

        print(f"ADD_LEAF({addr}): {result}, D={t.d}")
        print(f"\tQUEUE:{_q} => {q}")
        print(f"\tNODE[{cur.id}] => PARENT[{parent}] | CHILDREN: {[child.id for child in cur.children]}")

        assert True == result

    t.print()
    result = t.add("wrong")
    assert False == result
