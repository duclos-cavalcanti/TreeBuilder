import os 
import shutil

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
        for d in [ "stages", "perf", "comp"]: 
            os.mkdir(f"{self.dir}/{d}")

    def view(self, command="feh -r"):
        try:
            os.system(f"cd {self.dir} && {command}")

        except KeyboardInterrupt:
            print("Exiting...")

    def stages(self, run:RunDict):
        stages(run, self.A, self.dir)

    def performance(self, run:RunDict):
        name     = run['name']
        key      = run['strategy']['key']
        tree     = self.A.graph(run)
        for i, _ in enumerate(run["perf"]):
            print(f"PLOTTING TREE[{name}:{key}] PERF[{i + 1}]")
            performance(tree, run, i, self.A, self.dir)

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

    def plot(self, view:bool=False):
        self.setup()

        for run in self.A.runs:
            name = run["name"]
            key  = run["strategy"]["key"]
            root = self.A.map(run["tree"]["root"])

            print(f"PLOTTING TREE[{name}:{key}:{root}]")

            # plot build stages
            self.stages(run)

            # plot tree performance
            self.performance(run)

        # plot tree comparisons
        self.comparisons()

        if view: 
            print(f"VIEWING IMAGES")
            self.view()
