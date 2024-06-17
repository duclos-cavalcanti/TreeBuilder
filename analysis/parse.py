import os
import json
import shutil
import ipdb

from typing import List
from manager import Pool

from .plot import Plotter

class Parser():
    def __init__(self, dir:str):
        self.map        = {}
        self.events     = self.read(dir)
        self.schema     = self.load(dir)
        self.runs       = self.sort()
        self.plotter    = Plotter(map=self.map)

        assert(len(self.runs) == len(self.schema["runs"]))

    def read(self, dir:str):
        file = os.path.join(dir, "events.log")
        events = []
        with open(file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    events.append(event)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {line.strip()} - {e}")

        return events

    def load(self, dir:str):
        file   = os.path.join(dir, "docker.json")
        with open(file, 'r') as f: schema = json.load(f)

        for i,addr in enumerate(schema["addrs"][1:]):
            name = f"W_{i}"
            if len(name) < 4: name.ljust(1)
            self.map[addr] = name

        return schema

    def sort(self):
        i   = 0
        d   = {}
        p   = None
        ret = []
        while i < len(self.events):
            ev = self.events[i]
            for k,v in ev.items():
                if k == "RUN":
                    d["run"] = v
                    d["root"] = v["tree"]["root"].split(":")[0]
                    break

                if k == "POOL":
                    if "perf" in d: 
                        d["final"]   = [ p.split(":")[0] for p in v ]
                        c = d.copy()
                        d = {}
                        ret.append(c) 
                    else:
                        d["pool"]   = [ p.split(":")[0] for p in v ]
                        d["stages"] = []
                        p = Pool(d["pool"], 1, 1)

                    break

                if k == "BUILD":
                    if p is None or d == {}: raise RuntimeError("Parsing gone wrong")
                    stage = {}
                    stage["before"]   = p.get() 
                    stage["parent"]   = v["root"].split(":")[0]
                    stage["data"]     = v["data"] if "data" in v else []
                    stage["selected"] = v["selected"]

                    for a in  v["selected"]:
                        addr = a["addr"].split(":")[0]
                        p.remove(addr)

                    stage["after"]   = p.get() 
                    d["stages"].append(stage)
                    break

                if k == "TREE":
                    d["tree"] = v
                    d["tree"]["nodes"] = [ n.split(":")[0] for n in v["nodes"] ]
                    break

                if k == "PERF":
                    d["perf"] = v
                    break

                raise RuntimeError(f"KEY[{k}] IS UNKNOWN")

            i += 1

        return ret

    def plot(self, dir:str):
        dir = os.path.join(dir, "plot")
        if os.path.isdir(dir): shutil.rmtree(dir)
        os.mkdir(dir)

        for run in self.runs:
            if run["run"]["name"] == "RAND": continue
            self.plotter.stages(run, dir)

def parse(dir:str):
    P = Parser(dir=os.path.join(dir, "logs"))
    P.plot(dir)
