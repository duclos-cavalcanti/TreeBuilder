from .logger import Logger

import hashlib 

from collections import deque
from typing import List, Callable, Optional
from enum import Enum, auto

class Format(Enum):
    TREE = auto()
    ARR  = auto()
    IDS  = auto()

class TreeNode():
    def __init__(self, id:str, parent=None):
        self.id = ''.join(id.split())
        self.parent = parent
        self.children = []

    def __str__(self):
        parent = "NONE" if self.parent is None else self.parent.id
        ret    = f"NODE: {self.id} | PARENT={parent} | CHILDREN={[c.id for c in self.children]}"
        return ret

class Tree():
    def __init__(self, name:str, root:str, fanout:int, depth:int, arr:List[str]=[]):
        self.name   = name
        self.fanout = fanout
        self.d      = 0
        self.dmax   = depth
        self.max    = self._max()
        self.n      = 1
        self.L      = Logger()

        self.root   = TreeNode(root)
        self.queue  = deque([self.root])
        if arr:
            for i,a in enumerate(arr):
                if not self.add(a):
                    raise RuntimeError(f"List[{i}] exceeds tree dimensions: {self}")

    def hash(self):
        string = "".join(self.ids())
        H = hashlib.sha256()
        H.update(string.encode())
        return H.hexdigest()

    def _state(self):
        ret = "[ "
        for i,n in enumerate(self.queue):
            ret += f"{n.id}"
            if i < len(self.queue) - 1:
                ret += ", "

        ret += " ]"
        return ret

    def _max(self):
        F = self.fanout
        D = self.dmax
        if F == 1:
            return D + 1
        else:
            return (F ** (D + 1) - 1) // (F - 1)

    def full(self):
        return (self.n >= self.max)

    def peak(self):
        node = self.queue[0]
        return node

    def next(self):
        if self.queue:
            n = self.peak()
            return n.id
        else:
            raise RuntimeError("Tree queue is empty")

    def depth(self, node):
        d = 0 
        n = node
        while n.parent is not None:
            d += 1
            n = n.parent
        return d

    def n_add(self, arr:List):
        for id in arr:
            self.add(id)

    def add(self, id):
        if self.full():
            return False

        node = self.peak()
        new  = TreeNode(id, parent=node)
        node.children.append(new)
        self.n += 1
        self.d = self.depth(new)

        if len(node.children) >= self.fanout:
            self.queue.popleft()
            if not self.queue and self.n < self.max:
                self.queue.extend(self.leaves())

        return True

    def find(self, id:str):
        buf = []
        def callback(_, node, buf):
            if node.id == id:
                buf.append(node)

        self.traverse(callback, buf)
        return len(buf) == 1, buf[0]

    def traverse(self, callback:Callable, buf:List, node:Optional[TreeNode]=None):
        if node is None: node = self.root
        queue = deque([node])
        while queue:
            node = queue.popleft()
            callback(self, node, buf)
            queue.extend(node.children)

    def leaves(self) -> List:
        buf = []
        def callback(_, node, buf):
            if len(node.children) == 0: 
                buf.append(node)

        self.traverse(callback, buf)
        return buf

    def arr(self, node:Optional[TreeNode]=None) -> List:
        buf = []
        def callback(_, node, buf):
            buf.append(node)

        self.traverse(callback, buf, node)
        return buf

    def ids(self, node:Optional[TreeNode]=None) -> List:
        if node is None: 
            node = self.root

        ret = [ a.id for a in self.arr(node) ]
        return ret

    def slice(self, node:Optional[TreeNode]=None, fmt:Format=Format.IDS) -> List:
        ret = []
        if node is None: 
            node = self.root

        for c in node.children:
            if   fmt == Format.IDS: ret.append(self.ids(c))
            elif fmt == Format.ARR: ret.append(self.arr(c))
            else:                   ret.append(self.subtree(c))

        return ret

    def subtree(self, node:Optional[TreeNode]=None):
        if node is None: 
            node = self.root

        arr = self.ids(node)
        ret = Tree(name=f"SUBTREE:{self.root.id}:{node.id}", root=arr[0], 
                   fanout=self.fanout, 
                   depth=(self.d - self.depth(node)), 
                   arr=arr[1:])

        return ret

    def __str__(self):
        ret = ""
        buf = []
        buf.append(f"NAME={self.name}")
        buf.append(f"FOUT={self.fanout}, DEPTH={self.d}/{self.dmax}")
        buf.append(f"N={self.n}/{self.max}")

        ret += "\n" + "\n".join(buf)
        ret += "\n" + "NODES: "

        buf = []
        def callback(_, node, buf):
            name     = node.id
            children = [child.id for child in node.children]
            buf.append(f"{name}:\t {children}")

        self.traverse(callback, buf)
        ret += "\n\t" + "\n\t".join(buf)
        return ret
