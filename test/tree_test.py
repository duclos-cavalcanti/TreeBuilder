import pytest
import ipdb

from manager import *
from typing  import List

import zmq
import threading

from queue import Queue

L = Logger()

class TestTreeClass:
    Q = Queue()

    # tests building of tree
    def test_a(self):
        fout  = 2 
        depth = 3

        # build tree
        self.build(fout=fout, depth=depth)

        # test if tree correctly reached complete state
        assert self.tree.max == self.tree.n

        # test if all leaves have the same depth equal to the one instructed
        assert any(self.tree.depth(node) == depth for node in self.tree.leaves())

        # test if general tree depth is correct
        assert self.tree.d == depth

        # test if tree refuses to add node beyond max
        assert False == self.tree.add("wrong")

    # tests splcing of tree downstream
    def test_b(self):
        fout  = 2 
        depth = 4
        self.build(fout=fout, depth=depth)

        buf = []
        buf.append([ a.id for a in self.tree.arr() ])

        def callback(tree, node, buf):
            assert buf[0]

            L.log(f"{node.id} RECV:\t{[id for id in buf[0]]}")

            for nbuf,ntree in zip(tree.slice(node), tree.slice(node, fmt=Format.TREE)):
                buf.append(nbuf)
                assert ntree.ids() == nbuf

            buf.pop(0)

        self.tree.traverse(callback, buf)
        assert not buf

    def build(self, fout, depth, verbose=False):
        root  = "r_0"
        child = "c"

        self.tree = Tree("TEST", root, fanout=fout, depth=depth)
        max  = self.tree.max

        for i in range(max - 1):
            id = f"{child}_{i}"
            self.pre_add()

            ret =  self.tree.add(id)
            assert ret == True

            self.post_add(id)
            self.state(verbose)
        
        L.log(f"TREE: {self.tree}")
        return self.tree

    def pre_add(self):
        self.cur   = self.tree.peak()
        self.qprev = self.tree._state()

    def post_add(self, new:str):
        self.new   = new
        self.qpost = self.tree._state()

    def state(self, verbose:bool):
        qs       = f"Q{self.qprev} => Q{self.qpost}"
        node     = f"NODE[{self.cur.id}]: PARENT[{'None' if self.cur.parent is None else self.cur.parent.id}]"
        children = f"CHILDREN: {[c.id for c in self.cur.children]}"
        if verbose:
            L.log(f"ADDED({self.new}): {qs}")
            L.log(f"{node} | {children}")
