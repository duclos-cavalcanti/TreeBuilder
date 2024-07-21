from .utils  import *
from manager import Timer, TreeBuilder, RunDict, StrategyDict, ParametersDict, TreeDict, ResultDict, TimersDict

import os
import json

from datetime import datetime

def compress(dst:str):
    command = "tar --exclude=jasper \
		       --exclude=project.tar.gz \
		       --exclude=.git \
		       --exclude=.gitkeep \
		       --exclude=.gitignore \
		       --exclude=.gitmodules \
		       --exclude=examples \
		       --exclude=lib \
		       --exclude=build \
		       --exclude=.cache \
		       --exclude=terra \
		       --exclude=infra \
		       --exclude=analysis \
		       --exclude-vcs-ignores \
		       -zcvf"

    command = f"{command} {dst}/project.tar.gz ."
    execute(command)

def run(name:str, key:str, args, epsilon:float=1e-4, max_i:int=1000):
    r:RunDict = RunDict({
            "name": name,
            "strategy": StrategyDict({
                "key": key, 
                "reverse": name == "WORST",
            }), 
            "parameters": ParametersDict({
                "num": args.num,
                "choices": args.choices,
                "hyperparameter": args.fanout * 2,
                "rate": args.rate, 
                "duration": args.duration,
                "epsilon": epsilon, 
                "max_i": max_i,
                "converge": False
            }),
            "tree": TreeDict({
                "name": "", 
                "depth": args.depth, 
                "fanout": args.fanout,
                "n": 0, 
                "max": 0,
                "root": "",
                "nodes": []
            }), 
            "pool": [],
            "stages": [],
            "perf":  [ ResultDict({
                "id": "",
                "root": "",
                "key": key,
                "select": 0, 
                "rate": args.rate,
                "duration": args.duration,
                "items": [],
                "selected": []
            }) for _ in range(args.num) ], 
            "timers": TimersDict({
                    "build": 0.0,
                    "stages": [],
                    "convergence": 0.0,
                    "perf": [ 0.0 for _ in range(args.num) ],
                    "total": 0.0,
            })
    })
    return r

def runs(args):
    runs = []
    names = [ "BEST" ] # [ "BEST", "WORST" ]
    keys  = [ "p90", "p50", "heuristic" ]
    if args.mode == "default":
        for name in names:
            for key in keys:
                r = run(name, key, args)
                runs.append(r)

        runs.append(run(name="WORST",  key="p90", args=args))
        runs.append(run(name="WORST",  key="p50", args=args))

        runs.append(run(name="RAND",   key="NONE", args=args))

        hyperparameters = [ (1e-4, 1000), (5.5e-5, 10000) ]
        for tup in hyperparameters:
            epsilon, max_i = tup
            runs.append(run(name="LEMON", key="NONE", args=args, epsilon=epsilon, max_i=max_i))

    if args.mode == "lemondrop":
        hyperparameters = [(1e-4, 1000), (8.5e-05, 100000), (5.5e-05, 100000) ]
        for tup in hyperparameters:
            epsilon, max_i = tup
            runs.append(run(name="LEMON", key="NONE", args=args, epsilon=epsilon, max_i=max_i))

    return runs

def commands(args, addrs):
    commands = []

    match args.mode:
        case "mcast":
            tb  = TreeBuilder(arr=addrs, depth=args.depth, fanout=args.fanout)
            ret = tb.mcast(rate=args.rate, duration=args.duration, id="example")
            commands.extend(ret.buf)

        case "udp":
            tb  = TreeBuilder(arr=addrs, depth=1, fanout=len(addrs[1:]))
            ret = tb.parent(rate=args.rate, duration=args.duration, id="example")
            commands.extend(ret.buf)

        case "lemon":
            t = Timer()
            future = t.future_ts(args.duration + 25)
            commands.extend( [ f"./bin/lemon -i {addr} -p {6066} -s docker -f {future}" for addr in addrs[1:]] )

        case _: 
            pass

    return commands

def config(args, path):
    base_addr   = "10.1.1." if args.infra == "docker" else "10.1.25."
    base_saddr  = "10.1.0." if args.infra == "docker" else "10.0.25."
    addrs       = [ f"{base_addr}{i + 1}" for i in range(args.size + 1) ]
    saddrs      = [ f"{base_saddr}{i + 1}" for i in range(args.size + 1) ]
    names       = [ "manager" ] + [ f"worker{i}" for i in range(args.size) ]
    data        = {
            "infra": args.infra,
            "suffix": datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
            "port": args.port,
            "addrs": addrs,
            "saddrs": saddrs,
            "names": names,
            "map": {},
            "commands": commands(args, addrs) if (args.infra == "docker" and args.mode != "default") else [],
            "runs": runs(args),
    }

    for addr, name in zip(data["addrs"], data["names"]):
        data["map"][f"{addr}:{data['port']}"] = name

    with open(path, "w") as file: 
        json.dump(data, file, indent=4)

    del data["commands"]

    with open("schemas/default.json", "w") as file: 
        json.dump(data, file, indent=4)

    return data

def build(args, wdir):
    command=f"packer build -force -var-file=./variables.pkr.hcl {args.infra}.pkr.hcl"
    lexecute(f"{command}", wdir=wdir)

def plan(args, wdir):
    config(args, f"{wdir}/extract/data.json")
    compress(f"{wdir}/extract")
    lexecute(f"terraform init", wdir=wdir)
    lexecute(f"terraform plan -out=tf.plan -var mode={args.mode}", wdir=wdir)

def deploy(args , wdir):
    lexecute(f"terraform apply tf.plan", wdir=wdir)

def destroy(args, wdir):
    lexecute(f"terraform destroy -auto-approve", wdir=wdir)

