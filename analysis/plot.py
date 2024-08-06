import numpy as np
import matplotlib.pyplot as plt 
import networkx as nx 

from typing import List

MARKERS     = ["*", ".", "+", "1", '2', 'v', '<', '>', '^', 'h', '3', '4', '8', 's', 'p', 'P', ',', 'H', 'o', 'x', 'D', 'd']
COLORS      = ['black', 'orange', 'red', 'magenta', 'brown', 'magenta', 'orange', 'brown', 'cyan', 'magenta', 'gray', 'yellow', 'white', 'olive', 'maroon', 'orange', 'teal', 'lime', 'aqua', 'fuchsia', 'silver', 'gold', 'indigo', 'violet', 'coral', 'salmon', 'peru', 'orchid', 'lavender', 'turquoise']
LINESTYLES  = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 1))]

def cdf(ax:plt.Axes, label:str, color:str, linestyle:str, data:List):
    # percentiles to show
    y = [ round(i, 2) for i in list(np.arange(1, 100, 1)) ]

    # data
    x = np.percentile(data, y)

    line = ax.plot(x, 
                    y, 
                    label=label, 
                    color=color,
                    linestyle=linestyle, 
                    linewidth=3.0)

    return line, max(x), max(y)

def tsp(ax:plt.Axes, label:str, color:str, linestyle:str, step:int, data:List, key:str):
    x       = []
    y       = []
    d       = {
        "p90":          lambda buf, x:     np.percentile(buf, 90),
        "p50":          lambda buf, x:     np.percentile(buf, 50),
        "mad":          lambda buf, x:     np.mean(np.absolute(buf - np.median(x))),
        "iqr":          lambda buf, x:     np.quantile(buf, 0.75) - np.quantile(buf, 0.25),
        "stddev":       lambda buf, x:     np.std(buf),
        "sign-stddev":  lambda buf, x:     np.mean( np.array(buf) - np.mean(x) ),
    }


    xi  = 1
    buf = []

    for i,element in enumerate(data):
        buf  += [element]
        count = len(buf)

        if (count >= step) or i == (len(data)-1):
                value = d[key](buf, data)
                buf   = []

                y  += [value]
                x  += [xi]
                xi += 1

    line = ax.plot(x, 
                   y, 
                   label=label, 
                   color=color,
                   linestyle=linestyle,
                   linewidth=3.0)

    return line, max(x), max(y) 

def graph(G, ax:plt.Axes, args, cmap=None, emap=None):
    G.graph['rankdir'] = "TB"
    G.graph['ranksep'] = "0.03"
    pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
    nx.draw(G, 
            pos, 
            node_color=cmap, 
            edge_color=emap,
            node_size=args.size, 
            with_labels=True, 
            ax=ax, 
            font_size=args.nfont, 
            font_color=args.gfcolor)

    return pos
