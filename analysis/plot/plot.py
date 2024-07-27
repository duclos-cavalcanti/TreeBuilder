import numpy as np
import matplotlib.pyplot as plt

from typing     import List

# from manager    import ResultDict
# from .utils     import MARKERS, COLORS, LINESTYLES

def cdf(ax:plt.Axes, label:str, color:str, linestyle:str, data:List):
    # percentiles to show
    y = [ round(i, 2) for i in list(np.arange(1, 100, 1)) ]

    # data
    x = np.percentile(data, y)

    line = ax.plot(x, 
                    y, 
                    label=label, 
                    color=color,
                    linestyle=linestyle)

    ax.set_xlim(0, max(x) + 50)
    ax.set_ylim(0, 100)

    return line

def tsp(ax:plt.Axes, label:str, color:str, linestyle:str, step:int, data:List):
    x   = []
    y   = []

    xi  = 0
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
                   linestyle=linestyle)

    ax.set_xlim(0, max(x))
    ax.set_ylim(0, max(y) + 50)

    return line
