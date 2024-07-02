import glob
import subprocess
import os
import shutil
import json

from manager import RunDict

from .analysis  import Analyzer, UDP
from .plot      import Plotter
from .slides    import export
from .utils     import *

def load(dir:str, infra:str):
    f = "docker.json" if infra == "docker" else "default.json"
    file = os.path.join(dir, f)
    map  = {}

    with open(file, 'r') as f: 
        schema = json.load(f)

    map[schema["addrs"][0]] = "M_0"
    for i,addr in enumerate(schema["addrs"][1:]):
        map[addr] = f"W_{i}"

    return schema, map

def read(dir:str):
    file = os.path.join(dir, "events.log")
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

def gpull(prefix:str):
    command = "gcloud storage ls gs://exp-results-nyu-systems-multicast/"
    ret     = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)
    arr     = ret.stdout.strip().split('\n')
    for a in arr:
        if prefix in a:
            print(f"PULLING {a}")
            return a

    raise RuntimeError(f"No bucket found on GCP matching: {prefix}")

def gcopy(src:str, dst:str, bucket:str="gs://exp-results-nyu-systems-multicast"):
    os.system(f"gcloud storage cp --recursive {bucket}/{src}* {dst}")

def pull(args):
    if args.infra == "gcp":
        res = gpull(args.prefix)
        src = res.split('/')[-2]
        dst = os.path.join(os.getcwd(), "analysis", "data")
        path = os.path.join(os.getcwd(), "analysis", "data", src)
        file = os.path.join(path, "results.tar.gz", "results.tar.gz")
        if not os.path.isdir(path):
            gcopy(src, dst)
            if os.path.exists(file):
                shutil.move(file, f"{path}/tmp.tar.gz")
                shutil.rmtree(os.path.join(path, "results.tar.gz"))
                shutil.move(f"{path}/tmp.tar.gz", f"{path}/results.tar.gz")
                extract(f"{path}")
            else:
                raise RuntimeError(f"results.tar.gz not found in {path}")
        else:
            raise RuntimeError(f"Bucket: {path} has been pulled already")
        return

    elif args.infra == "docker":
        dir = isdir("infra/terra/docker/modules/default/volume")
        src = find(dir=dir, pattern=f"treefinder-docker-{args.prefix}")
        dst = isdir("analysis/data")
        shutil.move(src,  dst)
        print(f"MOVED: {src} -> {dst}")
        extract(f"{dst}/{src.split('/')[-1]}")
        return

    else:
        raise NotImplementedError()

def process(args):
    if args.mode == "default":
        dir = isdir("analysis/data")
        dir = find(dir=dir, pattern=f"treefinder-{args.infra}-{args.prefix}")
        dir = os.path.join(dir, "logs")
        runs   = read(dir)
        schema, map = load(dir, args.infra)
        A = Analyzer(runs, schema,  map)
        P = Plotter(A)
        P.plot(dir, view=args.view)

    elif args.mode == "udp":
        dir  = isdir("infra/terra/docker/modules/default/volume")
        csvs = glob.glob(os.path.join(dir, '*.csv'))
        U = UDP()
        U.process(csvs)

    else: 
        raise NotImplementedError()

def generate(args):
    dir     = isdir("analysis/data")
    dir     = find(dir=dir, pattern=f"treefinder-{args.infra}-{args.prefix}")
    dir     = os.path.join(dir, "logs", "plot")
    export(dir)
