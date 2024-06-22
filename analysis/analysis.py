import os 
import signal
import shutil

import networkx as nx 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from matplotlib.table import table
from networkx.drawing.nx_agraph import graphviz_layout

from .parse  import Parser
from manager import Run, RunDict, ResultDict, KEYS

class Analyzer():
    def __init__(self, parser):
        self.parser = parser

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
        G.add_node(self.parser.map[root])
        for i, result in enumerate(run['stages']):
            parent   = self.parser.map[result['root'].split(":")[0]]
            children = [ self.parser.map[s.split(':')[0]] for s in result['selected'] ]
        
            for child in children:
                G.add_edge(parent, child) 

        return G
