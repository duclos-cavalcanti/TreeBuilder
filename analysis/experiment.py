import os
import json
import csv
import glob

from typing  import Dict, List
from manager import RunDict, ResultDict

import multiprocessing as mp
import networkx as nx

class Experiment():
    def __init__(self, dir:str):
        self.dir    = dir
        self.schema = self.load(dir) 
        self.runs   = self.read(dir=os.path.join(dir, "manager", "logs"))
        self.jobs   = self.find()

    def map(self, addr:str):
        return self.schema["map"][addr.split(":")[0]]

    def description(self, run:RunDict):
        ret  = ""
        name = run["name"]

        if "LEMON" in name: 
            epsilon = run["parameters"]["epsilon"]
            max_i   = run["parameters"]["max_i"]
            conv    = run["parameters"]["converge"]
            ret     = f"EPS={epsilon}, MAX={max_i}, CONV={conv}"
        else:
            if run['strategy']['key'] == "heuristic":
                ret = f"Expr: (0.7 x stddev) + (0.3 * p90)"

        return ret

    def worst(self, results:List[ResultDict]):
        i       = 0 
        max     = 0
        for idx, result in enumerate(results):
            latency = result["items"][0]["p90"]
            if latency > max: 
                max = latency
                i   = idx

        return i

    def graph(self, run:RunDict):
        G       = nx.DiGraph()
        name    = run['name']
        root    = run["tree"]["root"]
        key     = run['strategy']['key']

        if   "LEMON" in name: G.name = f"{name}"
        elif name == "RAND":  G.name = f"{name}"
        else:                 G.name = f"{name}-{key}"

        G.add_node(self.map(root))

        if len(run['stages']) > 0 and "REBUILD" not in name:
            for i, result in enumerate(run['stages']):
                parent   = self.map(result['root'])
                children = [ self.map(s) for s in result['selected'] ]
            
                for child in children:
                    G.add_edge(parent, child) 

        else:
            parents = [ self.map(root) ]
            nodes   = run['tree']['nodes'][1:]
            
            for i in range(0, len(nodes), run['tree']['fanout']):
                p = parents[0]
                parents.pop(0)
            
                for j in range(run['tree']['fanout']):
                    child = self.map(nodes[i + j])
                    G.add_edge(p, child) 
                    parents.append(child)

        return G

    def run(self, run:RunDict):
        name = run["name"]
        key  = run['strategy']['key']
        root = self.map(run["tree"]["root"])
        tree = f"{name}-{key}"
        id   = f"{name}-{key}-{root}"
        return name, key, tree, id

    def load(self, dir:str):
        f = "default.json"
        file = os.path.join(dir, f)
    
        with open(file, 'r') as f: 
            schema = json.load(f)
    
        schema["map"] = {}
        schema["map"][schema["addrs"][0]] = "M_0"
        for i,addr in enumerate(schema["addrs"][1:]):
            schema["map"][addr] = f"W_{i}"
    
        return schema

    def read(self, dir:str):
        file   = os.path.join(dir, "events.log")
        events = []
        with open(file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    events.append(event)
    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {line.strip()} - {e}")
    
        runs:List[RunDict]   = []
        for e in events:
            if "RUN" in e:
                runs.append(RunDict(e["RUN"]))
    
        return runs

    def search(self, result:ResultDict, patt:str="child"):
        id      = self.fix_id(result["id"])
        items   = result["items"]
        addrs   = []
        names   = []
        data    = []

        for i in items:
            raddr = i["addr"].split(":")[0]
            names.append(self.schema["names"][self.schema["addrs"].index(raddr)])
            addrs.append(raddr)

        for i,name in enumerate(names):
            files  = glob.glob(os.path.join(self.dir, f"{name}", "logs", "*.csv"))
            fnames = [ f.split("/")[-1] for f in files ]
    
            assert any([ addrs[i] in n for n in fnames ]), f"ADDR: {addrs[i]} NOT FOUND IN FILES FROM {name.upper()}"
            assert any([ patt     in n for n in fnames ]), f"NO {patt.upper()} JOBS IN FILES FROM {name.upper()}"
    
            idx = -1
            for i,f in enumerate(files):
                name = f.split("/")[-1]
                if patt in name and id in name:
                    idx = i 
                    break
    
            assert idx >= 0, f"NO FILE FOUND MATCHING: {patt}"

            rows = []
            with open(files[idx], 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader: 
                    rows.append(row)

            data.append([ float(row[1]) for row in rows ])

        return result["id"], data 

    def find(self):
        manager = mp.Manager()
        ret     = manager.dict()
        lock    = mp.Lock()
        procs   = []
    
        def worker(d:dict, run:RunDict, lock):
            name, key, tree, id = self.run(run)
            if "BEST" in name or "WORST" in name:
                for stage in run["stages"]:
                    k, data = self.search(stage, "child")
                    with lock:
                        d[k] = data
                        print(f"PARSED RESULT[{stage['id']}] from RUN[{id}]")

            for perf in run["perf"]:
                k, data = self.search(perf, "mcast")
                with lock:
                    d[k] = data
                    print(f"PARSED RESULT[{perf['id']}] from RUN[{id}]")
    
        for run in self.runs:
            p = mp.Process(target=worker, args=(ret, run, lock))
            procs.append(p)
            p.start()
    
        for p in procs:
            p.join()

        return ret

    def fix_id(self, id_:str):
        id = id_
        match id_:
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
        return id
    
