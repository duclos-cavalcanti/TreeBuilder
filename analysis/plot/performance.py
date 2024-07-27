import matplotlib
import matplotlib.pyplot as plt

from matplotlib.table import table

from manager    import RunDict, ResultDict, KEYS, EXPRESSIONS
from ..analysis import Analyzer
from ..utils    import rnd

from .draw      import draw_subtitle, draw_graph
from .args      import pargs

def performance(G, run:RunDict, iter:int, A:Analyzer, dir:str):
    # meta
    name     = run['name']
    key      = run['strategy']['key']
    rate     = run['parameters']['rate']
    duration = run['parameters']['duration']
    total    = run['parameters']['rate'] * run['parameters']['duration']
    K        = run['parameters']['hyperparameter']
    result   = ResultDict(run["perf"][iter])
    cloud    = A.schema['infra'].upper()

    # pool
    P        = len(run['pool'])
    pool     = A.pool([ A.map(p) for p in run['pool'] ])

    # tree
    root     = A.map(run['tree']['root'])
    depth    = run['tree']['depth']
    fanout   = run['tree']['fanout']
    N        = run['tree']['n']

    sel      = [A.map(s) for s in result["selected"]]
    cmap     = ([pargs.blue] * len(G.nodes()))
    for i,node in enumerate(G.nodes()):
        if node in sel:
            cmap[i] = pargs.red

    # fig, ax1 = plt.subplots(figsize=(pargs.w, pargs.h))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(pargs.w, pargs.h))
    ax1.axis("off")
    ax2.axis("off")

    fig.suptitle(f"{name} Tree - Performance[i={iter + 1}] - N={N}, D={depth}, F={fanout}, K={K}, KEY={key}, P={P}, {cloud}", fontsize=pargs.tfont, fontweight='bold')
    ax1.set_title(f"ROOT: {root}", fontsize=pargs.tfont - 2, fontweight='bold',  y = 1.0)

    subtitle = A.descr(run)
    if subtitle: draw_subtitle(f"{subtitle}", ax2)

    # gs = fig.add_gridspec(2, 1, height_ratios=[0.6, 0.4])  # 60% for the first subplot, 40% for the second
    # ax1 = fig.add_subplot(gs[0])
    # ax2 = fig.add_subplot(gs[1])

    # table
    clabels     = ["SCORE", "90(%)-OWD", "50(%)-OWD", "STDDEV", "RX(%)"]
    rlabels     = [ A.map(d["addr"]) for d in result["items"] ]
    rowcolors   = ['white'] * len(result["items"])
    colcolors   = ['white'] * len(clabels)
    cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]
    data        = []

    for i,d in enumerate(result["items"]):
        addr = rlabels[i]
        score = EXPRESSIONS[key](d)

        if addr in sel:
            if key in KEYS:
                cellcolors[i][0] = pargs.red
                cellcolors[i][KEYS.index(key) + 1] = pargs.red
            elif key == "heuristic":
                cellcolors[i][0] = pargs.red
                cellcolors[i][1] = pargs.red
                cellcolors[i][-3] = pargs.red
            elif key == "NONE":
                cellcolors[i][0] = pargs.red
                cellcolors[i][1] = pargs.red

        perc = 100 * (float(d["recv"]/total))
        data.append([ rnd(float(score)),
                      d["p90"], 
                      d["p50"], 
                      rnd(d['stddev']),
                      rnd(perc)])

    th = ( 0.075 * (len(rlabels)) )
    tb = table(ax1, 
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

    tb.auto_set_font_size(False)
    tb.set_fontsize(pargs.font + 5)

    # graph
    draw_graph(G, ax2, cmap)

    handles = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Total: {total} packets"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Rate: {rate} packets/sec"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Measurement: {duration}sec"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Build: {rnd(run['timers']['build'], 4)}sec"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Evaluation: {rnd(run['timers']['perf'][iter], 4)}sec"),
    ]
    
    if "LEMON" in name:
        handles.append(plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Converged: {rnd(run['timers']['convergence'], 4)}sec"))

    plt.legend(handles = handles,
               loc='upper right', 
               fancybox=True, 
               fontsize=pargs.font + 3)

    suffix=""
    if "LEMON" in name:
        epsilon = run["parameters"]["epsilon"]
        max_i   = run["parameters"]["max_i"]
        suffix  = f"x{epsilon}x{max_i}"
    
    plt.savefig(f"{dir}/perf/TREE-{name}{suffix}-{key}-{root}-PERF-{iter + 1}.png", format="png")
    plt.close('all')
    plt.clf()
    del fig 
    ax1.clear()
    ax2.clear()
    del ax1 
    del ax2 

