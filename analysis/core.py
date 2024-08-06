import os

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from matplotlib.table   import table
from typing             import List
from manager            import ResultDict, RunDict

from . import utils
from . import plot

EXPERIMENT = None
ARGS       = None
ARGS2      = None

COLORS     = plot.COLORS
LINESTYLES = plot.LINESTYLES
MARKERS    = plot.MARKERS

def find(key:str, name:str, root:str=""):
    for i, run in enumerate(EXPERIMENT.runs): 
        _name, _key, _tree, _id = EXPERIMENT.run(run)
        _root = EXPERIMENT.map(run["tree"]["root"])

        if root == "": _bool = True
        else:          _bool = (root == _root)

        if name == _name and key == _key and _bool:
            return run, i

    raise RuntimeError(f"RUN[KEY={key} && NAME={name} && ROOT={root}] DOES NOT EXIST")

def legendResult(result:ResultDict, data:List[List]):
    select = [ s.split(":")[0] for s in result["selected"] ]
    parent = EXPERIMENT.map(result["root"])
    rate   = result["rate"]
    dur    = result["duration"]

    handles  = []
    labels   = []

    for j,item in enumerate(result["items"]):
        addr   = item["addr"].split(":")[0]
        label  = EXPERIMENT.map(item["addr"])
        d      = data[j]
        cnt    = j 
        
        if j >= (len(LINESTYLES) - 1): cnt = 0

        color     = COLORS[ cnt+1 % len(COLORS) ]
        linestyle = LINESTYLES[ cnt+1 % len(LINESTYLES) ]

        if addr in select: 
            linestyle = '-'
        else:              
            color = 'black'
            if j % 2 == 0: color = 'gray'

        handles.append(plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label))
        labels.append(label)

    handles += [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Sender: {parent}"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Rate: {rate}/sec"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Period: {dur}sec"),
    ]
    
    for _ in range((2*len(data)) - (len(handles))):
        handles.append(plt.Line2D([0], [0], marker='s', color='w', alpha=0, label=f" "))

    return handles, labels

def tspResult(fig:plt.Figure, ax:plt.Axes, args, title:str, result:ResultDict, data:List[List], key:str, interval:int=5):
    select = [ s.split(":")[0] for s in result["selected"] ]
    parent = EXPERIMENT.map(result["root"])
    rate   = result["rate"]
    dur    = result["duration"]

    handles  = []
    max_x    = 0
    max_y    = 0
    
    for j,item in enumerate(result["items"]):
        addr   = item["addr"].split(":")[0]
        label  = EXPERIMENT.map(item["addr"])
        d      = data[j]
        cnt    = j
        
        if j >= (len(LINESTYLES) - 1): cnt = 0

        color     = COLORS[ cnt+1 % len(COLORS) ]
        linestyle = LINESTYLES[ cnt+1 % len(LINESTYLES) ]
        
        if addr in select: 
            linestyle = '-'
        else:              
            color = 'black'
            if j % 2 == 0: color = 'gray'
    
        line, max_xi, max_yi   = plot.tsp(ax, label=label, color=color, linestyle=linestyle, step=rate, data=d, key=key)

        max_x = max(max_x, max_xi)
        max_y = max(max_y, max_yi)

        handle = plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label)
        handles.append(handle)
    
    fig.suptitle(f"{title}", fontsize=args.tfont, fontweight='bold')
    
    if args.title:
        ax.set_title(f"TIME SERIES {key.upper()} OWD (uS)", fontsize=args.nfont + 2, fontweight='bold')

    ax.set_xlim(0, max_x + 1)
    ax.set_ylim(0, max_y * 1.5)
    ax.set_xticks(np.arange(1, max_x + 1, interval))

    if args.ylabel:
        ax.set_ylabel("OWD(us)", fontsize=args.nfont)
    
    if args.xlabel:
        ax.set_xlabel("t(s)", fontsize=args.nfont)

    ax.tick_params(axis='x', labelsize=args.nfont - 1)
    ax.tick_params(axis='y', labelsize=args.nfont - 1)
    
    handles += [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Sender: {parent}"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Rate: {rate}/sec"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Period: {dur}sec"),
    ]
    
    for _ in range((2*len(data)) - (len(handles))):
        handles.append(plt.Line2D([0], [0], marker='s', color='w', alpha=0, label=f" "))
    
    if args.legend:
        ax.legend(handles=handles, loc='best', fancybox=True, fontsize=args.nfont + 1, ncol=2)

    return

def cdfResultArr(fig:plt.Figure, ax:plt.Axes, args, title:str, i:int, result:ResultDict, data:List[List]):
    max_x    = 0
    max_y    = 0

    handles = []
        
    for j,item in enumerate(result["items"]):
        addr   = item["addr"].split(":")[0]
        label  = EXPERIMENT.map(item["addr"])
        d      = data[j]
        cnt    = i

        if i >= (len(LINESTYLES) - 1): cnt = 0

        color     = COLORS[ cnt+1 % len(COLORS) ]
        linestyle = '-'
        
        line, max_xi, max_yi = plot.cdf(ax, label=label, color=color, linestyle=linestyle, data=d)
        handle = plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label)
        handles.append(handle)

        max_x = max(max_x, max_xi)
        max_y = max(max_y, max_yi)
        
    fig.suptitle(f"{title}", fontsize=args.tfont, fontweight='bold')
    
    if args.title:
        ax.set_title(f"CDF OWD LATENCY (uS)", fontsize=args.nfont + 2, fontweight='bold')

    ax.set_xlim(0, max_x + 50)
    ax.set_ylim(0, 100)
    
    if args.ylabel:
        ax.set_ylabel("CDF", fontsize=args.nfont)
    
    if args.xlabel:
        ax.set_xlabel("OWD(us)", fontsize=args.nfont)

    ax.tick_params(axis='x', labelsize=args.nfont - 1)
    ax.tick_params(axis='y', labelsize=args.nfont - 1)
        
    return max_x, max_y, handles

def cdfResult(fig:plt.Figure, ax:plt.Axes, args, title:str, result:ResultDict, data:List[List]):
    select = [ s.split(":")[0] for s in result["selected"] ]
    parent = EXPERIMENT.map(result["root"])
    rate   = result["rate"]
    dur    = result["duration"]

    # fig1, ax = plt.subplots()
    # fig1, ax = plt.subplots(figsize=(args.w - 8, args.h))
    handles  = []
    max_x    = 0
    max_y    = 0
        
    for j,item in enumerate(result["items"]):
        addr   = item["addr"].split(":")[0]
        label  = EXPERIMENT.map(item["addr"])
        d      = data[j]
        cnt    = j

        if j >= (len(LINESTYLES) - 1): cnt = 0

        color     = COLORS[ cnt+1 % len(COLORS) ]
        linestyle = LINESTYLES[ cnt+1 % len(LINESTYLES) ]
        
        if addr in select: 
            linestyle = '-'
        else:              
            color = 'black'
            if j % 2 == 0: color = 'gray'
        
        line, max_xi, max_yi = plot.cdf(ax, label=label, color=color, linestyle=linestyle, data=d)
        handle = plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label)
        handles.append(handle)

        max_x = max(max_x, max_xi)
        max_y = max(max_y, max_yi)
        
    fig.suptitle(f"{title}", fontsize=args.tfont, fontweight='bold')
    
    if args.title:
        ax.set_title(f"CDF OWD LATENCY (uS)", fontsize=args.nfont + 2, fontweight='bold')

    ax.set_xlim(0, max_x + 50)
    ax.set_ylim(0, 100)
    
    if args.ylabel:
        ax.set_ylabel("CDF", fontsize=args.nfont)
    
    if args.xlabel:
        ax.set_xlabel("OWD(us)", fontsize=args.nfont)

    ax.tick_params(axis='x', labelsize=args.nfont - 1)
    ax.tick_params(axis='y', labelsize=args.nfont - 1)
        
    handles += [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Sender: {parent}"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Rate: {rate}/sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Period: {dur}sec"),
    ]
        
    for _ in range((2*len(data)) - (len(handles))):
        handles.append(plt.Line2D([0], [0], marker='s', color='w', alpha=0, label=f" "))
        
    if args.legend:
        ax.legend(handles=handles, loc='best', fancybox=True, fontsize=args.nfont + 1, ncol=2)

    return max_x, max_y

def tableResult(fig:plt.Figure, ax:plt.Axes, args, title:str, run:RunDict, result:ResultDict, data:List[List], cols:List=[]):
    key         = run['strategy']['key']
    rate        = run['parameters']['rate']
    duration    = run['parameters']['duration']
    total       = run['parameters']['rate'] * run['parameters']['duration']
    
    sel         = [ EXPERIMENT.map(s) for s in result["selected"]]
    clabels     = ["99(%)", "90(%)", "50(%)", "MEAN", "STDDEV", "RX(%)"]
    rlabels     = [ EXPERIMENT.map(d["addr"]) for d in result["items"] ]
    rowcolors   = ['white'] * len(result["items"])
    colcolors   = ['white'] * len(clabels)
    cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]
    cells       = []

    fig.suptitle(f"{title}", fontsize=args.tfont, fontweight='bold')

    if args.title:
        ax.set_title(f"{title}", fontsize=args.nfont + 2, fontweight='bold')
        
    ax.axis("off")

    for i,d in enumerate(result["items"]):
        addr    = rlabels[i]
        d       = np.array(data[i])
        p99     = float(np.percentile(d, 99))
        p90     = float(np.percentile(d, 90))
        p75     = float(np.percentile(d, 75))
        p50     = float(np.percentile(d, 50))
        p25     = float(np.percentile(d, 25))
        mean    = float(np.mean(d))
        stddev  = float(np.std(d))
        recv    = len(data[i]) 
        score   = 0.0
        
               
        if key == "p90" or key == "NONE":
            score   = p90
                     
        elif key == "p50":
            score   = p50
                     
        elif key == "heuristic":
            score   = 0.3 * p90 + 0.7 * stddev 
            
        else: 
            raise RuntimeError(f"UNEXPECTED KEY: {key}")
        
        if addr in sel: 
            cnt = i 
            if cnt == len(result["items"]) - 1: cnt = 0
            color = COLORS[ cnt+1 % len(COLORS) ]
            if cols:
                for c in cols:
                    cellcolors[i][c] =  color
            else:
                if key == "p90" or key == "NONE":
                    cellcolors[i][1] = color
                elif key == "p50":
                    cellcolors[i][2] = color
                elif key == "heuristic":
                    cellcolors[i][1] =  color
                    cellcolors[i][-2] = color
        else:
            color = "#cccccc"
            if cols:
                for c in cols:
                    cellcolors[i][c] =  color

        perc = 100 * (float(recv/total))
        # cells.append([ utils.rnd(float(score)),
        cells.append( [utils.rnd(p99), 
                       utils.rnd(p90), 
                       utils.rnd(p50), 
                       utils.rnd(mean), 
                       utils.rnd(stddev),
                       utils.rnd(perc)])

    th = ( args.factor )
    tb = table(ax, 
               colLabels=clabels, 
               colColours=colcolors, 
               cellColours=cellcolors, 
               rowLabels=rlabels, 
               rowColours=rowcolors,
               cellText=cells, 
               cellLoc='left',
               loc='top',
               bbox=[0, 1 - th , 1, th])
               # left bottom width height

    tb.auto_set_font_size(False)
    tb.set_fontsize(args.tbfont + 5) 

def graphTree(fig, ax, args, title, run, i):
    G           = EXPERIMENT.graph(run)
    color       = COLORS[ (i+1) % len(COLORS) ]
    cmap        = ([color] * len(G.nodes()))

    if args.title:
        ax.set_title(f"{title}", fontsize=args.nfont + 2, fontweight='bold')

    plot.graph(G, ax, args, cmap)
    return fig

    
def graphStage(G, i, args, run:RunDict, result:ResultDict, data:List[List]):
    cloud  = EXPERIMENT.schema['infra'].upper()
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
    pool     = [ EXPERIMENT.map(p) for p in run['pool'] ]

    # tree
    root     = EXPERIMENT.map(run['tree']['root'])
    depth    = run['tree']['depth']
    fanout   = run['tree']['fanout']
    parent   = EXPERIMENT.map(result["root"])
    children = [EXPERIMENT.map(s) for s in result["selected"]]
    
    if parent not in G.nodes():
        G.add_node(parent)
    
    cmap     = (["gray"] * len(G.nodes())) + (["red"] * len(children))

    for child in children:
        G.add_edge(parent, child) 

    # figure and subplots
    # fig, ax1 = plt.subplots(figsize=(self.pargs.w, self.pargs.h))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(args.w, args.h))
    title = fig.suptitle(f"{name} Tree - Stage {i + 1}/{len(run['stages'])} - D={depth}, F={fanout}, K={K}, KEY={key}, P={P}, {cloud}", fontsize=args.tfont, fontweight='bold')
    ax1.axis("off")
    ax2.axis("off")

    # draw_subtitle(f"ROOT: {root}", ax1, pad=-5)
    subtitle = EXPERIMENT.description(run)
    if subtitle: 
        ax2.set_title(f"{subtitle}", fontsize=args.tfont - 2, fontweight='bold')
        
    # table
    sel         = [ EXPERIMENT.map(s) for s in result["selected"] ]
    clabels     = ["SCORE", "90(%)-OWD", "50(%)-OWD", "MEAN", "STDDEV", "RX(%)"]
    rlabels     = [ EXPERIMENT.map(d["addr"]) for d in result["items"] ]
    rowcolors   = ['white'] * len(result["items"])
    colcolors   = ['white'] * len(clabels)
    cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]
    data        = []

    for j,d in enumerate(result["items"]):
        addr = rlabels[j]
        score   = 0.0
        
               
        if key == "p90" or key == "NONE":
            score   = d["p90"]
                     
        elif key == "p50":
            score   = d["p50"]
                     
        elif key == "heuristic":
            score   = 0.3 * d["p90"] + 0.7 * d["stddev"] 
            
        else: 
            raise RuntimeError(f"UNEXPECTED KEY: {key}")

        if addr in sel: 
            color    = COLORS[ j + 1 % len(COLORS) ]
            if key == "p90":
                cellcolors[j][0] = color
                cellcolors[j][1] = color
            elif key == "p50":
                cellcolors[j][0] = color
                cellcolors[j][2] = color
            elif key == "heuristic":
                cellcolors[j][0] =  color
                cellcolors[j][1] =  color
                cellcolors[j][-2] = color
            elif key == "NONE":
                cellcolors[j][0] = color
                cellcolors[j][1] = color

        perc = 100 * (float(d["recv"]/total))
        data.append([ utils.rnd(float(score)),
                      utils.rnd(d["p90"]), 
                      utils.rnd(d["p50"]), 
                      utils.rnd(d["mean"]), 
                      utils.rnd(d['stddev']),
                      utils.rnd(perc)])

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
    tb.set_fontsize(args.font + 5)

    # graph
    plot.graph(G, ax2, args, cmap)

    handles = [
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Total: {total} packets"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Rate: {rate} packets/sec"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Measurement: {duration}sec"),
        plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Stage: {utils.rnd(run['timers']['stages'][0], 4)}sec"),
    ]

    plt.legend(handles = handles,
               loc='upper right', 
               fancybox=True, 
               fontsize=args.font + 3)

    return fig
    
def graphResult(run:RunDict, iter:int, args):
    G = EXPERIMENT.graph(run)
    name     = run['name']
    key      = run['strategy']['key']
    rate     = run['parameters']['rate']
    duration = run['parameters']['duration']
    total    = run['parameters']['rate'] * run['parameters']['duration']
    K        = run['parameters']['hyperparameter']
    result   = ResultDict(run["perf"][iter])
    cloud    = EXPERIMENT.schema['infra'].upper()

    # pool
    P        = len(run['pool'])
    pool     = [ EXPERIMENT.map(p) for p in run['pool'] ] 
    color    = COLORS[ 1 % len(COLORS) ]

    # tree
    root     = EXPERIMENT.map(run['tree']['root'])
    depth    = run['tree']['depth']
    fanout   = run['tree']['fanout']
    N        = run['tree']['n']

    sel      = [EXPERIMENT.map(s) for s in result["selected"]]
    cmap     = ([color] * len(G.nodes()))
    for i,node in enumerate(G.nodes()):
        if node in sel:
            cmap[i] = color

    # fig, ax1 = plt.subplots(figsize=(pargs.w, pargs.h))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(args.w, args.h))
    ax1.axis("off")
    ax2.axis("off")

    fig.suptitle(f"{name} Tree - Performance[i={iter + 1}] - N={N}, D={depth}, F={fanout}, K={K}, KEY={key}, P={P}, {cloud}", fontsize=args.tfont, fontweight='bold')
    ax1.set_title(f"ROOT: {root}", fontsize=args.tfont - 2, fontweight='bold',  y = 1.0)

    subtitle = EXPERIMENT.description(run)
    if subtitle: 
        ax2.set_title(f"{subtitle}", fontsize=args.tfont - 2, fontweight='bold')

    # gs = fig.add_gridspec(2, 1, height_ratios=[0.6, 0.4])  # 60% for the first subplot, 40% for the second
    # ax1 = fig.add_subplot(gs[0])
    # ax2 = fig.add_subplot(gs[1])

    # table
    clabels     = ["SCORE", "90(%)-OWD", "50(%)-OWD", "MEAN", "STDDEV", "RX(%)"]
    rlabels     = [ EXPERIMENT.map(d["addr"]) for d in result["items"] ]
    rowcolors   = ['white'] * len(result["items"])
    colcolors   = ['white'] * len(clabels)
    cellcolors  = [ ['white' for _ in range(len(clabels))] for _ in range(len(rlabels)) ]
    data        = []

    for i,d in enumerate(result["items"]):
        addr = rlabels[i]
        score   = 0.0
        
               
        if key == "p90" or key == "NONE":
            score   = d["p90"]
                     
        elif key == "p50":
            score   = d["p50"]
                     
        elif key == "heuristic":
            score   = 0.3 * d["p90"] + 0.7 * d["stddev"] 
            
        else: 
            raise RuntimeError(f"UNEXPECTED KEY: {key}")
        
        if addr in sel:
            if key == "p90":
                cellcolors[i][0] = color
                cellcolors[i][1] = color
            elif key == "p50":
                cellcolors[i][0] = color
                cellcolors[i][2] = color
            elif key == "heuristic":
                cellcolors[i][0] =  color
                cellcolors[i][1] =  color
                cellcolors[i][-2] = color
            elif key == "NONE":
                cellcolors[i][0] = color
                cellcolors[i][1] = color

        perc = 100 * (float(d["recv"]/total))
        data.append([ utils.rnd(float(score)),
                      utils.rnd(d["p90"]), 
                      utils.rnd(d["p50"]), 
                      utils.rnd(d["mean"]), 
                      utils.rnd(d['stddev']),
                      utils.rnd(perc)])

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
    tb.set_fontsize(args.font + 5)

    # graph
    plot.graph(G, ax2, args, cmap)

    handles = [plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Total: {total} packets"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Rate: {rate} packets/sec"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Measurement: {duration}sec"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Build: {utils.rnd(run['timers']['build'], 4)}sec"),
                plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Evaluation: {utils.rnd(run['timers']['perf'][iter], 4)}sec"),]
    
    if "LEMON" in name:
        handles.append(plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"Converged: {utils.rnd(run['timers']['convergence'], 4)}sec"))

    plt.legend(handles = handles,
               loc='upper right', 
               fancybox=True, 
               fontsize=args.font + 3)

    suffix=""
    if "LEMON" in name:
        epsilon = run["parameters"]["epsilon"]
        max_i   = run["parameters"]["max_i"]
        suffix  = f"x{epsilon}x{max_i}"
    
    return fig

def graphComparison(G1, G2, data1:RunDict, data2:RunDict, args):
    # meta
    name_1          = G1.name.upper()
    name_2          = G2.name.upper()
    key_1           = data1["strategy"]["key"]
    key_2           = data2["strategy"]["key"]
    root_1          = EXPERIMENT.map(data1["tree"]["root"])
    root_2          = EXPERIMENT.map(data2["tree"]["root"])

    rate     = data1['parameters']['rate']
    duration = data1['parameters']['duration']
    total    = data1['parameters']['rate'] * data1['parameters']['duration']
    K        = data1['parameters']['hyperparameter']
    cloud    = EXPERIMENT.schema['infra'].upper()
    iter1    = EXPERIMENT.worst(data1["perf"])
    iter2    = EXPERIMENT.worst(data2["perf"])

    # pool
    P        = len(data1['pool'])

    # tree
    depth    = data1['tree']['depth']
    fanout   = data1['tree']['fanout']
    root1    = EXPERIMENT.map(data1['tree']['root'])
    root2    = EXPERIMENT.map(data2['tree']['root'])
    N        = data1['tree']['n']

    red   = COLORS[ 1 % len(COLORS) ]
    blue  = COLORS[ 2 % len(COLORS) ]
    gray  = "gray" 
    
    # red    = '#FF9999'
    # blue   = '#99CCFF'
    # gray   = '#CCCCCC' # #efe897

    
    cmap1 = ([blue] * len(G1.nodes()))
    cmap2 = ([red]  *  len(G2.nodes()))


    for i, (n1, n2) in enumerate(zip(G1.nodes(), G2.nodes())):
        if n1 == n2:
            cmap1[i] = gray
            cmap2[i] = gray

    fig = plt.figure(figsize=(int(args.w), args.h))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.3, 0.7])
    gs_graphs = gs[1].subgridspec(1, 2)

    ax_t = fig.add_subplot(gs[0])
    ax1  = fig.add_subplot(gs_graphs[0])
    ax2  = fig.add_subplot(gs_graphs[1]) 

    fig.suptitle(f"Tree(s): {G1.name} x {G2.name} - N={N}, D={depth}, F={fanout}, K={K}, P={P}, {cloud}", fontsize=args.tfont, fontweight='bold')
    ax_t.set_title(f"ROOTS: {root1} x {root2}", fontsize=args.tfont - 2, fontweight='bold',  y = 0.9)

    ax_t.axis('off')
    ax1.axis('off')
    ax2.axis('off')

    # table
    sel1        = EXPERIMENT.map(data1["perf"][iter1]["selected"][0])
    sel2        = EXPERIMENT.map(data2["perf"][iter2]["selected"][0])
    clabels     = ["90(%)", "50(%)", "STDDEV", "RX(%)"]
    rlabels1    = [ EXPERIMENT.map(d["addr"]) for d in data1["perf"][iter1]["items"] ]
    rlabels2    = [ EXPERIMENT.map(d["addr"]) for d in data2["perf"][iter2]["items"] ]
    cellcolors1 = [ ['white'] * len(clabels) for _ in range(len(rlabels1)) ]
    cellcolors2 = [ ['white'] * len(clabels) for _ in range(len(rlabels1)) ]
    cells1      = []
    cells2      = []

    for i,(d1,d2) in enumerate(zip(data1["perf"][iter1]["items"], data2["perf"][iter2]["items"])):
        addr1 = EXPERIMENT.map(d1["addr"])
        addr2 = EXPERIMENT.map(d2["addr"])

        perc1 = 100 * (float(d1["recv"]/total))
        cells1.append([ d1["p90"], 
                        d1["p50"], 
                        utils.rnd(d1['stddev']),
                        utils.rnd(perc1)])

        perc2 = 100 * (float(d2["recv"]/total))
        cells2.append([ d2["p90"], 
                        d2["p50"], 
                        utils.rnd(d2['stddev']),
                        utils.rnd(perc2)])

        if addr1 == sel1: cellcolors1[i][0] = blue
        if addr2 == sel2: cellcolors2[i][0] = red

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

    tb11 = table(ax_t, colLabels=[f"BUILD", f"CONVERGENCE", f"EVALUATION[{iter1}]",f"TOTAL"], 
                cellText=[[
                    f"{utils.rnd(data1['timers']['build'], 2)}s",
                    f"{utils.rnd(data1['timers']['convergence'], 6)}s",
                    f"{utils.rnd(data1['timers']['perf'][iter1], 2)}s",
                    f"{utils.rnd(data1['timers']['total'], 2)}s",
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
                colLabels=[f"BUILD", f"CONVERGENCE", f"EVALUATION[{iter2}]", f"TOTAL"], 
                cellText=[[
                    f"{utils.rnd(data2['timers']['build'], 2)}s",
                    f"{utils.rnd(data2['timers']['convergence'], 6)}s",
                    f"{utils.rnd(data2['timers']['perf'][iter2], 2)}s",
                    f"{utils.rnd(data2['timers']['total'], 2)}s",
                ]],
                cellLoc='left',
                loc='top',
                bbox=[tw + gap, 0.6 - th2 - 0.2, tw, (0.095 * 2)])

    tb1.auto_set_font_size(False)
    tb1.set_fontsize(args.font + 5)
    tb11.auto_set_font_size(False)
    tb11.set_fontsize(args.font + 5)
    tb12.auto_set_font_size(False)
    tb12.set_fontsize(args.font + 5)
    tb2.auto_set_font_size(False)
    tb2.set_fontsize(args.font + 5)

    plot.graph(G1, ax1, args, cmap1, 'black')
    plot.graph(G2, ax2, args, cmap2, 'black')

    sub1 = EXPERIMENT.description(data1)
    if sub1: name1 = f"{G1.name} {sub1}"
    else:    name1 = f"{G1.name}"

    sub2 = EXPERIMENT.description(data2)
    if sub2: name2 = f"{G2.name} {sub2}"
    else:    name2 = f"{G2.name}"

    handles = [ plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=blue,  markersize=10, label=f"{name1}"), 
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=red,   markersize=10, label=f"{name2}"),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=gray, markersize=10,  label=f"COMMON"),
    ]

    if "LEMON" in name_1:
        name_1  = f"{name_1}x{data1['parameters']['epsilon']}x{data1['parameters']['max_i']}"
    
    if "LEMON" in name_2:
        name_2  = f"{name_2}x{data2['parameters']['epsilon']}x{data2['parameters']['max_i']}"

    fig.legend(handles=handles,  loc='center', fontsize=args.font)
    plt.tight_layout()
    return fig


def plotComparisons(i:int, rdir:str): 
    run_i = EXPERIMENT.runs[i]
    name_i, key_i, tree_i, id_i = EXPERIMENT.run(run_i)  
    G_i = EXPERIMENT.graph(run_i)
    
    for j, run_j in enumerate(EXPERIMENT.runs): 
        if j == i: 
            continue 
        
        name_j, key_j, tree_j, id_j = EXPERIMENT.run(run_j)
        G_j = EXPERIMENT.graph(run_j)

        dir = rdir + f"/cmp"
        file = f"{id_i}x{id_j}_CMP_GRAPH.png"
        
        fig  = graphComparison(G_i, G_j, run_i, run_j, args=ARGS) 
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")

def plotStages(run: RunDict, rdir:str):
    name, key, tree, id = EXPERIMENT.run(run) 
    dir     = f"{rdir}" 
    handles = [] 
    labels = []

    F, G = plt.subplots(nrows=len(run["stages"]), ncols=4, figsize=(40, 32))
    if len(run["stages"]) == 1: G = [ G ] 
    
    TREE = nx.DiGraph()

    for i, stage in enumerate(run["stages"]):
        data    = EXPERIMENT.jobs[stage["id"]]
        print(f"RUN[{id}] => STAGE[{i+1}/{len(run['stages'])}]")
        
        # plot and save individual CDF
        file    = f"{id}_STAGE_{i + 1}_CDF.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        cdfResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data)
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")

        # plot and save individual MEDIAN TSP
        file    = f"{id}_STAGE_{i + 1}_MEDIAN_TSP.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        tspResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="p50")
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")

        # plot and save individual STDDEV TSP
        file    = f"{id}_STAGE_{i + 1}_STDDEV_TSP.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        tspResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="stddev")
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")

         # plot and save individual TABLE
        file    = f"{id}_STAGE_{i + 1}_TABLE.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        tableResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} RESULTS - STAGE[{i + 1}]", run=run, result=stage, data=data)
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")  
        
        # plot and save individual GRAPH
        file    = f"{id}_STAGE_{i + 1}_GRAPH.png"
        fig = graphStage(TREE, i, args=ARGS, run=run, result=stage, data=data)
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")

        # plot major grid for visualization on notebook
        ARGS2.legend = False
        ARGS2.title  = False
        
        if i == 0:
            ARGS2.title = True 
            
        tableResult(fig=F, ax=G[i][0], args=ARGS2, title=f"{tree} RESULTS - STAGE[{i + 1}]", run=run, result=stage, data=data)

        ARGS2.legend  = True
        cdfResult(fig=F, ax=G[i][1], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data)
        ARGS2.legend  = False

        tspResult(fig=F, ax=G[i][2], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="p50")
        tspResult(fig=F, ax=G[i][3], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="stddev")
        
        handles, labels = legendResult(stage, data)

    
    F.suptitle(f"{id} STAGES", fontsize=ARGS.tfont, fontweight='bold')
    file = f"{id}_ALL_STAGES.png" 
    
    F.legend(handles=handles, 
             labels=labels, 
             loc='upper center', 
             bbox_to_anchor=(0.5, 1 + 0.1),
             ncol=2, 
             fancybox=True, 
             shadow=True)
    
    
    F.savefig(f"{dir}/{file}", format="png")
    # plt.show()
    plt.close(F)
    print(f"PLOTTED: {file}")

def plotEval(run: RunDict, rdir:str):
    name, key, tree, id = EXPERIMENT.run(run) 
    dir     = f"{rdir}/eval" 
    handles = [] 
    labels = []

    F, G = plt.subplots(nrows=len(run["perf"]), ncols=4, figsize=(40, 32))
    if len(run["perf"]) == 1: G = [ G ]

    for i, stage in enumerate(run["perf"]):
        data    = EXPERIMENT.jobs[stage["id"]]
        print(f"RUN[{id}] => PERF[{i+1}/{len(run['perf'])}]")
        
        # plot and save individual CDF
        file    = f"{id}_EVAL_{i + 1}_CDF.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        cdfResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} - EVAL[{i + 1}]", result=stage, data=data)
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")

        # plot and save individual MEDIAN TSP
        file    = f"{id}_EVAL_{i + 1}_MEDIAN_TSP.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        tspResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} - EVAL[{i + 1}]", result=stage, data=data, key="p50")
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")

        # plot and save individual STDDEV TSP
        file    = f"{id}_EVAL_{i + 1}_STDDEV_TSP.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        tspResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} - EVAL[{i + 1}]", result=stage, data=data, key="stddev")
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")
        
         # plot and save individual TABLE
        file    = f"{id}_EVAL_{i + 1}_TABLE.png"
        fig, ax = plt.subplots(figsize=(ARGS.w - 8, ARGS.h))
        tableResult(fig=fig, ax=ax, args=ARGS, title=f"{tree} RESULTS - EVAL[{i + 1}]", run=run, result=stage, data=data)
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")   
      
        file    = f"{id}_EVAL_{i + 1}_GRAPH.png"
        fig = graphResult(run, i, ARGS)
        fig.savefig(f"{dir}/{file}", format="png")
        plt.close(fig)
        print(f"PLOTTED: {file}")   

        # plot major grid for visualization on notebook
        ARGS2.legend = False
        ARGS2.title  = False
        
        if i == 0:
            ARGS2.title = True 
            
        tableResult(fig=F, ax=G[i][0], args=ARGS2, title=f"{tree} RESULTS - STAGE[{i + 1}]", run=run, result=stage, data=data)

        ARGS2.legend  = True
        cdfResult(fig=F, ax=G[i][1], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data)
        ARGS2.legend  = False

        tspResult(fig=F, ax=G[i][2], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="p50")
        tspResult(fig=F, ax=G[i][3], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="stddev")
        
        handles, labels = legendResult(stage, data)

    
    F.suptitle(f"{id} EVALUATION", fontsize=ARGS.tfont, fontweight='bold')
    file = f"{id}_ALL_EVALS.png" 
    
    F.legend(handles=handles, 
             labels=labels, 
             loc='upper center', 
             bbox_to_anchor=(0.5, 1 + 0.1),
             ncol=2, 
             fancybox=True, 
             shadow=True)
    
    
    F.savefig(f"{dir}/{file}", format="png")
    plt.close(F)
    print(f"PLOTTED: {file}")

def plotCDFomparison(run:RunDict, runs:List[RunDict], rdir:str, file:str):
    F, G = plt.subplots(nrows=len(runs) + 1, 
                        ncols=4, 
                        figsize=(28, 18))

    _, _, _, ID = EXPERIMENT.run(run)  
    arr = [ run ] + runs
    max_x = 0
    max_y = 0

    for i, run in enumerate(arr): 
        name, key, tree, id = EXPERIMENT.run(run)
        iter                = EXPERIMENT.worst(run["perf"])
        stage               = run["perf"][iter]
        data                = EXPERIMENT.jobs[stage["id"]]

        handles, max_x, max_y = cdfResultArr(fig=F,  ax=G[i][1], args=ARGS2, title=f"{tree} - EVAL[{iter}]", i=i, result=stage[:2], data=data[:2])

def plotEvalComparison(run:RunDict, runs:List[RunDict], rdir:str, title:str, file:str):
    F, G = plt.subplots(nrows=len(runs) + 1, 
                        ncols=5, 
                        figsize=(32, 18))

    _, _, _, ID = EXPERIMENT.run(run)  
    arr = [ run ] + runs
    max_x = 0
    max_y = 0

    for i, run in enumerate(arr): 
        name, key, tree, id = EXPERIMENT.run(run)
        root                = EXPERIMENT.map(run["tree"]["root"])
        iter                = EXPERIMENT.worst(run["perf"])
        stage               = run["perf"][iter]
        data                = EXPERIMENT.jobs[stage["id"]]

        if "LEMON" in name or "RAND" in name:
            id = f"{name}x{root}"

        ARGS2.legend = False
        ARGS2.title  = True

        tableResult(fig=F, ax=G[i][0], args=ARGS2, title=f"{id} RESULTS", run=run, result=stage, data=data, cols=[1, -2])
        if i > 0:
            ARGS2.title  = False

        max_x_i, max_y_i = cdfResult(fig=F,   ax=G[i][1], args=ARGS2, title=f"{tree} - EVAL[{iter}]", result=stage, data=data)
        max_x = max(max_x, max_x_i)
        max_y = max(max_y, max_y_i)
        for k in range(len(arr)):
            ax = G[k][1]
            ax.set_xlim(0, max_x + 50)
            ax.set_ylim(0, max_y)
            ax.set_xticks(np.arange(0, max_x, 100))

        tspResult(fig=F,   ax=G[i][2], args=ARGS2, title=f"{tree} - EVAL[{iter}]", result=stage, data=data, key="p90")
        tspResult(fig=F,   ax=G[i][3], args=ARGS2, title=f"{tree} - EVAL[{iter}]", result=stage, data=data, key="p50")
        tspResult(fig=F,   ax=G[i][4], args=ARGS2, title=f"{tree} - EVAL[{iter}]", result=stage, data=data, key="stddev")
        # graphTree(fig=F,   ax=G[i][4], args=ARGS2, title=f"{tree} - TREE", run=run, i=0)

        if "LEMON" in run["name"]: 
            handles = [ 
                       plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"eps={run['parameters']['epsilon']} , max_i={run['parameters']['max_i']}"), 
                       plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"converged={run['parameters']['converge']}"), 
                       plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=10, label=f"time={utils.rnd(run['timers']['convergence'], 4)} sec"), 
                       ]
            G[i][1].legend(handles=handles,  loc='lower center', fontsize=ARGS2.font)


    dir     = f"{rdir}" 
    F.suptitle(f"{title}", fontsize=ARGS.tfont + 10, fontweight='bold')
    # ax_t.set_title(f"ROOTS: {root1} x {root2}", fontsize=args.tfont - 2, fontweight='bold',  y = 0.9)

    # F.suptitle(f"", fontsize=0, fontweight='bold')
    F.savefig(f"{dir}/{file}", format="png")
    plt.close(F)
    print(f"PLOTTED: {file}")

def plotStageComparison(run:RunDict, stages:List[ResultDict], rdir:str, title:str, file:str):
    F, G = plt.subplots(nrows=len(stages), 
                        ncols=5, 
                        figsize=(32, 18))

    name, key, tree, id = EXPERIMENT.run(run) 
    dir     = f"{rdir}" 
    handles = [] 
    labels = []

    for i,stage in enumerate(stages):
        data    = EXPERIMENT.jobs[stage["id"]]

        ARGS2.legend = False
        ARGS2.title  = False

        tableResult(fig=F, ax=G[i][0], args=ARGS2, title=f"{tree} RESULTS - STAGE[{i + 1}]", run=run, result=stage, data=data)
        
        if i == 0:
            ARGS2.title = True 

        ARGS2.legend  = True
        tmp = ARGS2.nfont
        ARGS2.nfont = tmp - 5
        cdfResult(fig=F, ax=G[i][1], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data)
        ARGS2.nfont = tmp
        ARGS2.legend  = False

        tspResult(fig=F, ax=G[i][2], args=ARGS2, title=f"{tree} - EVAL[{iter}]", result=stage, data=data, key="p90", interval=2)
        tspResult(fig=F, ax=G[i][3], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="p50", interval=2)
        tspResult(fig=F, ax=G[i][4], args=ARGS2, title=f"{tree} - STAGE[{i + 1}]", result=stage, data=data, key="stddev", interval=2)
        
        handles, labels = legendResult(stage, data)

    F.suptitle(f"{title}", fontsize=ARGS.tfont + 10, fontweight='bold')
    # F.legend(handles=handles, 
    #          labels=labels, 
    #          loc='upper center', 
    #          bbox_to_anchor=(0.5, 1 + 0.1),
    #          ncol=2, 
    #          fancybox=True, 
    #          shadow=True)
    
    F.savefig(f"{dir}/{file}", format="png")
    # plt.show()
    plt.close(F)
    print(f"PLOTTED: {file}")
    
def plotRun(run:RunDict, i:int, dir:str, compare:bool=True): 
    name, key, tree, id = EXPERIMENT.run(run)
    rdir = os.path.join(dir, id)

    utils.mkdir(rdir)
    for d in [ "cmp", "stages", "eval"]:
        os.mkdir(f"{rdir}/{d}")
            
    if "RAND" not in name and "LEMON" not in name:
        plotStages(run, f"{rdir}/stages") 
            
    plotEval(run, rdir) 

    if compare:
        plotComparisons(i, rdir)

def plotAll(dir:str): 
    ARGS.show  = False 
    ARGS2.show = False

    for i, run in enumerate(EXPERIMENT.runs):
        plotRun(run, i, dir)

def plotTarget(key:str, name:str, dir:str, root:str=""): 
    run, i = find(key=key, name=name, root=root)
    plotRun(run, i, dir, compare=False)
