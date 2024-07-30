import os 
import shutil
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

from manager        import RunDict

from typing         import List

from ..analysis     import Analyzer
from .stages        import stages
from .performance   import performance
from .comparison    import comparison

class Plotter():
    def __init__(self, runs, schema, map, dir):
        self.A   = Analyzer(runs, schema,  map)
        self.dir = os.path.join(dir, "plot")

    def setup(self):
        if os.path.isdir(self.dir): 
            shutil.rmtree(self.dir)
        os.mkdir(f"{self.dir}")

    def view(self):
        try:
            plt.show()

        except KeyboardInterrupt:
            print("\nExiting...")
            exit(0)

    def stages(self, run:RunDict):
        root    = self.A.map(run["tree"]["root"])
        name    = run["name"] 
        key     = run['strategy']['key']
        id      = f"{name}-{key}-{root}"

        G = nx.DiGraph()
        G.add_node(self.A.map(run['tree']['root']))
        for i, stage in enumerate(run["stages"]):
            stages(G, run, self.A, stage, i, f"{self.dir}/stages/", file=f"{id}_STAGE_{i + 1}_GRAPH")

    def performance(self, run:RunDict):
        name     = run['name']
        key      = run['strategy']['key']
        tree     = self.A.graph(run)
        for i, _ in enumerate(run["perf"]):
            print(f"PLOTTING TREE[{name}:{key}] PERF[{i + 1}]")
            performance(tree, run, i, self.A, self.dir, file="")

    def comparisons(self):
        cnt   = 0
        trees = []
        lgth  = len(self.A.runs)
        total = ( (lgth * (lgth - 1) ) / 2 )

        for run in self.A.runs:
            trees.append(self.A.graph(run))

        for i in range(lgth):
            for j in range(i + 1, lgth):
                print(f"PLOTTING COMPARISON[{trees[i].name}x{trees[j].name}] {cnt + 1}/{total}")
                comparison(trees[i], trees[j], self.A.runs[i], self.A.runs[j], self.A, self.dir)
                cnt += 1

    def process(self, view:bool=False):
        matplotlib.use('agg')
        self.setup()

        for run in self.A.runs:
            name = run["name"]
            key  = run["strategy"]["key"]
            root = self.A.map(run["tree"]["root"])

            rdir    = f"{name}_{key}_{root}"
            rdir    = os.path.join(self.dir, "jobs", rdir)

            for d in [ "stages", "perf", "comp"]: 
                os.mkdir(f"{rdir}/{d}")

            print(f"PLOTTING TREE[{name}:{key}:{root}]")

            # plot build stages
            self.stages(run)

            # plot tree performance
            self.performance(run)

        # plot tree comparisons
        self.comparisons()

        if view: 
            self.view()
