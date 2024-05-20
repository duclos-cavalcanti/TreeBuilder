import pytest
import ipdb

from manager import Tree

def state(q):
    string = "[ "
    size = len(q)

    for i,n in enumerate(q):
        string += f"{n.id}"
        if i < size - 1:
            string += ", "
        else:
            string += " ]"

    return string

def node(n):
    print(f"NODE: {n.id} => ", end='')
    
    if (len(n.children) == 0):
        print(f"LEAF")
    else:
        print(f"CHILDREN: {[child.id for child in n.children]}")

def test_binary_tree():
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
        _q = state(t.queue)

        t.next()
        result = t.add(addr)

        q = state(t.queue)

        print(f"ADD_LEAF({addr}): {result}, D={t.d}")
        print(f"\tQUEUE:{_q} => {q}")
        print(f"\tNODE[{cur.id}] => PARENT[{parent}] | CHILDREN: {[child.id for child in cur.children]}")

        assert True == result

    print(f"TREE => NODES={t.n} | DEPTH={t.d}")
    t.traverse(node)
    result = t.add("wrong")
    assert False == result
