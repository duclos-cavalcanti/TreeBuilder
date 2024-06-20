import os
import json
import shutil
import ipdb

from manager import Pool

from .experiment import Experiment

class Parser():
    def __init__(self, dir:str):
        self.map         = {}
        self.experiments = self.read(dir)
        self.schema      = self.load(dir)
        self.sort()

        assert(len(self.experiments) == len(self.schema["runs"]))

    def read(self, dir:str):
        file = os.path.join(dir, "events.log")
        exp    = []
        exps   = []
        events = []
        with open(file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    events.append(event)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {line.strip()} - {e}")

        for e in events:
            if   "RUN" in e:
                exp.append(e)

            elif "PERF" in e:
                exp.append(e)
                exps.append(exp)
                exp = []

            else:
                exp.append(e)

        self.experiments = exps
        return exps

    def load(self, dir:str):
        file   = os.path.join(dir, "docker.json")

        with open(file, 'r') as f: 
            schema = json.load(f)

        self.map[schema["addrs"][0]] = "M_0"
        for i,addr in enumerate(schema["addrs"][1:]):
            name = f"W_{i}"
            self.map[addr] = name

        return schema

    def sort(self):
        for i, ex in enumerate(self.experiments):
            exp = Experiment()
            p = None
            for _, ev in enumerate(ex):
                if "RUN" in ev:
                    v = ev["RUN"]
                    exp.data["name"]       = v["name"]
                    exp.data["strategy"]   = v["strategy"]
                    exp.data["params"]     = v["params"]
                    exp.data["tree"]       = v["tree"]

                if "POOL" in ev:
                    v = ev["POOL"]
                    if len(exp.data["stages"]) == 0:
                        exp.data["pool"].extend([ p.split(":")[0] for p in v ])
                        p = Pool(exp.data["pool"], 1, 1)
                    else:
                        assert(p.get() == [n.split(":")[0] for n in v])

                if "BUILD" in ev:
                    v = ev["BUILD"]
                    root = v["root"].split(":")[0]
                    key = v["key"]
                    data   = v["data"] if "data" in v else []
                    params = v["parameters"]
                    select = v["selected"]
                    pool = p.get() 
                    p.n_remove([ a.split(":")[0] for a in v["selected"] ])

                    exp.stage(root, key, data, params, select, pool)

                if "TREE" in ev:
                    v = ev["TREE"]
                    exp.data["tree"]["nodes"] = [ n.split(":")[0] for n in v["nodes"] ]

                if "PERF" in ev:
                    v = ev["PERF"]
                    root = v["root"].split(":")[0]
                    key = v["key"]
                    data   = v["data"]
                    params = v["parameters"]
                    select = v["selected"]
                    exp.performance(root, key, data, params, select)

            self.experiments[i]  = exp
