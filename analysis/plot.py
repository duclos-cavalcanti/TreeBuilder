import os 
import signal
import shutil

import networkx as nx 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from matplotlib.table import table
from networkx.drawing.nx_agraph import graphviz_layout

from .parse     import Parser
from .analysis  import Analyzer
from manager    import Run, RunDict, ResultDict, KEYS, HMAP

class PlotArgs():
    def __init__(self, x:int=0, y:int=0, w:int=0, h:int=0, 
                       f:int=8, nf:int=0, tf:int=0, 
                       s:int=0):
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
        self.analyzer  = Analyzer(parser)
        self.red       = '#FF9999'
        self.blue      = '#99CCFF'
        self.grey      = '#CCCCCC' # #efe897
        self.pargs     = PlotArgs()

    def view(self, dir, command="feh -r"):
        def handler(s, frame):
            print("\nProcess interrupted.")
            raise SystemExit(0)

        signal.signal(signal.SIGINT, handler)

        try:
            os.system(f"cd {dir} && {command}")

        except KeyboardInterrupt:
            print("Exiting...")

    def draw_graph(self, G, ax, cmap=None, emap=None):
        # -Gnodesep=0.9 -Granksep=0.8
        # G.graph['rankdir'] = "LR"
        # A = nx.nx_agraph.to_agraph(G)
        # A.graph_attr.update(nodesep="4", ranksep="8")

        # for i,edge in enumerate(G.edges()):
        #     u = edge[0]
        #     v = edge[1]

        G.graph['rankdir'] = "TB"
        G.graph['ranksep'] = "0.03"

        A = nx.nx_agraph.to_agraph(G)
        A.layout(prog='dot')
        A.write(f"analysis/graphs/{G.name}.dot")

        pos = graphviz_layout(G, prog='dot')
        nx.draw(G, 
                pos, 
                node_color=cmap, 
                edge_color=emap,
                node_size=self.pargs.size, 
                with_labels=True, 
                ax=ax, 
                font_size=self.pargs.nfont)

        # plt.tight_layout()
        return pos

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

    def comparison_table(self, data1:RunDict, data2:RunDict, ax):
        rate        = data1['parameters']["rate"]
        dur         = data1['parameters']["duration"]
        packets     = rate * dur

        sel1 = self.parser.map[data1["perf"]["selected"][0].split(":")[0]]
        sel2 = self.parser.map[data2["perf"]["selected"][0].split(":")[0]]

        clabels     = ["90(%)-OWD", "75(%)-OWD", "50(%)-OWD", "RX(%)"]
        rlabels     = [ sel1, sel2 ]
        cellcolors  = [ ['white'] * len(clabels) for _ in range(len(rlabels)) ]

        data = [[],[]]

        for i,(d1,d2) in enumerate(zip(data1["perf"]["items"], data2["perf"]["items"])):
            addr1 = self.parser.map[d1["addr"].split(":")[0]]
            addr2 = self.parser.map[d2["addr"].split(":")[0]]

            if addr1 == sel1:
                # print(f"ADDR: {addr1} == {sel1}")
                data[0].extend([ d1["p90"], d1["p75"], d1["p50"], 100 * float(d1["recv"]/packets)])
                cellcolors[0][KEYS.index("p90")] = self.blue

            if addr2 == sel2:
                # print(f"ADDR: {addr2} == {sel2}")
                data[1].extend([ d2["p90"], d2["p75"], d2["p50"], 100 * float(d2["recv"]/packets)])
                cellcolors[1][KEYS.index("p90")] = self.red

        # print(f"ADDR: {rlabels}")
        # print(f"DATA: {data}")

        th = ( 0.095 * (len(rlabels)) )
        ret = table(ax, 
                    colLabels=clabels, 
                    cellColours=cellcolors, 
                    rowLabels=rlabels, 
                    cellText=data, 
                    cellLoc='left',
                    loc='top',
                    bbox=[0, 0.6 - th , 1, th])
                    # left bottom width height

        ret.auto_set_font_size(False)
        ret.set_fontsize(self.pargs.font + 5)


    def result_table(self, run:RunDict, result:ResultDict, ax):
        key      = run["strategy"]["key"]
        rate     = run['parameters']['rate']
        duration = run['parameters']['duration']
        total    = rate * duration
        data     = []

        sel     = [self.parser.map[s.split(":")[0]] for s in result["selected"]]

        clabels  = ["SCORE", "90(%)-OWD", "75(%)-OWD", "50(%)-OWD", "STDDEV", "RX(%)"]
        rlabels  = [ self.parser.map[d["addr"].split(":")[0]] for d in result["items"] ]

        rowcolors   = ['white'] * len(result["items"])
        colcolors   = ['white'] * len(clabels)
        cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]

        for i,d in enumerate(result["items"]):
            addr = rlabels[i]
            score = HMAP[key](d)

            if addr in sel:
                if key in KEYS:
                    cellcolors[i][0] = self.red
                    cellcolors[i][KEYS.index(key) + 1] = self.red
                else:
                    cellcolors[i][0] = self.red
                    cellcolors[i][KEYS.index("p90")    + 1] = self.red
                    cellcolors[i][KEYS.index("stddev") + 1] = self.red

            data.append([ score,
                          d["p90"], 
                          d["p75"], 
                          d["p50"], 
                          d["stddev"], 
                          100 * float(d["recv"]/total)])

        th = ( 0.075 * (len(rlabels)) )
        ret = table(ax, 
                    colLabels=clabels, 
                    colColours=colcolors, 
                    cellColours=cellcolors, 
                    rowLabels=rlabels, 
                    rowColours=rowcolors,
                    cellText=data, 
                    cellLoc='left',
                    loc='top',
                    bbox=[0, 1 - th , 1, th])
                    # left bottom width height

        ret.auto_set_font_size(False)
        ret.set_fontsize(self.pargs.font + 5)
        return ret

    def stages(self, run:RunDict):
        R = Run(run, run['tree']['root'], [ p.split(":")[0] for p in run['pool'] ], 1)
        G = nx.DiGraph()
        G.add_node(self.parser.map[R.data['tree']['root'].split(":")[0]])

        for i,result in enumerate(R.data["stages"]):
            G.name = f"{R.data['name']}-STAGE-{i}"

            name     = R.data['name']
            key      = R.data['strategy']['key']
            rate     = R.data['parameters']['rate']
            duration = R.data['parameters']['duration']
            total    = rate * duration
            depth    = R.data['tree']['depth']
            fanout   = R.data['tree']['fanout']

            pool     = self.pool([self.parser.map[p] for p in R.pool.get()])
            parent   = self.parser.map[result["root"].split(":")[0]]
            children = [self.parser.map[s.split(":")[0]] for s in result["selected"]]
            cmap     = ([self.blue] * len(G.nodes())) + ([self.red] * len(children))
        
            for child in children:
                G.add_edge(parent, child) 
                R.pool.remove(child)

            # figure and subplots
            # fig, ax1 = plt.subplots(figsize=(self.pargs.w, self.pargs.h))
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.pargs.w, self.pargs.h))
            fig.suptitle(f"{name} Tree - Iteration {i + 1}/{len(R.data['stages'])} - D={depth}, F={fanout}, KEY={key}", fontsize=self.pargs.tfont, fontweight='bold')
            ax1.axis("off")
            ax2.axis("off")

            # table
            self.result_table(R.data, result, ax1)

            # graph
            self.draw_graph(G, ax2, cmap)

            handles = [
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Rate: {rate}packets/sec"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Period: {duration}sec"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Total: {total} packets"),
            ]

            plt.legend(handles = handles,
                       loc='upper right', 
                       fancybox=True, 
                       fontsize=self.pargs.font + 3)

            # plt.tight_layout()
            yield plt,fig

    def performance(self, G, run:RunDict):
        R = Run(run, run['tree']['root'], [ p.split(":")[0] for p in run['pool'] ], 1)

        name     = R.data['name']
        key      = R.data['strategy']['key']
        rate     = R.data['parameters']['rate']
        duration = R.data['parameters']['duration']
        total    = rate * duration
        depth    = R.data['tree']['depth']
        fanout   = R.data['tree']['fanout']
        sel      = [self.parser.map[s.split(":")[0]] for s in run["perf"]["selected"]]
        cmap     = ([self.blue] * len(G.nodes()))

        for i,node in enumerate(G.nodes()):
            if node in sel:
                cmap[i] = self.red

        # fig, ax1 = plt.subplots(figsize=(self.pargs.w, self.pargs.h))
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.pargs.w, self.pargs.h))
        fig.suptitle(f"{name} Tree - Performance - D={depth}, F={fanout}, KEY={key}", fontsize=self.pargs.tfont, fontweight='bold')
        ax1.axis("off")
        ax2.axis("off")

        # gs = fig.add_gridspec(2, 1, height_ratios=[0.6, 0.4])  # 60% for the first subplot, 40% for the second
        # ax1 = fig.add_subplot(gs[0])
        # ax2 = fig.add_subplot(gs[1])

        # table
        self.result_table(run, run["perf"], ax1)

        # graph
        self.draw_graph(G, ax2, cmap)

        handles = [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Rate: {rate}packets/sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Period: {duration}sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Total: {total} packets"),
        ]
        
        plt.legend(handles = handles,
                   loc='upper right', 
                   fancybox=True, 
                   fontsize=self.pargs.font + 3)

        return plt, fig

    def merge(self, files):
        imgs = [mpimg.imread(f) for f in files]
        fig, axs = plt.subplots(1, len(imgs), figsize=(self.pargs.w * len(imgs), self.pargs.h))

        for ax, image in zip(axs, imgs):
            ax.imshow(image)
            ax.axis('off')

        plt.tight_layout()
        return plt, fig 

    def compare(self, G1, G2, data1, data2):
        cmap1 = ([self.blue] * len(G1.nodes()))
        cmap2 = ([self.red] *  len(G2.nodes()))

        for i, (n1, n2) in enumerate(zip(G1.nodes(), G2.nodes())):
            if n1 == n2:
                cmap1[i] = self.grey
                cmap2[i] = self.grey

        # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(int(self.pargs.w * 1.5), self.pargs.h))
        fig = plt.figure(figsize=(int(self.pargs.w * 1.2), self.pargs.h))
        fig.suptitle(f"Tree - Comparison {G1.name} x {G2.name}", fontsize=self.pargs.tfont, fontweight='bold')

        gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 0.7])
        gs_graphs = gs[1].subgridspec(1, 2)

        ax_t = fig.add_subplot(gs[0])
        ax_t.axis('off')

        ax1  = fig.add_subplot(gs_graphs[0])
        ax2  = fig.add_subplot(gs_graphs[1]) 

        self.comparison_table(data1, data2, ax_t)
        self.draw_graph(G1, ax1, cmap1, 'black')
        self.draw_graph(G2, ax2, cmap2, 'black')

        handles = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.blue,  markersize=10, label=f"{G1.name}"),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.red,   markersize=10, label=f"{G2.name}"),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.grey, markersize=10, label=f"COMMON")
        ]
        fig.legend(handles=handles, loc='center', fontsize=self.pargs.font)

        plt.tight_layout()
        return plt, fig

    def plot(self, dir:str, view:bool=False):
        dir = os.path.join(dir, "plot")
        if os.path.isdir(dir): shutil.rmtree(dir)
        os.mkdir(dir)

        data = []
        trees = []
        files = []
        self.pargs = PlotArgs(w=32, 
                              h=16, 
                              f=16, 
                              nf=18, 
                              tf=24, 
                              s=2100,)

        for run in self.parser.runs:
            print(f"PLOTTING TREE[{run['name']}]")

            name = run["name"]
            key  = run["strategy"]["key"]

            if name != "RAND":
                for i,(plt,fig) in enumerate(self.stages(run)):
                    f = f"{dir}/TREE-{name}-STAGE-{i}.png"
                    plt.savefig(f"{dir}/TREE-{name}-{key}-{i + 1}.png", format="png")
                    plt.close(fig)
                    files.append(f)

            if name == "RAND":
                continue

            G = self.analyzer.graph(run)
            f = f"{dir}/TREE-{name}-{key}-PERF.png"
            plt,fig = self.performance(G, run)
            plt.savefig(f, format="png")
            plt.close(fig)

            files.append(f)
            trees.append(G)
            data.append(run)

        for i in range(len(trees)):
            for j in range(i + 1, len(trees)):
                name_i = trees[i].name.upper()
                name_j = trees[j].name.upper()
                key1   = data[i]["strategy"]["key"]
                key2   = data[j]["strategy"]["key"]

                print(f"PLOTTING COMPARISON[{name_i}x{name_j}]")

                plt,fig = self.compare(trees[i], trees[j], data[i], data[j])
                plt.savefig(f"{dir}/TREE-{name_i}-{name_j}-CMP.png")
                plt.close(fig)


        if view: 
            print(f"VIEWING IMAGES")
            self.view(dir)

        return
