import os
import csv
import glob

import numpy as np
import shutil

import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib
import networkx as nx

from rich.text      import Text
from rich.table     import Table
from rich.console   import Console
from rich           import box

from manager import RunDict, ResultDict, ItemDict
from typing import List, Dict, TypedDict

from ..utils        import *
from ..plot         import *
from ..analysis     import Analyzer

class Job():
    def __init__(self, name:str, mname:str, result:ResultDict, item:ItemDict):
        self.id             = result["id"]
        self.name           = name
        self.mname          = mname
        self.addr           = item["addr"].split(":")[0]
        self.rate           = result["rate"] 
        self.duration       = result["duration"]
        self.item:ItemDict  = item
        self.ritem          = {}
        self.data           = []

    def parse(self, data):
        self.data = data
        d       = np.array(data)
        p90     = float(np.percentile(d, 90))
        p75     = float(np.percentile(d, 75))
        p50     = float(np.percentile(d, 50))
        p25     = float(np.percentile(d, 25))
        mean    = float(np.mean(d))
        std_dev = float(np.std(d))

        item:ItemDict = {
            "addr":     self.addr,
            "p90":      p90,
            "p75":      p75,
            "p50":      p50, 
            "p25":      p25,
            "stddev":   std_dev,
            "mean":     mean,
            "recv":     0,
        }

        self.ritem = item

class Supervisor():
    def __init__(self, runs:List[RunDict], schema:Dict, map:Dict, dir:str, mode:str, multi:bool=False):
        self.A     = Analyzer(runs, schema,  map)
        self.dir   = dir
        self.mode  = mode
        self.multi = multi

    def setup(self):
        path = os.path.join(self.dir, "plot")
        if os.path.isdir(path): 
            shutil.rmtree(path)
        os.mkdir(path)

    def show(self):
        try:
            plt.show()

        except KeyboardInterrupt:
            print("\nExiting...")
            exit(0)

    def search(self, stage:ResultDict, items:List[ItemDict], patt:str="child"):
        ret     = []
        id      = stage["id"]
        root    = self.A.name(stage["root"])
        addrs   = [ i["addr"].split(":")[0] for i in items ]
        names   = [ self.A.name(i["addr"])    for i in items ]
        mnames  = [ self.A.map(i["addr"])     for i in items ]

        # fixing bug after the fact
        match id:
            # BEST P-90 ROOT: 10.1.25.10
            case "EOCxiXhTfn": id = "IyuosKLoHy"
            case "stqtHpzbDv": id = "DNSAxLstSG"
            case "qPJIsuGmgW": id = "utroKCTgjr"

            # BEST P-90 ROOT: 10.1.25.25
            case "NLdaaTNBbd": id = "yvdepcuiLp"
            case "jPDBrvFTPQ": id = "BvTVwdkQEj"
            case "zWtWGOQjWi": id = "OcjJeNxtMA"

            # BEST P-50 ROOT: 10.1.25.10
            case "SCjhNtixpT": id = "bmxljJmKat"
            case "yzqCuIOlnF": id = "QiVvplnIlB"
            case "nQeaewDqjd": id = "LBHlvIsnqp"

            # BEST P-50 ROOT: 10.1.25.25
            case "qBkRKCCbwd": id = "tlxcuKMJAN"
            case "hGuLgncoLC": id = "RXvgMTiIyc"
            case "XmIsvyZTMj": id = "pcmLRABrAY"

            # BEST HEURISTIC ROOT: 10.1.25.10
            case "awttVGAnXB": id = "gwCcshFSWz"
            case "cZpZhBCrbZ": id = "iJAoawYemH"
            case "TBVgEBphOq": id = "dhhuRcxOru"

            # BEST HEURISTIC ROOT: 10.1.25.25
            case "aAVoXDBuBt": id = "hVGXCEBFWN"
            case "OkYIcYnJkI": id = "eumbOFwJBc"
            case "OsLsqVNBkm": id = "buHPYUVmnF"

            # WORST P-90 ROOT: 10.1.25.10
            case "JTJnHEisYX": id = "cjeXOuAaZj"
            case "ZlNLZzPdvy": id = "IqMTLYXecW"
            case "gYSEeAZqfN": id = "IvRoHFttxw"

            # WORST P-90 ROOT: 10.1.25.25
            case "RyzJDytGQl": id = "ZtDOglFVwI"
            case "oaHdufOIsw": id = "JpoCBaSdZr"
            case "HCFwvJyntn": id = "MOgYEuqCrK"

            # WORST P-50 ROOT: 10.1.25.10
            case "fkeXBzRHRl": id = "XzzyJWqzUw"
            case "FolfwGuYyG": id = "qWuMriaEjw"
            case "quBYuCsjyO": id = "AQfDeilhNU"

            # WORST P-50 ROOT: 10.1.25.25
            case "saceFFNcLL": id = "qhacFWBjpk"
            case "ioAWxUHKSC": id = "aPqKNOBlLH"
            case "lWfwiBpClM": id = "YHOzXtJSYf"

            # RAND ROOT: 10.1.25.10
            case "rlyqTuGkba": id = "OMDxSoDgEU"
            case "WSzpRhfmxJ": id = "EQsBjuOzhJ"
            case "vtstRBxwQA": id = "kGuPrHfaNz"

            # RAND ROOT: 10.1.25.25
            case "cGAVBklEtn": id = "DTLbjpcxss"
            case "LreykaIhVx": id = "nUJOAHAAhz"
            case "sskKCRriLZ": id = "DekRLqkiIO"

            # LEMON ROOT: 10.1.25.3 eps=1e-4 n=1000
            case "OQIfbcoAPT": id = "aDTkZNfBTv"
            case "BjcDoGPpSX": id = "vvyybotxks"
            case "aAvYhhlfgs": id = "LHeRBmcWAx"

            # LEMON ROOT: 10.1.25.6 eps=5.5e-05 n=10000
            case "BEduhFpxGS": id = "PFXdEIseGB"
            case "ZSaujGamsT": id = "vGFAuLWrva"
            case "igsQlUMxcf": id = "WzCPLchnIZ"

            case _: pass

        # print(f"SEARCHING {patt.upper()} JOBS[{id}] FROM {root.upper()}")
        # print(f"WORKERS: {names}")

        for i,name in enumerate(names):
            files, fnames = globfiles(os.path.join(self.dir, f"{name}", "logs"), patt="*.csv")

            assert any([ addrs[i] in n for n in fnames ]), f"ADDR: {addrs[i]} NOT FOUND IN FILES FROM {name.upper()}"
            assert any([ patt     in n for n in fnames ]), f"NO {patt.upper()} JOBS IN FILES FROM {name.upper()}"

            job = Job(name=names[i], mname=mnames[i], result=stage, item=items[i])
            idx = findfile(files, id, patt=patt)

            # print(f"FOUND FILE: {fnames[idx]} FROM {name.upper()}")

            data = [ float(row[1]) for row in read_csv(files[idx]) ]
            job.parse(data)
            ret.append(job)

        return ret

    def analyze(self, jobs:List[Job]):
        ret  = True
        idxs = [[]]
        keys = [ 
                "p90", 
                "p75", 
                "p50", 
                "mean", 
                "stddev"
        ]

        for i,job in enumerate(jobs):
            item  = job.item
            ritem = job.ritem

            for j,k in enumerate(keys):
                ref = item[k]
                val = ritem[k]

                if not bounded(reference=ref, value=val, perc=2): 
                    ret = False 
                    idxs[i].append(j)

        return ret, idxs

    def color(self, data, style):
        return Text(str(data), style=style)

    def table(self, stage:ResultDict, jobs:List[Job]):
        sel     = [ s.split(":")[0] for s in stage["selected"] ]
        keys = [ 
                "p90", 
                "p75", 
                "p50", 
                "mean", 
                "stddev"
        ]
        
        table   = Table(show_header=True, box=box.ROUNDED)
        headers = [ "addr", "p99" ] + keys + [ "recv", "rate", "duration"]
        
        for header in headers: 
            table.add_column(header)

        max_x    = 0
        max_y    = 0
        
        for i,job in enumerate(jobs):
            item  = job.item
            ritem = job.ritem
        
            data = []
            if job.addr in sel: data.append(self.color(job.mname, "green"))
            else:               data.append(self.color(job.mname, "red"))

            p99 = float(np.percentile(job.data, 99))
            data.append(rnd(p99))

            for k in keys:
                ref = item[k]
                val = ritem[k]
        
                string = f"R: {rnd(ref)} x {rnd(val)}"
        
                if not bounded(reference=ref, value=val, perc=2): 
                    string = self.color(string, "red")
                else:
                    string = f"{rnd(val)}"
        
        
                data.append(string)
            

            size  = len(job.data)
            rate  = job.rate
            dur   = job.duration
            total = rate * dur

            data += [ rnd(100 * float(size / total)), str(rate), str(dur)]
            table.add_row(*data)

        return table

    def tsp(self, title:str, dir:str, file:str, result:ResultDict, i:int, jobs:List[Job], typ:str):
        select = [ s.split(":")[0] for s in result["selected"] ]
        parent = self.A.map(result["root"])
        rate   = result["rate"]
        dur    = result["duration"]

        fig1, ax = plt.subplots(figsize=(28, 16))
        handles  = []
        max_x    = 0
        max_y    = 0
        
        for j,job in enumerate(jobs):
            label     = job.mname
            data      = job.data
            cnt       = j

            if j >= (len(LINESTYLES) - 1): cnt = 0

            color     = COLORS[ cnt+1 % len(COLORS) ]
            linestyle = LINESTYLES[ cnt+1 % len(LINESTYLES) ]
        
            if job.addr in select: linestyle = '-'
            else:                  color = 'gray'
        
            if typ.upper() == "MEDIAN":
                line, max_xi, max_yi   = tsp(ax, label=label, color=color, linestyle=linestyle, step=rate, data=data)
            else:
                line, max_xi, max_yi   = tsp_var(ax, label=label, color=color, linestyle=linestyle, step=rate, data=data)

            max_x = max(max_x, max_xi)
            max_y = max(max_y, max_yi)

            handle = plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label)
            handles.append(handle)
        
        fig1.suptitle(f"{title}", fontsize=pargs.tfont, fontweight='bold')
        ax.set_title(f"TIME SERIES {typ.upper()} OWD LATENCY", fontsize=pargs.nfont + 2)

        ax.set_xlim(0, max_x + 1)
        ax.set_ylim(0, max_y * 1.5)
        ax.set_xticks(np.arange(1, max_x + 1, 1))

        ax.set_ylabel("OWD(us)", fontsize=pargs.nfont)
        ax.set_xlabel("t(s)", fontsize=pargs.nfont)

        ax.tick_params(axis='x', labelsize=pargs.nfont - 1)
        ax.tick_params(axis='y', labelsize=pargs.nfont - 1)
        
        handles += [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Sender: {parent}"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Rate: {rate}/sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Period: {dur}sec"),
        ]
        
        for _ in range((2*len(jobs)) - (len(handles))):
            handles.append(plt.Line2D([0], [0], marker='s', color='w', alpha=0, label=f" "))
        
        ax.legend(handles=handles, loc='best', fancybox=True, fontsize=pargs.nfont + 1, ncol=2)
        fig1.savefig(f"{dir}/{file}.png", format="png")
        return fig1

    def cdf(self, title:str, dir:str, file:str, result:ResultDict, i:int, jobs:List[Job]):
        select = [ s.split(":")[0] for s in result["selected"] ]
        parent = self.A.map(result["root"])
        rate   = result["rate"]
        dur    = result["duration"]

        # fig1, ax = plt.subplots()
        fig1, ax = plt.subplots(figsize=(pargs.w, pargs.h))
        handles  = []
        max_x    = 0
        max_y    = 0
        
        for j,job in enumerate(jobs):
            label     = job.mname
            data      = job.data
            cnt       = j

            if j >= (len(LINESTYLES) - 1): cnt = 0

            color     = COLORS[ cnt+1 % len(COLORS) ]
            linestyle = LINESTYLES[ cnt+1 % len(LINESTYLES) ]
        
            if job.addr in select: linestyle = '-'
            else:                  color = 'gray'
        
            line, max_xi, max_yi = cdf(ax, label=label, color=color, linestyle=linestyle, data=data)
            handle = plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label)
            handles.append(handle)

            max_x = max(max_x, max_xi)
            max_y = max(max_y, max_yi)
        
        fig1.suptitle(f"{title}", fontsize=pargs.tfont, fontweight='bold')
        ax.set_title(f"PROBE OWD LATENCY", fontsize=pargs.nfont + 2)

        ax.set_xlim(0, max_x + 50)
        ax.set_ylim(0, 100)

        ax.set_ylabel("CDF", fontsize=pargs.nfont)
        ax.set_xlabel("OWD(us)", fontsize=pargs.nfont)

        ax.tick_params(axis='x', labelsize=pargs.nfont - 1)
        ax.tick_params(axis='y', labelsize=pargs.nfont - 1)
        
        handles += [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Sender: {parent}"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Rate: {rate}/sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Period: {dur}sec"),
        ]
        
        for _ in range((2*len(jobs)) - (len(handles))):
            handles.append(plt.Line2D([0], [0], marker='s', color='w', alpha=0, label=f" "))
        
        ax.legend(handles=handles, loc='best', fancybox=True, fontsize=pargs.nfont + 1, ncol=2)
        fig1.savefig(f"{dir}/{file}.png", format="png")
        return fig1

    def stages(self, tree:str, id:str, run:RunDict, dir:str, lock):
        name    = run["name"] 
        figs    = []

        C = Console()

        if "RAND" not in name and "LEMON" not in name:
            G = nx.DiGraph()
            G.add_node(self.A.map(run['tree']['root']))

            T = Table(title=f"{tree.upper()} STAGES", show_header=True, box=box.ROUNDED)
            for d in [ "Iteration", "Root", "Data"]: 
                T.add_column(d)

            R = Table(title=f"{tree.upper()} STAGES", show_header=True, box=box.ROUNDED)
            for d in [ "ID", "PASS"]: 
                R.add_column(d)
        
            for i,stage in enumerate(run["stages"]):
                parent = self.A.map(stage["root"])
                jobs   = self.search(stage, stage["items"], patt="child")

                # table  = self.table(stage, jobs)
                # table.title = f"STAGE[{i + 1}]: {id}"
                # C.print(table)
                # T.add_row(*[ f"STAGE_{i + 1}: {stage['id']}", str(parent), table ])

                ok, _ = self.analyze(jobs)
                if not ok: string = self.color("FALSE", "red")
                else:      string = self.color("TRUE", "green")

                R.add_row(*[ f"STAGE_{i + 1}: {stage['id']}", string ])
            
                fig_a = self.cdf(title=f"{tree} - STAGE[{i + 1}]", dir=f"{dir}/stages", file=f"{id}_STAGE_{i + 1}_CDF", result=stage, i=i, jobs=jobs)
                fig_b = self.tsp(title=f"{tree} - STAGE[{i + 1}]", dir=f"{dir}/stages", file=f"{id}_STAGE_{i + 1}_TSP", result=stage, i=i, jobs=jobs, typ="MEDIAN")
                fig_c = self.tsp(title=f"{tree} - STAGE[{i + 1}]", dir=f"{dir}/stages", file=f"{id}_STAGE_{i + 1}_VAR", result=stage, i=i, jobs=jobs, typ="STDDEV")
                fig_d = stages(G, run, self.A, stage, i, dir=f"{dir}/trees/stages", file=f"{id}_STAGE_{i + 1}_GRAPH")

                for f in [ fig_a, fig_b, fig_c, fig_d ]:
                    figs.append(f)

                for f in figs:
                    plt.close(f)

            with lock:
                C.print(R)
        
    def evals(self, tree:str, id:str, run:RunDict, dir:str, lock):
        figs    = []

        C = Console()
        G = self.A.graph(run)

        T = Table(title=f"{tree.upper()} EVALS", show_header=True, box=box.ROUNDED)
        for d in [ "Iteration", "Root", "Data"]: 
            T.add_column(d)

        R = Table(title=f"{tree.upper()} EVALS", show_header=True, box=box.ROUNDED)
        for d in [ "ID", "PASS"]: 
            R.add_column(d)
        
        for i, perf in enumerate(run["perf"]):
            parent = self.A.map(perf["root"])
            jobs   = self.search(perf, perf["items"], patt="mcast")

            # table  = self.table(perf, jobs)
            # table.title = f"EVAL[{i + 1}]: {id}"
            # C.print(table)
            # T.add_row(*[ f"EVAL_{i + 1}: {perf['id']}", str(parent), table ])

            ok, _ = self.analyze(jobs)
            if not ok: string = self.color("FALSE", "red")
            else:      string = self.color("TRUE", "green")

            R.add_row(*[ f"EVAL_{i + 1}: {perf['id']}", string ])
        
            fig_a = self.cdf(title=f"{tree} Evaluation[{i + 1}]", dir=f"{dir}/eval", file=f"{id}_EVAL_{i + 1}_CDF", result=perf, i=i, jobs=jobs)
            fig_b = self.tsp(title=f"{tree} Evaluation[{i + 1}]", dir=f"{dir}/eval", file=f"{id}_EVAL_{i + 1}_TSP", result=perf, i=i, jobs=jobs, typ="MEDIAN")
            fig_c = self.tsp(title=f"{tree} Evaluation[{i + 1}]", dir=f"{dir}/eval", file=f"{id}_EVAL_{i + 1}_VAR", result=perf, i=i, jobs=jobs, typ="STDDEV")
            fig_d = performance(G, run, i, self.A, dir=f"{dir}/trees/eval", file=f"{id}_EVAL_{i + 1}_GRAPH")

            for f in [ fig_a, fig_b, fig_c, fig_d ]:
                figs.append(f)

            for f in figs:
                plt.close(f)

        with lock:
            C.print(R)

    def compare(self, i:int, runs:List, dirs:List, lock):
        root_i    = self.A.map(runs[i]["tree"]["root"])
        tree_i    = self.A.graph(runs[i])
        name_i    = runs[i]["name"] 
        key_i     = runs[i]['strategy']['key']
        id_i      = f"{name_i}-{key_i}-{root_i}"
        dir_i     = dirs[i] + f"/trees/cmp"

        total = len(runs)

        C = Console()
        R = Table(title=f"COMPARISON[{i + 1}/{total}]", show_header=True, box=box.ROUNDED)

        for d in [ "TREE_I", "TREE_J", "COMPLETE"]: 
            R.add_column(d)

        for j in range(len(runs)):
            if j == i: 
                continue

            root_j    = self.A.map(runs[j]["tree"]["root"])
            tree_j    = self.A.graph(runs[j])
            name_j    = runs[j]["name"] 
            key_j     = runs[j]['strategy']['key']
            id_j      = f"{name_j}-{key_j}-{root_j}"

            R.add_row(*[ id_i, id_j, self.color("TRUE", "green") ])

            dir  = dir_i
            file = f"{id_i}x{id_j}_CMP_GRAPH"
            fig  = comparison(tree_i, tree_j, runs[i], runs[j], self.A, dir, file)

            plt.close(fig)

        with lock:
            C.print(R)

    def process(self):
        self.setup()
        matplotlib.use('agg')

        runs  = []
        dirs  = []
        procs = []
        lock = mp.Lock()

        # pargs  = PlotArgs(w=28, h=16, f=16, nf=18, tf=24, s=2100)

        def worker(runs:List, dirs:List, i:int, L):
            run     = runs[i]
            dir     = dirs[i]
            name    = run["name"] 
            key     = run['strategy']['key']
            root    = self.A.map(run["tree"]["root"])
            tree    = f"{name}-{key}"
            id      = f"{name}-{key}-{root}"
            self.stages(tree=tree, id=id, run=run, dir=f"{dir}", lock=L)
            self.evals(tree=tree, id=id,  run=run, dir=f"{dir}", lock=L)
            self.compare(i=i, runs=runs, dirs=dirs, lock=L)

        for i,run in enumerate(self.A.runs):
            name    = run["name"] 
            key     = run['strategy']['key']
            root    = self.A.map(run["tree"]["root"])
            id      = f"{name}-{key}-{root}"
            rdir    = os.path.join(self.dir, "plot", id)

            os.mkdir(rdir)
            for d in [ "trees", "trees/stages", "trees/eval", "trees/cmp", "stages", "eval"]:
                os.mkdir(f"{rdir}/{d}")

            runs.append(run)
            dirs.append(rdir)

        for i, run in enumerate(runs):
            p = mp.Process(target=worker, args=(runs, dirs, i, lock))
            procs.append(p)

            if self.multi: 
                p.start()

        for p in procs:
            if not self.multi: 
                p.start()
            p.join()
