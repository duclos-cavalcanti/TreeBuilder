import numpy as np
import matplotlib.pyplot as plt

from typing     import List

TRAFOS = {
    "p90":          lambda buf, x:     np.percentile(buf, 90),
    "p50":          lambda buf, x:     np.percentile(buf, 50),
    "mad":          lambda buf, x:     np.median(np.absolute(buf - np.median(x))),
    "iqr":          lambda buf, x:     np.quantile(buf, 0.75) - np.quantile(buf, 0.25),
    "stddev":       lambda buf, x:     np.median(np.absolute(buf - np.mean(x))),
    "pos_stddev":   lambda buf, x:     np.median(np.absolute([ b for b in buf if b > np.mean(x) ] - np.mean(x))),
}


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

def tsp(ax:plt.Axes, label:str, color:str, linestyle:str, step:int, data:List, traf):
    x   = []
    y   = []

    xi  = 1
    buf = []

    for i,element in enumerate(data):
        buf  += [element]
        count = len(buf)

        if (count >= step) or i == (len(data)-1):
                value = traf(buf, data)
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
