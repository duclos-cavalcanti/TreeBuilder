from .utils  import *
from manager import TreeBuilder, RunDict, StrategyDict, ParametersDict, TreeDict, ResultDict

import os
import json

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

def runs(args):
    runs = []
    names = [ "BEST", "WORST", "RAND"]
    keys  = [ "p90", "heuristic" ]

    for name in names:
        for key in keys:
            r:RunDict = RunDict({
                    "name": name,
                    "strategy": StrategyDict({
                        "key": key, 
                        "expr": {},
                        "reverse": name == "WORST",
                        "rand":    name == "RAND",
                    }), 
                    "parameters": ParametersDict({
                        "hyperparameter": args.fanout * 2,
                        "rate": args.rate, 
                        "duration": args.duration,
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
                    "perf": ResultDict({
                        "root": "",
                        "key": key,
                        "select": 0, 
                        "rate": args.rate,
                        "duration": args.duration,
                        "items": [],
                        "selected": []

                    })
            })
            runs.append(r)
    return runs

def config(args, path):
    base_addr  = "10.1.1." if args.infra == "docker" else "10.1.25."
    base_saddr = "10.1.0." if args.infra == "docker" else "10.0.25."
    data = {
            "infra": args.infra,
            "port": args.port,
            "addrs":  [ f"{base_addr}{i + 1}" for i in range(args.size + 1) ],
            "saddrs": [ f"{base_saddr}{i + 1}" for i in range(args.size + 1) ],
            "names":  [ "manager" ] + [ f"worker{i}" for i in range(args.size) ],
            "map":    {},
            "commands": [],
            "runs": runs(args),
    }

    for addr, name in zip(data["addrs"], data["names"]):
        data["map"][f"{addr}:{data['port']}"] = name

    if args.infra == "docker" and args.mode != "default":
        if args.mode == "mcast":
            tb  = TreeBuilder(arr=data["addrs"], depth=args.depth, fanout=args.fanout)
            ret = tb.mcast(rate=args.rate, duration=args.duration)
            data["commands"].extend(ret.buf)

        elif args.mode == "udp":
            tb  = TreeBuilder(arr=data["addrs"], depth=1, fanout=len(data["addrs"][1:]))
            ret = tb.parent(rate=args.rate, duration=args.duration, id="example")
            data["commands"].extend(ret.buf)

        else:
            raise NotImplementedError()

    with open(path, "w") as file: 
        json.dump(data, file, indent=4)

    del data["commands"]

    with open("schemas/default.json" if data["infra"] == "gcp" else "schemas/docker.json", "w") as file: 
        json.dump(data, file, indent=4)

    return data

def plan(args, wdir):
    config(args, f"{wdir}/extract/data.json")
    compress(f"{wdir}/extract")
    lexecute(f"terraform init", wdir=wdir)
    lexecute(f"terraform plan -out=tf.plan -var mode={args.mode}", wdir=wdir)

def deploy(args , wdir):
    lexecute(f"terraform apply tf.plan", wdir=wdir)

def destroy(args, wdir):
    lexecute(f"terraform destroy -auto-approve", wdir=wdir)

