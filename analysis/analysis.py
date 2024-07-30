import networkx as nx 

from manager import RunDict, ResultDict
from typing import List

class Analyzer():
    def __init__(self, runs:List[RunDict], schema:dict, map:dict):
        self.runs   = runs
        self.schema = schema
        self.M      = map

    def map(self, addr:str):
        return self.M[addr.split(":")[0]]

    def name(self, addr:str):
        idx = self.schema["addrs"].index(addr.split(":")[0])
        return self.schema["names"][idx]

    def descr(self, run:RunDict):
        ret  = ""
        name = run["name"]

        if "LEMON" in name: 
            epsilon = run["parameters"]["epsilon"]
            max_i   = run["parameters"]["max_i"]
            conv    = run["parameters"]["converge"]
            ret     = f"EPS={epsilon}, MAX={max_i}, CONV={conv}"
        else:
            if run['strategy']['key'] == "heuristic":
                ret = f"Expr: (0.7 x stddev) + (0.3 * p90)"

        return ret

    def worst(self, lperf:List[ResultDict]):
        i       = 0 
        max     = 0

        for idx, result in enumerate(lperf):
            latency = result["items"][0]["p90"]
            if latency > max: 
                max = latency
                i   = idx

        return i

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
        G       = nx.DiGraph()

        name    = run['name']
        root    = run["tree"]["root"]
        key     = run['strategy']['key']

        if   "LEMON" in name: G.name = f"{name}"
        elif name == "RAND":  G.name = f"{name}"
        else:                 G.name = f"{name}-{key}"

        G.add_node(self.map(root))

        if len(run['stages']) > 0:
            for i, result in enumerate(run['stages']):
                parent   = self.map(result['root'])
                children = [ self.map(s) for s in result['selected'] ]
            
                for child in children:
                    G.add_edge(parent, child) 

        else:
            parents = [ self.map(root) ]
            nodes   = run['tree']['nodes'][1:]
            
            for i in range(0, len(nodes), run['tree']['fanout']):
                p = parents[0]
                parents.pop(0)
            
                for j in range(run['tree']['fanout']):
                    child = self.map(nodes[i + j])
                    G.add_edge(p, child) 
                    parents.append(child)

        return G
