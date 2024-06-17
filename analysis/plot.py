import networkx as nx 
import matplotlib.pyplot as plt

from matplotlib.table import table
from networkx.drawing.nx_agraph import graphviz_layout

class Plotter():
    def __init__(self, map:dict):
        self.map = map
        pass

    def name(self, addr:str):
        return self.map[addr]

    def stages(self, run:dict, dir:str):
        name    = run["run"]["name"]
        root    = run["root"]
        depth   = run["tree"]["depth"]
        fanout  = run["tree"]["fanout"]

        G = nx.DiGraph()
        G.add_node(self.name(root))
        
        for i,stage in enumerate(run["stages"]):
            map      = []
            parent   = self.name(stage["parent"])
            children = [ self.name(a["addr"].split(":")[0]) for a in stage["selected"] ]
        
            for child in children:
                G.add_edge(parent, child) 
        
            for node in G:
                if node == self.name(root):
                    map.append('blue')
                elif any(node == child for child in children):
                    map.append('red')
                else: 
                    map.append('blue')
        
            # figure and subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
            # graph
            pos = graphviz_layout(G, prog="dot")
            nx.draw(G, pos, node_color=map, node_size=1000, with_labels=True, ax=ax1)
            ax1.set_title(f"Tree[{name}] - Stage {i}")
            ax2.axis('off')
        
            # table
            data = []
            for d in stage["data"]:
                row = []
                row.append(self.name(d["addr"].split(":")[0]))
                row.append(d["perc"])
                row.append(d["recv"])
                data.append(row)
        
            tb      = table(ax2, 
                            colLabels=["Addr", "90(%)-OWD", "RECV"], 
                            cellText=data, 
                            cellLoc='left',
                            loc='center')
            tb.auto_set_font_size(False)
            tb.set_fontsize(8)
        
            plt.tight_layout()
            plt.savefig(f"{dir}/TREE-{name}-{i}.pdf", format="pdf")
            plt.close(fig)


