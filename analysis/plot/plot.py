import numpy as np
import matplotlib.pyplot as plt

from typing     import List

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

def tsp(ax:plt.Axes, label:str, color:str, linestyle:str, step:int, data:List):
    x   = []
    y   = []

    xi  = 1
    buf = []

    for i,element in enumerate(data):
        buf  += [element]
        count = len(buf)

        if (count >= step) or i == (len(data)-1):
                value = np.percentile(buf, 50)
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

def tsp_var(ax:plt.Axes, label:str, color:str, linestyle:str, step:int, data:List):
    x   = []
    y   = []

    xi  = 1
    buf = []

    for i,element in enumerate(data):
        buf  += [element]
        count = len(buf)

        if (count >= step) or i == (len(data)-1):
                value = np.std(buf)
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
