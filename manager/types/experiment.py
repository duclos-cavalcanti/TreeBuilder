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

class Result():
    def __init__(self, result:ResultDict):
        self.data:ResultDict = ResultDict(result)

class Experiment():
    def __init__(self, schema:dict):
        self.manager = f"{schema['addrs'][0]}"
        self.workers = [ f"{addr}:{schema['port']}" for addr in schema["addrs"][1:] ] 
        self.seed    = Seed()
        self.map     = schema["map"]
        self.runs    = []

        pairs        = []
        choices      = schema["runs"][0]["parameters"]["choices"]
        pool         = Pool(self.workers, 0, self.seed.get())

        for _ in range(choices):
            root    = pool.select()
            workers = pool.get()
            pairs.append((root, workers))

        for run in schema["runs"]:
            if run["name"] == "LEMON": 
                self.runs.append(Run(run, "NONE", self.workers, self.seed.get()))
            else:                      
                for pair in pairs: 
                    root, workers = pair
                    self.runs.append(Run(run, root, workers, self.seed.get()))

