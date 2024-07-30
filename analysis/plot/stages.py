import networkx as nx 

import matplotlib
import matplotlib.pyplot as plt

from matplotlib.table import table

from manager    import Run, RunDict, ResultDict, KEYS, EXPRESSIONS
from ..analysis import Analyzer
from ..utils    import rnd

from .draw      import draw_subtitle, draw_graph
from .args      import pargs

def stages(G, run:RunDict, A:Analyzer, result:ResultDict, i, dir:str, file:str):
    cloud  = A.schema['infra'].upper()
    G.name = f"{run['name']}-STAGE-{i + 1}"

    # meta
    name     = run['name']
    key      = run['strategy']['key']
    rate     = run['parameters']['rate']
    duration = run['parameters']['duration']
    total    = run['parameters']['rate'] * run['parameters']['duration']
    K        = run['parameters']['hyperparameter']

    # pool
    P        = len(run['pool'])
    pool     = A.pool([ A.map(p) for p in run['pool'] ])

    # tree
    root     = A.map(run['tree']['root'])
    depth    = run['tree']['depth']
    fanout   = run['tree']['fanout']
    parent   = A.map(result["root"])
    children = [A.map(s) for s in result["selected"]]
    cmap     = ([pargs.blue] * len(G.nodes())) + ([pargs.red] * len(children))

    for child in children:
        G.add_edge(parent, child) 

    # figure and subplots
    # fig, ax1 = plt.subplots(figsize=(self.pargs.w, self.pargs.h))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(pargs.w, pargs.h))
    title = fig.suptitle(f"{name} Tree - Stage {i + 1}/{len(run['stages'])} - D={depth}, F={fanout}, K={K}, KEY={key}, P={P}, {cloud}", fontsize=pargs.tfont, fontweight='bold')
    ax1.axis("off")
    ax2.axis("off")

    # draw_subtitle(f"ROOT: {root}", ax1, pad=-5)
    subtitle = A.descr(run)
    if subtitle: draw_subtitle(f"{subtitle}", ax2)

    # table
    sel         = [ A.map(s) for s in result["selected"] ]
    clabels     = ["SCORE", "90(%)-OWD", "50(%)-OWD", "STDDEV", "RX(%)"]
    rlabels     = [ A.map(d["addr"]) for d in result["items"] ]
    rowcolors   = ['white'] * len(result["items"])
    colcolors   = ['white'] * len(clabels)
    cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]
    data        = []

    for j,d in enumerate(result["items"]):
        addr = rlabels[j]
        score = EXPRESSIONS[key](d)

        if addr in sel:
            if key in KEYS:
                cellcolors[j][0] = pargs.blue
                cellcolors[j][KEYS.index(key) + 1] = pargs.red
            elif key == "heuristic":
                cellcolors[j][0] = pargs.blue
                cellcolors[j][KEYS.index("p90")    + 1] = pargs.red
                cellcolors[j][KEYS.index("stddev") + 1] = pargs.red

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
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Stage: {rnd(run['timers']['stages'][i], 4)}sec"),
    ]

    plt.legend(handles = handles,
               loc='upper right', 
               fancybox=True, 
               fontsize=pargs.font + 3)

    # plt.tight_layout()
    plt.savefig(f"{dir}/{file}.png", format="png")
        # plt.close('all')
        # plt.clf()
        # del fig 
        # ax1.clear()
        # ax2.clear()
        # del ax1 
        # del ax2 
