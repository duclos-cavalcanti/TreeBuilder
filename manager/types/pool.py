from typing import List

import random

from .logger import Logger

class Pool():
    def __init__(self, elements:List, K:float, N:int):
        self.base = [ e for e in elements ]
        self.pool = [ e for e in elements ]
        self.K = K 
        self.N = N
        self.L = Logger()

    def reset(self):
        self.pool.clear()
        self.pool.extend(self.base)

    def select(self, remove:bool=True):
        self.L.log(f"{self}")
        pool = self.pool
        size = len(pool)
        idx = random.randint(0, size - 1)
        el = self.pool[idx]
        if remove: self.pool.pop(idx)
        self.L.log(f"{self}")
        return el

    def slice(self, param:int=0):
        self.L.log(f"{self}")
        return self.pool

    def n_remove(self, elements:List):
        for el in elements: 
            self.remove(el)

    def remove(self, el:str):
        for i,p in enumerate(self.pool):
            if p == el: 
                self.pool.pop(i)
                self.L.log(f"POOL REMOVED: {i} => {el}")
                return
        raise RuntimeError(f"ATTEMPT TO REMOVE[{el}] NOT IN POOL")

    def to_dict(self):
        data = {}
        data["K"]       = self.K
        data["N"]       = self.N
        data["NODES"]   = [ p for p in self.pool ]

        return data

    def __str__(self):
        ret =  ""
        ret += f"POOL: {[e for e in self.pool]}"
        return ret
