import subprocess
import os
import shutil
import json

from manager import RunDict

from .analysis      import Analyzer
from .supervisor    import Supervisor
from .utils         import *

def load(dir:str):
    f = "default.json"
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

        if os.path.isdir(path):
            print(f"FOLDER ALREADY EXISTS: {path}")
            return

        gcopy(src, dst)
        extract(path)
        return

    elif args.infra == "docker":
        dir = isdir("infra/terra/docker/modules/default/volume")
        src = finddir(dir=dir, patt=f"treefinder-docker-{args.prefix}")
        dst = isdir("analysis/data")
        shutil.move(src,  dst)
        print(f"MOVED: {src} -> {dst}")
        extract(f"{dst}/{src.split('/')[-1]}")
        return

    else:
        raise NotImplementedError()

def process(args):
    if args.mode == "default" or args.mode == "super":
        dir = isdir("analysis/data")
        dir = finddir(dir=dir, patt=f"treefinder-{args.infra}-{args.prefix}")
        runs   = read(os.path.join(dir, "manager", "logs"))
        schema, map = load(dir)
        S = Supervisor(runs, schema, map, dir, mode=args.mode, multi=(not args.single))
        S.process()

    else: 
        raise NotImplementedError()
