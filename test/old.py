import pytest
import ipdb

from manager import *
from types   import List

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
        # self.buffers = [[]]
        # for i in range(self.tree.d):
        #     self.buffers.append([])
        #
        # self.buffers[0] = self.tree.all()[1:]

        def callback(tree, node, _):
            pass
            # fout     = tree.fanout
            # cdepth   = tree.depth(node)
            # depth    = tree.d
            # layer    = depth - cdepth
            #
            # buf = self.buffers[cdepth][0]
            # nodes    = [ n for n in buf]
            #
            # L.log(f"NODE[{node.id}][L={layer}/D={cdepth}/DMAX={depth}]: RECV {[n.id for n in nodes]}")
            #
            # if layer:
            #     ret = self.splice(nodes[:fout], layer, fout, depth)
            #     if ret:
            #         for i in fout:
            #             L.log(f"NODE[{nodes[i].id}]: WILL RECV {[n.id for n in ret[i]]}")
            #             self.buffers[cdepth + 1].append([ n for n in ret[i] ])
            #
            #         self.buffers[cdepth].pop(0)

        self.tree.traverse(callback, [])

    def build(self, fout, depth, verbose=False):
        root  = "r_0"
        child = "c"

        self.tree = Tree("TEST", root, fanout=fout, depth=depth)
        max  = self.tree.max

        L.log(f"TREE INITIALIED: MAX={max}")
        for i in range(max - 1):
            id = f"{child}_{i}"
            self.before(id)

            ret =  self.tree.add(id)
            assert ret == True

            self.after()
            self.state(verbose)

        L.logd("TREE", d=self.tree.to_dict())

    # def splice(self, addrs:List, layer:int, fout:int, depth:int) -> List[List]:
    #     if layer == 0: raise RuntimeError()
    #
    #     ret = []
    #     if layer == 1:
    #         return ret
    #     else:
    #         ret = [ addrs[ (i*fout) : (i*fout) + fout] for i in range(fout)]
    #
    #         begin = (fout-1)*fout + fout
    #         end   = begin + (depth+1)*fout
    #
    #         for i in range(fout):
    #             for j in range(begin, end):
    #                 ret[i].append(addrs[j])
    #
    #         return ret

    def before(self, new:str):
        self.new   = new
        self.cur   = self.tree.peak()
        self.qprev = self.tree._state()

    def after(self):
        self.qpost = self.tree._state()

    def state(self, verbose:bool):
        qs       = f"Q{self.qprev} => Q{self.qpost}"
        node     = f"NODE[{self.cur.id}]: PARENT[{'None' if self.cur.parent is None else self.cur.parent.id}]"
        children = f"CHILDREN: {[c.id for c in self.cur.children]}"
        if verbose:
            L.log(f"ADDED({self.new}): {qs}")
            L.log(f"{node} | {children}")
