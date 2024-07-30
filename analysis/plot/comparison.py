import matplotlib
import matplotlib.pyplot as plt

from matplotlib.table import table

from ..analysis import Analyzer
from ..utils    import rnd

from manager    import RunDict, ResultDict, KEYS, EXPRESSIONS

from .draw      import draw_subtitle, draw_graph
from .args      import pargs

def comparison(G1, G2, data1:RunDict, data2:RunDict, A:Analyzer, dir:str, file:str):
    # meta
    name_1          = G1.name.upper()
    name_2          = G2.name.upper()
    key_1           = data1["strategy"]["key"]
    key_2           = data2["strategy"]["key"]
    root_1          = A.map(data1["tree"]["root"])
    root_2          = A.map(data2["tree"]["root"])

    rate     = data1['parameters']['rate']
    duration = data1['parameters']['duration']
    total    = data1['parameters']['rate'] * data1['parameters']['duration']
    K        = data1['parameters']['hyperparameter']
    cloud    = A.schema['infra'].upper()
    iter1    = A.worst(data1["perf"])
    iter2    = A.worst(data2["perf"])

    # pool
    P        = len(data1['pool'])

    # tree
    depth    = data1['tree']['depth']
    fanout   = data1['tree']['fanout']
    root1    = A.map(data1['tree']['root'])
    root2    = A.map(data2['tree']['root'])
    N        = data1['tree']['n']

    cmap1 = ([pargs.blue] * len(G1.nodes()))
    cmap2 = ([pargs.red] *  len(G2.nodes()))


    for i, (n1, n2) in enumerate(zip(G1.nodes(), G2.nodes())):
        if n1 == n2:
            cmap1[i] = pargs.grey
            cmap2[i] = pargs.grey

    fig = plt.figure(figsize=(int(pargs.w), pargs.h))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 0.7])
    gs_graphs = gs[1].subgridspec(1, 2)

    ax_t = fig.add_subplot(gs[0])
    ax1  = fig.add_subplot(gs_graphs[0])
    ax2  = fig.add_subplot(gs_graphs[1]) 

    fig.suptitle(f"Tree(s): {G1.name} x {G2.name} - N={N}, D={depth}, F={fanout}, K={K}, P={P}, {cloud}", fontsize=pargs.tfont, fontweight='bold')
    ax_t.set_title(f"ROOTS: {root1} x {root2}", fontsize=pargs.tfont - 2, fontweight='bold',  y = 0.9)

    ax_t.axis('off')
    ax1.axis('off')
    ax2.axis('off')

    # table
    sel1        = A.map(data1["perf"][iter1]["selected"][0])
    sel2        = A.map(data2["perf"][iter2]["selected"][0])
    clabels     = ["90(%)-OWD", "50(%)-OWD", "STDDEV", "RX(%)"]
    rlabels1    = [ A.map(d["addr"]) for d in data1["perf"][iter1]["items"] ]
    rlabels2    = [ A.map(d["addr"]) for d in data2["perf"][iter2]["items"] ]
    cellcolors1 = [ ['white'] * len(clabels) for _ in range(len(rlabels1)) ]
    cellcolors2 = [ ['white'] * len(clabels) for _ in range(len(rlabels1)) ]
    cells1      = []
    cells2      = []

    for i,(d1,d2) in enumerate(zip(data1["perf"][iter1]["items"], data2["perf"][iter2]["items"])):
        addr1 = A.map(d1["addr"])
        addr2 = A.map(d2["addr"])

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

        if addr1 == sel1: cellcolors1[i][KEYS.index("p90")] = pargs.blue
        if addr2 == sel2: cellcolors2[i][KEYS.index("p90")] = pargs.red

    gap = 0.05
    tw = (1 - gap) / 2
    th1 = ( 0.095 * (len(rlabels1)) )
    th2 = ( 0.095 * (len(rlabels2)) )

    tb1 = table(ax_t, 
                colLabels=clabels, 
                cellColours=cellcolors1, 
                rowLabels=rlabels1, 
                cellText=cells1, 
                cellLoc='left',
                loc='top',
                bbox=[0, 0.6 - th1, tw, th1])

    tb11 = table(ax_t, 
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

    tb2 = table(ax_t, 
                colLabels=clabels, 
                cellColours=cellcolors2, 
                rowLabels=rlabels2, 
                cellText=cells2, 
                cellLoc='left',
                loc='top',
                bbox=[tw + gap, 0.6 - th2, tw, th2])
                # left bottom width height

    tb12 = table(ax_t, 
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
    tb1.set_fontsize(pargs.font + 5)
    tb11.auto_set_font_size(False)
    tb11.set_fontsize(pargs.font + 5)
    tb12.auto_set_font_size(False)
    tb12.set_fontsize(pargs.font + 5)
    tb2.auto_set_font_size(False)
    tb2.set_fontsize(pargs.font + 5)

    draw_graph(G1, ax1, cmap1, 'black')
    draw_graph(G2, ax2, cmap2, 'black')

    sub1 = A.descr(data1)
    if sub1: name1 = f"{G1.name} {sub1}"
    else:    name1 = f"{G1.name}"

    sub2 = A.descr(data2)
    if sub2: name2 = f"{G2.name} {sub2}"
    else:    name2 = f"{G2.name}"

    handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=pargs.blue,  markersize=10, label=f"{name1}"),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=pargs.red,   markersize=10, label=f"{name2}"),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=pargs.grey, markersize=10,  label=f"COMMON"),
    ]

    if "LEMON" in name_1:
        name_1  = f"{name_1}x{data1['parameters']['epsilon']}x{data1['parameters']['max_i']}"
    
    if "LEMON" in name_2:
        name_2  = f"{name_2}x{data2['parameters']['epsilon']}x{data2['parameters']['max_i']}"

    fig.legend(handles=handles,  loc='center', fontsize=pargs.font)
    plt.tight_layout()
    plt.savefig(f"{dir}/{file}.png")
    # plt.close('all')
    # plt.clf()
    # del fig 
    # ax_t.clear()
    # ax1.clear()
    # ax2.clear()
    # del ax_t
    # del ax1 
    # del ax2 
