import time
import random
import json
import threading

from collections import deque
from typing import List, Callable

class SQueue():
    def __init__(self, arr:List=[]):
        self.Q = arr

    def peak(self):
        if len(self.Q) == 0: 
            return None
        return self.Q[0]

    def pop(self):
        if len(self.Q) == 0: 
            return None
        el = self.Q[0]
        self.Q.pop(0)
        return el

    def push(self, el) -> None:
        self.Q.append(el)

    def __str__(self):
        return self.Q.__str__()

class Timer():
    def __init__(self):
        pass

    def ts(self) -> int: 
        return int(time.time_ns() / 1_000)

    def future_ts(self, sec:float) -> int: 
        now = self.ts()
        return int(now + self.sec_to_usec(sec))

    def sleep_to(self, ts:int): 
        now = self.ts()
        if ts > now: 
            self.sleep_usec(ts - now)
        else:
            print(f"TRIGGER EXPIRED={ts} < NOW={now}")

    def sleep_sec(self, sec:float): 
        time.sleep(sec)

    def sleep_usec(self, usec:int): 
        print(f"SLEEP UNTIL: {usec}")
        self.sleep_sec(self.usec_to_sec(usec))
        print(f"AWAKE AT: {self.ts()}")

    def sec_to_usec(self, sec:float) -> float:
        return (sec * 1_000_000)
    
    def usec_to_sec(self, usec:int) -> float:
        return usec / 1_000_000

class Pool():
    def __init__(self, elements:List, K:float, N:int):
        self.base = [ e for e in elements ]
        self.pool = elements
        self.K = K 
        self.N = N

    def reset(self):
        self.pool.clear()
        self.pool.extend(self.base)

    def select(self, verbose=False):
        pool = self.pool
        size = len(pool)
        idx = random.randint(0, size - 1)
        el = self.pool[idx]
        self.pool.pop(idx)

        if verbose: 
            print(f"CHOSEN: {idx} => {el}")
            print(self)

        return el

    def slice(self, param:int=0, verbose=False):
        if verbose: print(self)
        return self.pool

    def n_remove(self, elements:List, verbose=False):
        for el in elements: 
            self.remove(el, verbose)

    def remove(self, el:str, verbose=False):
        for i,p in enumerate(self.pool):
            if p == el: 
                self.pool.pop(i)
                if verbose: 
                    print(f"REMOVED: {i} => {el}")
                return
        raise RuntimeError(f"ATTEMPT TO REMOVE[{el}] NOT IN POOL")

    def to_dict(self):
        data = {}
        data["K"]       = self.K
        data["N"]       = self.N
        data["NODES"]   = [ p for p in self.pool ]

        return data

    def __str__(self):
        buf = []
        buf.append("POOL: {")
        for i,el in enumerate(self.pool): 
            buf.append(f"\t{i} => {el}")
        buf.append("}")
        ret = "\n".join(buf)
        return ret


class Tree():
    class Node():
        def __init__(self, id:str, parent=None):
            self.id = ''.join(id.split())
            self.parent = parent
            self.children = []

    def __init__(self, name:str, root:str, fanout:int=2, depth:int=2):
        self.name   = name
        self.root   = self.Node(root)
        self.fanout = fanout
        self.d      = 0
        self.dmax   = depth
        self.max    = self._max()
        self.n      = 1

        self.queue  = deque([self.root])

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
            raise RuntimeError("Tree Queue is empty")

    def depth(self, node):
        d = 0 
        n = node
        while n.parent is not None:
            d += 1
            n = n.parent
        return d

    def n_add(self, arr:List, verbose:bool=False):
        for id in arr:
            self.add(id, verbose=verbose)

    def add(self, id, verbose:bool=False):
        if self.full():
            return False

        node = self.peak()
        node.children.append(self.Node(id, parent=node))
        self.n += 1

        if verbose:
            print(f"ADDED {id} TO TREE")

        if len(node.children) >= self.fanout:
            self.queue.popleft()
            if not self.queue and self.n < self.max:
                self.queue.extend(self.leaves())

        return True

    def traverse(self, callback:Callable, buf:List):
        queue = deque([self.root])
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

    def to_dict(self):
        data = {}
        buf  = []

        def callback(_, node, buf):
            name     = node.id
            children = [child.id for child in node.children]
            buf.append([name, children])
        self.traverse(callback, buf)

        data["NAME"]    = self.name
        data["F"]       = self.fanout
        data["D"]       = self.d
        data["DMAX"]    = self.dmax
        data["MAX"]     = self.max
        data["NODES"]   = {}

        for arr in buf:
            name     = arr[0]
            children = arr[1]
            data["NODES"][name] = children

        return data

    def __str__(self):
        buf = ["TREE:"]
        def callback(_, node, buf):
            n_children = len(node.children)
            if node.parent == None: name = "ROOT"
            elif n_children > 0:    name = "NODE"
            else:                   name = "LEAF"
            buf.append(f"{name}: {node.id} \t=> CHILDREN: {[child.id for child in node.children]}")

        self.traverse(callback, buf)
        ret = "\n".join(buf)
        return  ret

class Logger():
    def __init__(self, file:str="LOG.JSON"):
        self.file    = file
        self.buf     = {}
        self.events  = []
        self.trees   = []
        self.records = []
        self.lock    = threading.Lock()

    def event(self, key, data, verbosity=False):
        with self.lock:
            self.events.append({key: data})
            if verbosity: 
                print(f"{key} => {data}")

    def record(self, key, data, verbosity=False):
        with self.lock:
            self.records.append({key: data})
            if verbosity: 
                print(f"{key} => {data}")

    def tree(self, key, data, verbosity=False):
        with self.lock:
            self.trees.append({key: data})
            if verbosity: 
                print(f"{key} => {data}")

    def get(self, key, default):
        with self.lock:
            ret = self.buf.get(key, default)
            return ret

    def write(self, key, data):
        with self.lock:
            self.buf[key] = data

    def update(self):
        self.buf["records"] = self.records
        self.buf["trees"]   = self.trees
        self.buf["events"]  = self.events

    def dump(self):
        with self.lock:
            self.update()
            with open(self.file, 'w') as f:
                json.dump(self.buf, f, indent=4)

    def __str__(self):
        with self.lock:
            self.update()
            ret = json.dumps(self.buf, indent=4)
            return ret


