from ..message  import *
from .pool      import Seed, Pool
from .dicts     import *
from .tree      import Tree

from typing     import List

import time

class Run():
    def __init__(self, run:RunDict, root:str, nodes:List, seed:int):
        self.data:RunDict = {
                "name": run["name"],
                "strategy": StrategyDict(run["strategy"]),
                "parameters": ParametersDict(run["parameters"]),
                "tree": TreeDict(run["tree"]),
                "pool": [n for n in nodes], 
                "stages": [],
                "perf": [ ResultDict(perf) for perf in run["perf"] ],
                "timers": TimersDict({
                    "build": 0.0,
                    "stages": [],
                    "convergence": 0.0,
                    "perf": [ 0.0 for _ in range(len(run["perf"])) ],
                    "total": 0.0,
                })
        }
        self.pool       = Pool([n for n in nodes], run["parameters"]["hyperparameter"], seed)
        self.tree       = Tree(name=run["name"], 
                               root=root, 
                               fanout=run["tree"]["fanout"], 
                               depth=run["tree"]["depth"])

class Experiment():
    def __init__(self, schema:dict):
        self.manager = f"{schema['addrs'][0]}"
        self.workers = [ f"{addr}:{schema['port']}" for addr in schema["addrs"][1:] ] 
        self.seed    = Seed()
        self.map     = schema["map"]
        self.runs    = []

        pairs        = []
        choices      = schema["runs"][0]["parameters"]["choices"]
        if choices > 1:
            for _ in range(choices):
                pool    = Pool(self.workers, 0, self.seed.get())
                root    = pool.select()
                workers = pool.get()
                pairs.append((root, workers))
        else:
            pool    = Pool(self.workers, 0, self.seed.get())
            root    = pool.select()
            workers = pool.get()
            pairs.append((root, workers))

        for run in schema["runs"]:
            name = run["name"]
            for i, (root, workers) in enumerate(pairs):
                if "LEMON" in name:
                    run["name"] = f"{name}-{i+1}"
                    self.runs.append(Run(run, "NONE", self.workers, self.seed.get())  )

                elif "RAND" in name:  
                    self.runs.append(Run(run, root,   workers,      int(time.time())) )

                else:               
                    self.runs.append(Run(run, root,   workers,      self.seed.get())  )

