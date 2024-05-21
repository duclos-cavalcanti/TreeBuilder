import hashlib
import time

from collections import deque
from typing import List, Callable
from enum import Enum

class DictionaryQueue():
    def __init__(self):
        self.Q = []

    def make(self, **kwargs) -> dict:
        return kwargs

    def pop(self) -> dict:
        if len(self.Q) == 0: 
            return {}
        ret = self.Q[0]
        self.Q.pop(0)
        return ret

    def push(self, d:dict) -> None:
        self.Q.append(d)

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

class Tree():
    class Layer():
        def __init__(self, length:int):
            self.length = length

    class Node():
        def __init__(self, id:str, parent=None):
            self.id = ''.join(id.split())
            self.parent = parent
            self.children = []

    def __init__(self, root:str, fanout:int=2, depth:int=2):
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
            else:
                ret += " ]"

        return ret

    def _max(self):
        F = self.fanout
        D = self.dmax
        if F == 1:
            return D + 1
        else:
            return (F ** (D + 1) - 1) // (F - 1)

    def peak(self):
        node = self.queue[0]
        return node

    def next(self):
        n = self.peak()
        return n.id, self.fanout

    def depth(self, node):
        d = 0 
        n = node
        while n.parent is not None:
            d += 1
            n = n.parent
        return d

    def add(self, id, verbose:bool=False):
        if self.n >= self.max:
            return False

        node = self.peak()
        node.children.append(self.Node(id, parent=node))
        self.n += 1

        if verbose:
            print(f"ADDED {id} TO TREE")

        if len(node.children) >= self.fanout:
            self.queue.popleft()
            if not self.queue:
                self.queue.extend(self.leaves())

        return True

    def traverse(self, callback:Callable):
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            callback(self, node)
            queue.extend(node.children)

    def leaves(self) -> List:
        self.arr = []
        def callback(self, node):
            if len(node.children) == 0: 
                self.arr.append(node)

        self.traverse(callback)
        return self.arr

    def show(self, header:str=""):
        def callback(_, node):
            n_children = len(node.children)
            if node.parent == None: name = "ROOT"
            elif n_children > 0:    name = "NODE"
            else:                   name = "LEAF"

            print(f"{name}: {node.id} \t=> CHILDREN: {[child.id for child in node.children]}")

        if header: print(f"{header}")
        self.traverse(callback)


class Job():
    def __init__(self, addr:str="", command:str="", params:List=[], arr:List=[]):
        if len(arr) > 0:
            if len(arr) < 8 : 
                raise RuntimeError(f"Arr has incorrect length: {arr}")
            self.from_arr(arr)
        else:
            self.id         = self.hash(f"{addr}{command}")
            self.pid        = 0
            self.addr       = addr
            self.command    = command
            self.end        = False
            self.complete   = False
            self.ret        = -1
            self.params     = params
            self.out        = [ "NONE" ]
        self.deps = []

    def __str__(self):
        output = [f"{{"]
        output.append(f"\tID={self.id}")
        output.append(f"\tPID={self.pid}")
        output.append(f"\tADDR={self.addr}")
        output.append(f"\tCOMM={self.command}")
        output.append(f"\tEND={self.end}")
        output.append(f"\tCOMPLETE={self.end}")
        output.append(f"\tRET={self.ret}")
        output.append(f"\tPARAM={self.params}")
        output.append(f"\tOUT=[")
        for o in self.out: output.append(f"\t\t{o}")
        output.append(f"\t]")
        output.append(f"}}")
        return "\n".join(output)


    def hash(self, string:str) -> str: 
        bytes = string.encode('utf-8')
        hash = hashlib.sha256(bytes)
        return hash.hexdigest()

    def is_resolved(self) -> bool: 
        for d in self.deps:
            if d.end == False: 
                return False
        return True

    def concatenate(self) -> bool: 
        for d in self.deps:
            for o in d.out:
                self.out.append(str(o))
        return True

    def to_arr(self) -> List:
        ret = []
        ret.append(f"{self.id}")
        ret.append(f"{self.pid}")
        ret.append(f"{self.addr}")
        ret.append(f"{self.command}")
        ret.append(f"{self.end}")
        ret.append(f"{self.complete}")
        ret.append(f"{self.ret}")
        ret.append(f"{self.params}")
        if len(self.out) == 0:
            ret.append(f"[]")
        else:
            for o in self.out: 
                ret.append(f"{o}")
        return ret

    def from_arr(self, arr:List):
        self.id         = arr[0]
        self.pid        = arr[1]
        self.addr       = arr[2]
        self.command    = arr[3]
        self.end        = True if arr[4] == "True" else False
        self.complete   = True if arr[5] == "True" else False
        self.ret        = arr[6]
        self.params     = arr[7]
        self.out = []
        for o in arr[8:]:
            self.out.append(o)

class LOG_LEVEL(Enum):
    NONE = 1 
    DEBUG = 2 
    ERROR = 3
