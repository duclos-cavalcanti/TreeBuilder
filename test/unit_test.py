import pytest
import ipdb

from manager import Tree

def test_binary_tree():
    def callback(t, n):
        if n.parent == None: 
            print(f"TREE => NODES={t.n} | DEPTH={t.d}")

        print(f"NODE: {n.id} => \t", end='')

        print(f"DEPTH={t.depth(n)}, ", end='')
        
        if (len(n.children) == 0):
            print(f"LEAF")
        else:
            print(f"CHILDREN: {[child.id for child in n.children]}")

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

        print(f"ADD_LEAF({addr}): {result}")
        print(f"\tQUEUE:{qprev} => {q}")
        print(f"\tNODE[{cur.id}] => PARENT[{parent}] | CHILDREN: {[child.id for child in cur.children]}")

    t.traverse(callback)

    # test if tree correctly reached complete state
    assert max == t.n

    # test if all leaves have the same depth equal to the one instructed
    assert any(t.depth(node) == depth for node in t.leaves())

    # test if tree refuses to add node beyond max
    assert False == t.add("wrong")
