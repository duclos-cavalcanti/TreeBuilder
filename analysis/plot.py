import os 
import shutil

import networkx as nx 
import matplotlib.pyplot as plt

from matplotlib.table import table
import matplotlib.image as mpimg

from networkx.drawing.nx_agraph import graphviz_layout

from .parse import Parser

class PlotArgs():
    def __init__(self, x:int=0, y:int=0, w:int=0, h:int=0, f:int=8, nf:int=0, tf:int=0, s:int=0):
        self.x      = x
        self.y      = y
        self.w      = w
        self.h      = h
        self.font   = f
        self.nfont  = nf
        self.tfont  = tf
        self.size   = s

class Plotter():
    def __init__(self, parser:Parser):
        self.parser    = parser
        self.selcolor  = '#FF9999'
        self.evalcolor = '#99CCFF'
        self.defcolor  = '#CCCCCC'
        self.cmpcolor  = '#efe897'

    def graph(self, exp:dict):
        root    = exp["tree"]["root"].split(":")[0]

        G = nx.DiGraph()
        G.add_node(self.parser.map[root])
        for _, stage in enumerate(exp["stages"]):
            parent  = self.parser.map[stage["root"]]
            children = [self.parser.map[s.split(":")[0]] for s in stage["selected"]]
        
            for child in children:
                G.add_edge(parent, child) 

        return G

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

    def table(self, stage:dict, ax, args):
        sel     = [self.parser.map[s.split(":")[0]] for s in stage["selected"]]
        key     = "p90" if not stage["key"] else stage["key"]
        idx     = -1
        data    = []
        colors  = []
        packets = stage["params"]["packets"]
        labels  = ["Node", "90(%)-OWD", "75(%)-OWD", "50(%)-OWD", "RX(%)"]
        values  = ["name", "p90", "p75", "p50", "recv"]

        for i,v in enumerate(values):
            if v == key:
                idx = i 
                break 

        if idx < 0: raise RuntimeError("Key not found")

        for d in stage["data"]:
            name = self.parser.map[d["addr"].split(":")[0]]
            row = [name, d["p90"], d["p75"], d["p50"], 100 * float(d["recv"]/packets)]
            data.append(row)

            c = [self.defcolor] * len(row)
            if name in sel: 
                c[idx] = self.selcolor

            colors.append(c)

        ret = table(ax, 
                    colLabels=labels, 
                    cellText=data, 
                    cellColours=colors,
                    cellLoc='left',
                    loc='bottom')

        ret.auto_set_font_size(False)
        ret.set_fontsize(args.font)
        return ret

    def stages(self, exp:dict, args):
        name    = exp["name"]
        root    = exp["tree"]["root"].split(":")[0]
        params =  exp['params']
        rate    = exp['params']["rate"]
        dur     = exp['params']["duration"]

        G = nx.DiGraph()
        G.add_node(self.parser.map[root])
        
        for i,stage in enumerate(exp["stages"]):
            pool    = self.pool([self.parser.map[p] for p in stage['pool']])
            parent  = self.parser.map[stage["root"]]
            children = [self.parser.map[s.split(":")[0]] for s in stage["selected"]]
            cmap     = ([self.evalcolor] * len(G.nodes())) + ([self.selcolor] * len(children))
        
            for child in children:
                G.add_edge(parent, child) 

            # figure and subplots
            fig, ax1 = plt.subplots(figsize=(args.w, args.h))
            fig.suptitle(f"Tree[{name}] - Stage {i}", fontsize=args.tfont)

            # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            # ax1.set_title(f"Tree[{name}] - Stage {i}")
            # ax2.axis('off')
        
            # graph
            pos = graphviz_layout(G, prog="dot")
            nx.draw(G, pos, node_color=cmap, node_size=args.size, with_labels=True, ax=ax1, font_size=args.nfont)

            # table
            self.table(stage, ax1, args)

            leg = plt.legend([plt.Line2D([0], 
                        [0], 
                        color='white')], 
                        [f"Pool: {pool}\nRate: {rate} packets/sec\nDur: {dur}sec\nPackets:{rate*dur}"], 
                       loc='upper right', 
                       frameon=True, 
                       fontsize=args.font + 3)

            leg.get_frame().set_facecolor(self.evalcolor)
            # plt.tight_layout()
            yield plt,fig

    def perf(self, G, exp:dict, args):
        name    = exp["name"]
        root    = exp["tree"]["root"].split(":")[0]
        depth   = exp["tree"]["depth"]
        fanout  = exp["tree"]["fanout"]
        sel     = [self.parser.map[s.split(":")[0]] for s in exp["perf"]["selected"]]
        params  =  exp['params']
        rate    = exp['params']["rate"]
        dur     = exp['params']["duration"]
        cmap    = ([self.evalcolor] * len(G.nodes()))

        for i,node in enumerate(G.nodes()):
            if node in sel:
                cmap[i] = self.selcolor

        fig, ax1 = plt.subplots(figsize=(args.w, args.h))
        fig.suptitle(f"Tree[{name}] - Performance", fontsize=args.tfont)

        # graph
        pos = graphviz_layout(G, prog="dot")
        nx.draw(G, pos, node_color=cmap, node_size=args.size, with_labels=True, ax=ax1, font_size=args.nfont)

        # table
        self.table(exp["perf"], ax1, args)

        leg = plt.legend([plt.Line2D([0], 
                        [0], 
                        color='white')], 
                         [f"Depth: {depth}\nFanout: {fanout}\nRate: {rate} packets/sec\nDur: {dur}sec\nPackets:{rate*dur}"], 
                       loc='upper right', 
                       frameon=True, 
                       fontsize=args.font + 3)

        leg.get_frame().set_facecolor(self.evalcolor)
        return plt, fig

    def merge(self, files, patt1, patt2, args):
        sel = []

        idx = next((i for i, f in enumerate(files) if "PERF" in f and patt1 in f ), -1)
        sel.append(files[idx])

        idx = next((i for i, f in enumerate(files) if "PERF" in f and patt2 in f ), -1)
        sel.append(files[idx])

        imgs = [mpimg.imread(f) for f in sel]
        fig, axs = plt.subplots(1, len(imgs), figsize=(args.w * len(imgs), args.h))

        for ax, image in zip(axs, imgs):
            ax.imshow(image)
            ax.axis('off')

        plt.tight_layout()
        return plt, fig 

    def compare(self, G1, G2, args):
        CG = nx.compose(G1, G2)
        
        # Color maps for nodes and edges
        node_colors = []
        edge_colors = []

        for node in CG.nodes():
            if node in G1 and node in G2:   node_colors.append('green')
            elif node in G1:                node_colors.append('blue')
            else:                           node_colors.append('red')

        for edge in CG.edges():
            if G1.has_edge(*edge) and G2.has_edge(*edge):   edge_colors.append('green')
            elif G1.has_edge(*edge):                        edge_colors.append('blue')
            else:                                           edge_colors.append('red')

        pos = graphviz_layout(CG, prog="dot")

        fig, ax = plt.subplots(figsize=(args.w, args.h))
        nx.draw(CG, pos, node_color=node_colors, edge_color=edge_colors, with_labels=True, ax=ax, node_size=args.size, font_size=args.nfont)
        
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='G1 Only'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='G2 Only'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Common')
        ]

        plt.legend(handles=legend_elements, loc='upper right', fontsize=args.font)
        # plt.tight_layout()
        return plt, fig

    def mirror(self, G1, G2, args):
        pos1 = graphviz_layout(G1, prog="dot")
        pos2 = graphviz_layout(G2, prog="dot")

        cmap1 = ([self.evalcolor] * len(G1.nodes()))
        cmap2 = ([self.selcolor] *  len(G2.nodes()))

        for i, (n1, n2) in enumerate(zip(G1.nodes(), G2.nodes())):
            if n1 == n2:
                cmap1[i] = self.cmpcolor
                cmap2[i] = self.cmpcolor

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(int(args.w * 1.5), args.h))

        nx.draw(G1, pos1, node_color=cmap1, edge_color='black', with_labels=True, ax=ax1, node_size=args.size, font_size=args.nfont)
        ax1.set_title('Tree BEST')

        nx.draw(G2, pos2, node_color=cmap2, edge_color='black', with_labels=True, ax=ax2, node_size=args.size, font_size=args.nfont)
        ax2.set_title('Tree WORST')

        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='G1'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='G2')
        ]
        fig.legend(handles=legend_elements, loc='upper center', fontsize=args.font)

        plt.tight_layout()
        return plt, fig

    def plot(self, dir:str):
        dir = os.path.join(dir, "plot")
        if os.path.isdir(dir): shutil.rmtree(dir)
        os.mkdir(dir)

        files = []
        args = PlotArgs(w=32, h=16, f=16, nf=18, tf=20, s=2100)

        BEST  = None
        WORST = None

        for exp in self.parser.experiments:
            name = exp.data["name"]
            print(f"PLOTTING TREE[{name}]")
            if name  != "RAND": 
                for i,(plt,fig) in enumerate(self.stages(exp.data, args)):
                    f = f"{dir}/TREE-{name}-STAGE-{i}.png"
                    plt.savefig(f"{dir}/TREE-{name}-{i}.png", format="png")
                    plt.close(fig)
                    files.append(f)

            f = f"{dir}/TREE-{name}-PERF.png"
            G = self.graph(exp.data)
            plt,fig = self.perf(G, exp.data, args)
            plt.savefig(f, format="png")
            plt.close(fig)
            files.append(f)

            if name == "BEST":  BEST = G 
            if name == "WORST": WORST = G

        plt,fig = self.mirror(BEST, WORST, args)
        plt.savefig(f"{dir}/TREE-BEST-WORST-CMP.png")
        plt.close(fig)
