import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import networkx as nx

from matplotlib.table   import table
from typing             import List
from manager            import ResultDict, RunDict, ItemDict

from . import utils
from . import plot

class Plotter():
    def __init__(self, E, ARGS):
        self.EXPERIMENT = E
        self.ARGS       = ARGS
