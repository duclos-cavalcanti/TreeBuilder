import os
import csv
import glob

import numpy as np
import shutil

import matplotlib.pyplot as plt
import matplotlib

# from tabulate       import tabulate
# from termcolor      import colored, cprint
from rich.text      import Text
from rich.table     import Table
from rich.console   import Console
from rich           import box

from manager import RunDict, ResultDict, ItemDict
from typing import List, Dict, TypedDict

from ..utils    import *
from ..plot     import cdf, tsp, COLORS, MARKERS, LINESTYLES

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
    def __init__(self, runs:List[RunDict], schema:Dict, map:Dict, dir:str):
        self.dir    = dir
        self.runs   = runs
        self.schema = schema
        self.M      = map

    def setup(self):
        path = os.path.join(self.dir, "super")
        if os.path.isdir(path): 
            shutil.rmtree(path)
        os.mkdir(path)

    def view(self):
        try:
            plt.show()

        except KeyboardInterrupt:
            print("\nExiting...")
            exit(0)

    def map(self, addr:str):
        return self.M[addr.split(":")[0]]

    def name(self, addr:str):
        idx = self.schema["addrs"].index(addr.split(":")[0])
        return self.schema["names"][idx]

    def search(self, stage:ResultDict, items:List[ItemDict]):
        ret     = []
        id      = stage["id"]
        addrs   = [ i["addr"].split(":")[0] for i in items ]
        names   = [ self.name(i["addr"])    for i in items ]
        mnames  = [ self.map(i["addr"])     for i in items ]

        for i,name in enumerate(names):
            files, fnames = globfiles(os.path.join(self.dir, f"{name}", "logs"), patt="*.csv")

            assert any([ addrs[i] in n for n in fnames ]), f"ADDR: {addrs[i]} NOT FOUND IN FILES"
            assert any([ "child"  in n for n in fnames ]), f"NO CHILD JOBS IN FILES"

            job = Job(name=names[i], mname=mnames[i], result=stage, item=items[i])
            idx = findfile(files, id, patt="child")
            data = [ float(row[1]) for row in read_csv(files[idx]) ]
            job.parse(data)
            ret.append(job)

        return ret

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

    def tsp(self, tree:str, name:str, stage:ResultDict, i:int, jobs:List[Job]):
        select = [ s.split(":")[0] for s in stage["selected"] ]
        parent = self.map(stage["root"])
        rate   = stage["rate"]
        dur    = stage["duration"]

        fig1, ax = plt.subplots()
        handles  = []
        
        for j,job in enumerate(jobs):
            label     = job.mname
            data      = job.data
            color     = COLORS[ j+1 % len(COLORS) ]
            linestyle = LINESTYLES[ j+1 % len(LINESTYLES) ]
        
            if job.addr in select: linestyle = '-'
            else:                  color = 'gray'
        
            line   = tsp(ax, label=label, color=color, linestyle=linestyle, step=rate, data=data)
            handle = plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label)
            handles.append(handle)
        
        fig1.suptitle(f"{tree} - STAGE[{i + 1}]", fontweight='bold')
        ax.set_title(f"TIME SERIES MEDIAN OWD LATENCY")
        ax.set_ylabel("OWD(us)")
        ax.set_xlabel("t(s)")
        
        handles += [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Parent: {parent}"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Rate: {rate}/sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Period: {dur}sec"),
        ]
        
        for _ in range((2*len(jobs)) - (len(handles))):
            handles.append(plt.Line2D([0], [0], marker='s', color='w', alpha=0, label=f" "))
        
        ax.legend(handles=handles, loc='lower right', fancybox=True, fontsize=10, ncol=2)
        fig1.savefig(f"{self.dir}/super/{name}-TSP.png", format="png")

    def cdf(self, tree:str, name:str, stage:ResultDict, i:int, jobs:List[Job]):
        select = [ s.split(":")[0] for s in stage["selected"] ]
        parent = self.map(stage["root"])
        rate   = stage["rate"]
        dur    = stage["duration"]

        fig1, ax = plt.subplots()
        handles  = []
        
        for j,job in enumerate(jobs):
            label     = job.mname
            data      = job.data
            color     = COLORS[ j+1 % len(COLORS) ]
            linestyle = LINESTYLES[ j+1 % len(LINESTYLES) ]
        
            if job.addr in select: linestyle = '-'
            else:                  color = 'gray'
        
            line   = cdf(ax, label=label, color=color, linestyle=linestyle, data=data)
            handle = plt.Line2D([0], [0], color=color, linestyle=linestyle, label=label)
            handles.append(handle)
        
        fig1.suptitle(f"{tree} - STAGE[{i + 1}]", fontweight='bold')
        ax.set_title(f"PROBE OWD LATENCY")
        ax.set_ylabel("CDF")
        ax.set_xlabel("OWD(us)")
        
        handles += [
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Parent: {parent}"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Rate: {rate}/sec"),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='black', markersize=8, label=f"Period: {dur}sec"),
        ]
        
        for _ in range((2*len(jobs)) - (len(handles))):
            handles.append(plt.Line2D([0], [0], marker='s', color='w', alpha=0, label=f" "))
        
        ax.legend(handles=handles, loc='lower right', fancybox=True, fontsize=10, ncol=2)
        fig1.savefig(f"{self.dir}/super/{name}-CDF.png", format="png")

    def process(self):
        self.setup()
        matplotlib.use('GTK3Agg')

        C = Console()

        for run in self.runs:
            root  = self.map(run["tree"]["root"])
            name  = run["name"] + "-" + run["strategy"]["key"]
            T     = Table(title=f"{name.upper()}", show_header=True, box=box.ROUNDED)

            for header in [ "Stage", "Parent", "Tables" ]: 
                T.add_column(header)

            for i,stage in enumerate(run["stages"]):
                parent = self.map(stage["root"])
                jobs   = self.search(stage, stage["items"])
                table  = self.table(stage, jobs)
                T.add_row(*[ f"STAGE_{i}: {stage['id']}", str(parent), table ])
                # C.print(table)

                self.cdf(name, f"{name}-{root}-STAGE_{i}", stage, i, jobs)
                self.tsp(name, f"{name}-{root}-STAGE_{i}", stage, i, jobs)

            C.print(T)
            self.view()
            return

