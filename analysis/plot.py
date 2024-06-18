import networkx as nx 
import matplotlib.pyplot as plt

from matplotlib.table import table
from networkx.drawing.nx_agraph import graphviz_layout

class Plotter():
    def __init__(self, map:dict):
        self.map = map
        self.selcolor  = '#FF9999'
        self.evalcolor = '#99CCFF'
        self.defcolor  = '#CCCCCC'

    def graph(self, G):
        pass

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

    def table(self, stage:dict, ax):
        pool  = [self.map[p] for p in stage['before']]
        eval  = [self.map[s["addr"].split(":")[0]] for s in stage["data"]]
        sel   = [self.map[s["addr"].split(":")[0]] for s in stage["selected"]]

        data   = []
        colors = []

        for d in stage["data"]:
            name = self.map[d["addr"].split(":")[0]]
            row = [name, d["perc"], d["recv"]]
            data.append(row)
            colors.append(self.selcolor if name in sel else self.evalcolor)

        # for pn in pool:
        #     if pn not in eval:
        #         row = [pn, "", ""]
        #         data.append(row)
        #         colors.append('white')

        ret = table(ax, 
                    colLabels=["Node", "90(%)-OWD", "RX(%)"], 
                    cellText=data, 
                    cellColours=[[c] * 3 for c in colors],
                    cellLoc='left',
                    loc='bottom')
        ret.auto_set_font_size(False)
        ret.set_fontsize(8)
        return ret

    def stages(self, run:dict):
        name    = run["run"]["name"]
        root    = run["root"]
        rate    = run['run']["params"]["rate"]
        dur     = run['run']["params"]["duration"]
        depth   = run["tree"]["depth"]
        fanout  = run["tree"]["fanout"]

        G = nx.DiGraph()
        G.add_node(self.map[root])
        
        for i,stage in enumerate(run["stages"]):
            pool    = [self.map[p] for p in stage['before']]
            parent  = self.map[stage["parent"]]
            children = [ self.map[a["addr"].split(":")[0]] for a in stage["selected"] ]
            cmap     = ([self.evalcolor] * len(G.nodes())) + ([self.selcolor] * len(children))
        
            for child in children:
                G.add_edge(parent, child) 

            # figure and subplots
            fig, ax1 = plt.subplots(figsize=(16, 8))
            fig.suptitle(f"Tree[{name}] - Stage {i}")

            # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            # ax1.set_title(f"Tree[{name}] - Stage {i}")
            # ax2.axis('off')
        
            # graph
            pos = graphviz_layout(G, prog="dot")
            nx.draw(G, pos, node_color=cmap, node_size=1000, with_labels=True, ax=ax1, font_size=8)

            # table
            self.table(stage, ax1)

            plt.legend([plt.Line2D([0], 
                        [0], 
                        color='white')], 
                       [f"Pool: {self.pool(pool)}\nRate: {rate} packets/sec\nDur: {dur}sec"], 
                       loc='upper right', 
                       frameon=False, 
                       fontsize=10)
            plt.tight_layout()
            yield plt,fig

