from .logger        import Logger
from .dicts         import TreeDict

import hashlib 

from collections import deque
from typing import List, Callable, Optional

class TreeBuilder():
    def __init__(self, arr:List[str], depth:int, fanout:int):
        self.root   = arr[0]
        self.depth  = depth
        self.fanout = fanout
        self.tree   = Tree(name="BUILDER", root=self.root, fanout=self.fanout, depth=self.depth, arr=arr[1:]) 

        if not self.tree.full(): 
            raise RuntimeError("Array does not form a tree")

    def slice(self):
        ret = self.tree.slice()
        return ret

    @staticmethod
    def _parent(_, node, data):
        if len(node.children) > 0:
            c  =  f"./bin/parent -a "
            c  += f" ".join(f"{n.id.split(':')[0]}:{data.port}" for n in node.children)
            c  += f" -w {data.warmup}"
            c  += f" -r {data.rate} -d {data.duration}"
        else:
            c   =  f"./bin/child -i {node.id.split(':')[0]} -p {data.port}"
            c   += f" -r {data.rate} -d {data.duration}"
            c   += f" -w {data.warmup}"
            c   += f" -n {node.id.split(':')[0]}_{data.id}"

        data.buf.append(c)

    def parent(self, rate, duration, id, warmup, port:int=8080):
        class Data:
            def __init__(self):
                self.rate       = rate
                self.duration   = duration
                self.id         = id
                self.warmup     = warmup
                self.port       = port
                self.buf        = []

        data = Data()
        self.tree.traverse(self._parent, data)
        return data

    @staticmethod
    def _mcast(_, node, data):
        if len(node.children) > 0:
            c   =   f"./bin/mcast -a "
            c   +=  f" ".join(f"{n.id.split(':')[0]}:{data.port}" for n in node.children)
            c   +=  f" -r {data.rate} -d {data.duration}"
            c   +=  f" -w {data.warmup}"
            c   +=  f" -i {node.id.split(':')[0]} -p {data.port}"
            if node.parent is None: c += " -R"
        else:
            c   =   f"./bin/mcast "
            c   +=  f" -r {data.rate} -d {data.duration}"
            c   +=  f" -w {data.warmup}"
            c   +=  f" -i {node.id.split(':')[0]} -p {data.port}"
            c   +=  f" -n {node.id.split(':')[0]}_{data.id}"

        data.buf.append(c)

    def mcast(self, rate, duration, id, warmup, port:int=7070):
        class Data:
            def __init__(self):
                self.rate       = rate
                self.duration   = duration
                self.id         = id
                self.warmup     = warmup
                self.port       = port
                self.buf        = []

        data = Data()
        self.tree.traverse(self._mcast, data)
        return data

class TreeNode():
    def __init__(self, id:str, parent=None):
        self.id = id
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
        self.n      = 1
        self.nmax   = self.max()
        self.L      = Logger()

        self.root   = TreeNode(root)
        self.queue  = deque([self.root])
        if arr:
            for i,a in enumerate(arr):
                if not self.add(a):
                    raise RuntimeError(f"List[{i}] exceeds tree dimensions: {self}")

    def get(self):
        ret:TreeDict = {
                "name": self.name, 
                "fanout": self.fanout, 
                "depth": self.d, 
                "n": self.n, 
                "max": self.nmax, 
                "root": self.root.id,
                "nodes": self.arr()
        }
        return ret

    def hash(self):
        string = "".join(self.arr())
        H = hashlib.sha256()
        H.update(string.encode())
        return H.hexdigest()

    def max(self):
        F = self.fanout
        D = self.dmax
        if F == 1:
            return D + 1
        else:
            return (F ** (D + 1) - 1) // (F - 1)

    def full(self):
        return (self.n >= self.nmax)

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
            if not self.queue and self.n < self.nmax:
                self.queue.extend(self.leaves())

        return True

    def find(self, id:str):
        data = []
        def callback(_, node, data):
            if node.id == id:
                data.append(node)

        self.traverse(callback, data)
        return len(data) == 1, data[0]

    def traverse(self, callback:Callable, data, node:Optional[TreeNode]=None):
        if node is None: node = self.root
        queue = deque([node])
        while queue:
            node = queue.popleft()
            callback(self, node, data)
            queue.extend(node.children)

    def leaves(self) -> List:
        data = []
        def callback(_, node, data):
            if len(node.children) == 0: 
                data.append(node)

        self.traverse(callback, data)
        return data

    def nodes(self, node:Optional[TreeNode]=None) -> List:
        data = []
        def callback(_, node, data):
            data.append(node)

        self.traverse(callback, data, node)
        return data

    def arr(self, node:Optional[TreeNode]=None) -> List:
        if node is None: 
            node = self.root

        ret = [ a.id for a in self.nodes(node) ]
        return ret

    def slice(self, node:Optional[TreeNode]=None) -> List:
        ret = []
        if node is None: 
            node = self.root

        for c in node.children:
            ret.append(self.arr(c))

        return ret

    def __str__(self):
        ret = ""
        arr = []
        arr.append(f"NAME={self.name}")
        arr.append(f"FOUT={self.fanout}, DEPTH={self.d}/{self.dmax}")
        arr.append(f"N={self.n}/{self.nmax}")

        ret += "\n" + "\n".join(arr)
        ret += "\n" + "NODES: "

        data = []
        def callback(_, node, data):
            name     = node.id
            children = [child.id for child in node.children]
            data.append(f"{name}:\t {children}")

        self.traverse(callback, data)
        ret += "\n\t" + "\n\t".join(data)
        return ret
