import os 
import signal
import shutil

import networkx as nx 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from matplotlib.table import table
from networkx.drawing.nx_agraph import graphviz_layout

from .analysis  import Analyzer
from manager    import Run, RunDict, ResultDict, KEYS, EXPRESSIONS

def rnd(val:float, precision:int=2):
    ret = val
    ret = round(ret, precision)
    ret = f"{ret}"
    return  ret

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
        self.red    = '#FF9999'
        self.blue   = '#99CCFF'
        self.grey   = '#CCCCCC' # #efe897

class Plotter():
    def __init__(self, A:Analyzer):
        self.A      = A
        self.pargs  = PlotArgs()

    def view(self, dir, command="feh -r"):
        def handler(s, f):
            print("\nProcess interrupted.")
            raise SystemExit(0)

        signal.signal(signal.SIGINT, handler)

        try:
            os.system(f"cd {dir} && {command}")

        except KeyboardInterrupt:
            print("Exiting...")

    def subtitle(self, run:RunDict):
        ret  = ""
        name = run["name"]

        if "LEMON" in name: 
            epsilon = run["parameters"]["epsilon"]
            max_i   = run["parameters"]["max_i"]
            conv    = run["parameters"]["converge"]
            ret = f"EPS={epsilon}, MAX={max_i}, CONV={conv}"
        else:
            if run['strategy']['key'] == "heuristic":
                ret = f"Expr: (0.7 x stddev) + (0.3 * p90)"

        return ret

    def draw_subtitle(self, text:str, ax, pad:int=0):
        ax.set_title(f"{text}", fontsize=self.pargs.tfont - 2, fontweight='bold', pad=pad)

    def draw_graph(self, G, ax, cmap=None, emap=None):
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

    def comparison_table(self, data1:RunDict, data2:RunDict, ax, iter1, iter2):
        rate        = data1['parameters']["rate"]
        dur         = data1['parameters']["duration"]
        total       = rate * dur

        sel1 = self.A.map(data1["perf"][iter1]["selected"][0])
        sel2 = self.A.map(data2["perf"][iter2]["selected"][0])

        clabels  = ["90(%)-OWD", "50(%)-OWD", "STDDEV", "RX(%)"]
        rlabels1    = [ self.A.map(d["addr"]) for d in data1["perf"][iter1]["items"] ]
        rlabels2    = [ self.A.map(d["addr"]) for d in data2["perf"][iter2]["items"] ]

        cellcolors1  = [ ['white'] * len(clabels) for _ in range(len(rlabels1)) ]
        cellcolors2  = [ ['white'] * len(clabels) for _ in range(len(rlabels1)) ]

        cells1 = []
        cells2 = []

        for i,(d1,d2) in enumerate(zip(data1["perf"][iter1]["items"], data2["perf"][iter2]["items"])):
            addr1 = self.A.map(d1["addr"])
            addr2 = self.A.map(d2["addr"])

            perc1 = 100 * (float(d1["recv"]/total))
            cells1.append([ d1["p90"], 
                            d1["p50"], 
                            rnd(d1['stddev']),
                            rnd(perc1)])

            perc2 = 100 * (float(d2["recv"]/total))
            cells2.append([ d2["p90"], 
                            d2["p50"], 
                            rnd(d2['stddev']),
                            rnd(perc2)])

            if addr1 == sel1:
                cellcolors1[i][KEYS.index("p90")] = self.pargs.blue

            if addr2 == sel2:
                cellcolors2[i][KEYS.index("p90")] = self.pargs.red

        gap = 0.05
        tw = (1 - gap) / 2
        th1 = ( 0.095 * (len(rlabels1)) )
        th2 = ( 0.095 * (len(rlabels2)) )

        tb1 = table(ax, 
                    colLabels=clabels, 
                    cellColours=cellcolors1, 
                    rowLabels=rlabels1, 
                    cellText=cells1, 
                    cellLoc='left',
                    loc='top',
                    bbox=[0, 0.6 - th1, tw, th1])

        tb11 = table(ax, 
                    colLabels=[
                        f"BUILD", 
                        f"CONVERGENCE", 
                        f"EVALUATION[{iter1}]",
                        f"TOTAL"
                    ], 
                    cellText=[[
                        f"{rnd(data1['timers']['build'], 2)}s",
                        f"{rnd(data1['timers']['convergence'], 6)}s",
                        f"{rnd(data1['timers']['perf'][iter1], 2)}s",
                        f"{rnd(data1['timers']['total'], 2)}s",
                    ]],
                    cellLoc='left',
                    loc='top',
                    bbox=[0, 0.6 - th1 - 0.2, tw, (0.095 * 2)])

        tb2 = table(ax, 
                    colLabels=clabels, 
                    cellColours=cellcolors2, 
                    rowLabels=rlabels2, 
                    cellText=cells2, 
                    cellLoc='left',
                    loc='top',
                    bbox=[tw + gap, 0.6 - th2, tw, th2])
                    # left bottom width height

        tb12 = table(ax, 
                    colLabels=[
                        f"BUILD", 
                        f"CONVERGENCE", 
                        f"EVALUATION[{iter2}]", 
                        f"TOTAL"
                    ], 
                    cellText=[[
                        f"{rnd(data2['timers']['build'], 2)}s",
                        f"{rnd(data2['timers']['convergence'], 6)}s",
                        f"{rnd(data2['timers']['perf'][iter2], 2)}s",
                        f"{rnd(data2['timers']['total'], 2)}s",
                    ]],
                    cellLoc='left',
                    loc='top',
                    bbox=[tw + gap, 0.6 - th2 - 0.2, tw, (0.095 * 2)])

        tb1.auto_set_font_size(False)
        tb1.set_fontsize(self.pargs.font + 5)

        tb11.auto_set_font_size(False)
        tb11.set_fontsize(self.pargs.font + 5)

        tb12.auto_set_font_size(False)
        tb12.set_fontsize(self.pargs.font + 5)

        tb2.auto_set_font_size(False)
        tb2.set_fontsize(self.pargs.font + 5)

    def performance_table(self, run:RunDict, result:ResultDict, ax, iter):
        key      = "p90"
        rate     = run['parameters']['rate']
        duration = run['parameters']['duration']
        total    = rate * duration
        data     = []

        sel     = [ self.A.map(s) for s in result["selected"] ]

        clabels  = ["SCORE", "90(%)-OWD", "50(%)-OWD", "STDDEV", "RX(%)"]
        rlabels  = [ self.A.map(d["addr"]) for d in result["items"] ]

        rowcolors   = ['white'] * len(result["items"])
        colcolors   = ['white'] * len(clabels)
        cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]

        for i,d in enumerate(result["items"]):
            addr = rlabels[i]
            score = EXPRESSIONS[key](d)

            if addr in sel:
                if key in KEYS:
                    cellcolors[i][0] = self.pargs.red
                    cellcolors[i][KEYS.index(key) + 1] = self.pargs.red
                elif key == "heuristic":
                    cellcolors[i][0] = self.pargs.red
                    cellcolors[i][1] = self.pargs.red
                    cellcolors[i][-3] = self.pargs.red
                elif key == "NONE":
                    cellcolors[i][0] = self.pargs.red
                    cellcolors[i][1] = self.pargs.red

            perc = 100 * (float(d["recv"]/total))
            data.append([ rnd(float(score)),
                          d["p90"], 
                          d["p50"], 
                          rnd(d['stddev']),
                          rnd(perc)])

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


    def result_table(self, run:RunDict, result:ResultDict, ax):
        key      = run["strategy"]["key"]
        rate     = run['parameters']['rate']
        duration = run['parameters']['duration']
        total    = rate * duration
        data     = []

        sel      = [ self.A.map(s) for s in result["selected"] ]
        clabels  = ["SCORE", "90(%)-OWD", "50(%)-OWD", "STDDEV", "RX(%)"]
        rlabels  = [ self.A.map(d["addr"]) for d in result["items"] ]

        rowcolors   = ['white'] * len(result["items"])
        colcolors   = ['white'] * len(clabels)
        cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]

        for i,d in enumerate(result["items"]):
            addr = rlabels[i]
            score = EXPRESSIONS[key](d)

            if addr in sel:
                if key in KEYS:
                    cellcolors[i][0] = self.pargs.blue
                    cellcolors[i][KEYS.index(key) + 1] = self.pargs.red
                elif key == "heuristic":
                    cellcolors[i][0] = self.pargs.blue
                    cellcolors[i][KEYS.index("p90")    + 1] = self.pargs.red
                    cellcolors[i][KEYS.index("stddev") + 1] = self.pargs.red

            perc = 100 * (float(d["recv"]/total))
            data.append([ rnd(float(score)),
                          d["p90"], 
                          d["p50"], 
                          rnd(d['stddev']),
                          rnd(perc)])

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
        G.add_node(self.A.map(R.data['tree']['root']))

        cloud    = self.A.schema['infra'].upper()

        for i,result in enumerate(run["stages"]):
            G.name = f"{R.data['name']}-STAGE-{i}"

            name     = R.data['name']
            key      = R.data['strategy']['key']
            rate     = R.data['parameters']['rate']
            duration = R.data['parameters']['duration']
            K        = R.data['parameters']['hyperparameter']
            total    = rate * duration
            root     = self.A.map(R.data['tree']['root'])
            depth    = R.data['tree']['depth']
            fanout   = R.data['tree']['fanout']

            P        = len(R.pool.get())
            pool     = self.A.pool([self.A.map(p) for p in R.pool.get()])
            parent   = self.A.map(result["root"])
            children = [self.A.map(s) for s in result["selected"]]
            cmap     = ([self.pargs.blue] * len(G.nodes())) + ([self.pargs.red] * len(children))
        
            for child in children:
                G.add_edge(parent, child) 

            # figure and subplots
            # fig, ax1 = plt.subplots(figsize=(self.pargs.w, self.pargs.h))
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.pargs.w, self.pargs.h))
            title = fig.suptitle(f"{name} Tree - Stage {i + 1}/{len(run['stages'])} - D={depth}, F={fanout}, K={K}, KEY={key}, P={P}, {cloud}", fontsize=self.pargs.tfont, fontweight='bold')
            ax1.axis("off")
            ax2.axis("off")

            # self.draw_subtitle(f"ROOT: {root}", ax1, pad=-5)
            subtitle = self.subtitle(run)
            if subtitle: self.draw_subtitle(f"{subtitle}", ax2)

            # table
            self.result_table(R.data, result, ax1)

            # graph
            self.draw_graph(G, ax2, cmap)

            handles = [
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Total: {total} packets"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Rate: {rate} packets/sec"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Measurement: {duration}sec"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Stage: {rnd(run['timers']['stages'][i], 4)}sec"),
            ]

            plt.legend(handles = handles,
                       loc='upper right', 
                       fancybox=True, 
                       fontsize=self.pargs.font + 3)

            # plt.tight_layout()
            yield plt,fig

    def performance(self, G, run:RunDict, perf:ResultDict, iter:int):
        R = Run(run, run['tree']['root'], [ p.split(":")[0] for p in run['pool'] ], 1)

        name     = R.data['name']
        key      = R.data['strategy']['key']
        params   = R.data['parameters']
        rate     = R.data['parameters']['rate']
        duration = R.data['parameters']['duration']
        K        = R.data['parameters']['hyperparameter']
        P        = len(R.pool.get())
        total    = rate * duration
        root     = self.A.map(R.data['tree']['root'])
        depth    = R.data['tree']['depth']
        fanout   = R.data['tree']['fanout']
        N        = R.data['tree']['n']
        cloud    = self.A.schema['infra'].upper()
        sel      = [self.A.map(s) for s in perf["selected"]]
        cmap     = ([self.pargs.blue] * len(G.nodes()))

        for i,node in enumerate(G.nodes()):
            if node in sel:
                cmap[i] = self.pargs.red

        # fig, ax1 = plt.subplots(figsize=(self.pargs.w, self.pargs.h))
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.pargs.w, self.pargs.h))
        title = fig.suptitle(f"{name} Tree - Performance[i={iter}] - N={N}, D={depth}, F={fanout}, K={K}, KEY={key}, P={P}, {cloud}", fontsize=self.pargs.tfont, fontweight='bold')
        ax1.axis("off")
        ax2.axis("off")

        # self.draw_subtitle(f"ROOT: {root}", ax1, pad=-5)
        subtitle = self.subtitle(run)
        if subtitle: self.draw_subtitle(f"{subtitle}", ax2)

        # gs = fig.add_gridspec(2, 1, height_ratios=[0.6, 0.4])  # 60% for the first subplot, 40% for the second
        # ax1 = fig.add_subplot(gs[0])
        # ax2 = fig.add_subplot(gs[1])

        # table
        self.performance_table(run, perf, ax1, iter)

        # graph
        self.draw_graph(G, ax2, cmap)

        handles = [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Total: {total} packets"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Rate: {rate} packets/sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Measurement: {duration}sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Build: {rnd(run['timers']['build'], 4)}sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Evaluation: {rnd(run['timers']['perf'][iter - 1], 4)}sec"),
        ]
        

        if R.data['name'] == "LEMON":
            h = plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Conv: {rnd(run['timers']['convergence'], 4)}sec")
            handles.append(h)

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

    def comparison(self, G1, G2, data1, data2, iter1, iter2):
        cmap1 = ([self.pargs.blue] * len(G1.nodes()))
        cmap2 = ([self.pargs.red] *  len(G2.nodes()))

        cloud    = self.A.schema['infra'].upper()
        depth    = data1['tree']['depth']
        fanout   = data1['tree']['fanout']
        root1    = self.A.map(data1['tree']['root'])
        root2    = self.A.map(data2['tree']['root'])
        N        = data1['tree']['n']
        K        = data1['parameters']['hyperparameter']
        P        = len(data1['pool'])

        for i, (n1, n2) in enumerate(zip(G1.nodes(), G2.nodes())):
            if n1 == n2:
                cmap1[i] = self.pargs.grey
                cmap2[i] = self.pargs.grey

        # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(int(self.pargs.w * 1.5), self.pargs.h))
        fig = plt.figure(figsize=(int(self.pargs.w), self.pargs.h))
        title = fig.suptitle(f"Tree(s): {G1.name} x {G2.name} - N={N}, D={depth}, F={fanout}, K={K}, P={P}, {cloud}", fontsize=self.pargs.tfont, fontweight='bold')
        gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 0.7])
        gs_graphs = gs[1].subgridspec(1, 2)


        ax_t = fig.add_subplot(gs[0])
        ax_t.axis('off')

        ax1  = fig.add_subplot(gs_graphs[0])
        ax2  = fig.add_subplot(gs_graphs[1]) 

        ax1.axis('off')
        ax2.axis('off')

        # self.draw_subtitle(f"ROOT: {root1}", ax1, pad=5)
        # self.draw_subtitle(f"ROOT: {root2}", ax2, pad=5)

        self.comparison_table(data1, data2, ax_t, iter1, iter2)
        self.draw_graph(G1, ax1, cmap1, 'black')
        self.draw_graph(G2, ax2, cmap2, 'black')

        sub1 = self.subtitle(data1)
        if sub1: name1 = f"{G1.name} {sub1}"
        else:    name1 = f"{G1.name}"

        sub2 = self.subtitle(data2)
        if sub2: name2 = f"{G2.name} {sub2}"
        else:    name2 = f"{G2.name}"

        handles = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.pargs.blue,  markersize=10, label=f"{name1}"),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.pargs.red,   markersize=10, label=f"{name2}"),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.pargs.grey, markersize=10,  label=f"COMMON"),
        ]

        fig.legend(handles=handles,  loc='center', fontsize=self.pargs.font)

        plt.tight_layout()
        return plt, fig

    def plot(self, dir:str, view:bool=False):
        dir = os.path.join(dir, "plot")
        if os.path.isdir(dir): shutil.rmtree(dir)
        os.mkdir(dir)

        runs  = []
        trees = []
        self.pargs = PlotArgs(w=28, 
                              h=16, 
                              f=16, 
                              nf=18, 
                              tf=24, 
                              s=2100,)

        for run in self.A.runs:
            name = run["name"]
            key  = run["strategy"]["key"]
            root = self.A.map(run["tree"]["root"])

            print(f"PLOTTING TREE[{name}:{key}:{root}]")

            # plot build stages
            for i,(plt,fig) in enumerate(self.stages(run)):
                plt.savefig(f"{dir}/TREE-{name}-{key}-{root}-STAGE{i + 1}.png", format="png")
                plt.close(fig)
                print(f"PLOTTING TREE[{name}:{key}:{root}] STAGE[{i + 1}]")

            # plot tree performance
            print(f"PLOTTING TREE[{name}:{key}] PERF")

            G = self.A.graph(run)
            for i, perf in enumerate(run["perf"]):
                plt,fig = self.performance(G, run, perf, i + 1)

                n = name
                if "LEMON" in n:
                    epsilon = run["parameters"]["epsilon"]
                    max_i   = run["parameters"]["max_i"]
                    n  = f"{n}x{epsilon}x{max_i}"

                plt.savefig(f"{dir}/TREE-{n}-{key}-{root}-PERF-{i}.png", format="png")
                plt.close(fig)

            trees.append(G)
            runs.append(run)

        k = 0
        total = ( (len(trees) * (len(trees) - 1) ) / 2 )
        # plot tree comparisons
        for i in range(len(trees)):
            for j in range(i + 1, len(trees)):
                print(f"PLOTTING COMPARISON[{trees[i].name}x{trees[j].name}] {k + 1}/{total}")
                iter_i, iter_j  = self.A.worst(runs[i]["perf"], runs[j]["perf"])
                name_i          = trees[i].name.upper()
                name_j          = trees[j].name.upper()
                root_i          = self.A.map(runs[i]["tree"]["root"])
                root_j          = self.A.map(runs[j]["tree"]["root"])
                params_i        = runs[i]["parameters"]
                params_j        = runs[j]["parameters"]
                key_i           = runs[i]["strategy"]["key"]
                key_j           = runs[j]["strategy"]["key"]
                k += 1

                if "LEMON" in name_i:
                    name_i  = f"{name_i}x{params_i['epsilon']}x{params_i['max_i']}"

                if "LEMON" in name_j:
                    name_j  = f"{name_i}x{params_j['epsilon']}x{params_j['max_i']}"
                
                # if key_i != key_j: continue
                plt,fig = self.comparison(trees[i], trees[j], runs[i], runs[j], iter_i, iter_j)
                plt.savefig(f"{dir}/TREE-{name_i}-{name_j}-{root_i}x{root_j}-{key_i}-{key_j}-CMP.png")
                plt.close(fig)

        if view: 
            print(f"VIEWING IMAGES")
            self.view(dir)
