import networkx as nx 

from manager import Run, RunDict
from typing import List

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
