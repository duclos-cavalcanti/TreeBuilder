from ..message  import *
from .pool      import Seed, Pool
from .dicts     import *
from .tree      import Tree

from typing     import List

class Run():
    def __init__(self, run:RunDict, root:str, nodes:List, seed:int):
        self.data:RunDict = {
                "name": run["name"],
                "strategy": StrategyDict(run["strategy"]),
                "parameters": ParametersDict(run["parameters"]),
                "tree": TreeDict(run["tree"]),
                "pool": [n for n in nodes], 
                "stages": [],
                "perf": ResultDict(run["perf"])
        }
        self.pool       = Pool([n for n in nodes], run["parameters"]["hyperparameter"], seed)
        self.tree       = Tree(name=run["name"], 
                               root=root, 
                               fanout=run["tree"]["fanout"], 
                               depth=run["tree"]["depth"])

class Experiment():
    def __init__(self, schema:dict):
        self.seed    = Seed()
        self.manager = f"{schema['addrs'][0]}"
        self.workers = [ f"{addr}:{schema['port']}" for addr in schema["addrs"][1:] ] 
        self.root    = self.workers[0]
        self.map     = schema["map"]
        self.runs    = []

        for run in schema["runs"]:
            self.runs.append(Run(run, self.root, self.workers[1:], self.seed.get()))

