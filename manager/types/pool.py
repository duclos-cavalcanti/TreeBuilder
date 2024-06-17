from .logger import Logger

import random
import time

from typing import List, Optional

class Seed():
    def __init__(self):
        self.seed = int(time.time())

    def get(self) -> int:
        return self.seed

class Pool():
    def __init__(self, elements:List, K:int, seed:int):
        self.base = [ e for e in elements ]
        self.pool = [ e for e in elements ]
        self.seed = seed
        self.rng = random.Random(self.seed)
        self.K = K 
        self.N = len(elements)
        self.L = Logger()

    def reset(self):
        self.pool.clear()
        self.pool.extend([b for b in self.base])

    def select(self, pool:Optional[List]):
        if pool is None: pool = self.pool
        idx = self.rng.randint(0, len(pool) - 1)
        el = pool[idx]
        pool.pop(idx)
        return el

    def slice(self, param:int=-1):
        if param < 0: param = self.K

        if len(self.pool) <= param: 
            return self.pool
        else:
            pseudo = [ p for p in self.pool ]
            return [ self.select(pool=pseudo) for _ in range(param) ]

    def n_remove(self, elements:List):
        for el in elements: 
            self.remove(el)

    def remove(self, el:str):
        for i,p in enumerate(self.pool):
            if p == el: 
                self.pool.pop(i)
                return
        raise RuntimeError(f"{el} NOT IN POOL")

    def __str__(self):
        ret = f"POOL: {[e for e in self.pool]}"
        return ret
