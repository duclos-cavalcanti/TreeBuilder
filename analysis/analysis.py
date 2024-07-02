import networkx as nx 
import numpy as np

import csv

from manager import Run, RunDict
from typing import List

class UDP():
    def __init__(self):
        pass

    def read(self, f:str):
        data = []
        name = f.split("/")[-1]
        name = name.split(".csv")[0]

        with open(f, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data.append(int(row[1]))
        
        return data, name

    def process(self, files:List):
        for f in files: 
            data, name = self.read(f)
            data = np.array(data)
            p90     = np.percentile(data, 90)
            p75     = np.percentile(data, 75)
            p50     = np.percentile(data, 50)
            p25     = np.percentile(data, 25)
            std_dev = np.std(data)

            print(f"RESULTS[{name}]:")
            print(f"p90: {p90}")
            print(f"p75: {p75}")
            print(f"p50: {p50}")
            print(f"p25: {p25}")
            print(f"dev: {std_dev}")
            print()

class Analyzer():
    def __init__(self, runs:List[RunDict], schema:dict, map:dict):
        self.runs   = runs
        self.schema = schema
        self.M      = map

    def map(self, addr:str):
        return self.M[addr.split(":")[0]]

    def pool(self, pool):
        spool = sorted([int(p.split('_')[1]) for p in pool])
        ret = []
        
        # Initialize the start of the range
        start = spool[0]
        end   = spool[0]

        for i in range(1, len(spool)):

            # If the current worker is consecutive, update the end
            if spool[i] == end + 1:
                end = spool[i]
            else:
                # If not consecutive, add the range to the result
                if start == end:    ret.append(f"{start}")
                else:               ret.append(f"{start} - {end}")
                start = spool[i]
                end   = spool[i]
        
        # Add the last range
        if start == end:    ret.append(f"{start}")
        else:               ret.append(f"{start} - {end}")
        
        return "[ " + ", ".join(ret) + " ]"

    def graph(self, run:RunDict):
        root    = run["tree"]["root"].split(":")[0]
        G = nx.DiGraph()
        G.name = f"{run['name']}-{run['strategy']['key']}"
        G.add_node(self.map(root))
        for i, result in enumerate(run['stages']):
            parent   = self.map(result['root'])
            children = [ self.map(s) for s in result['selected'] ]
        
            for child in children:
                G.add_edge(parent, child) 

        return G
