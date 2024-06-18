from .utils  import *
from manager import TreeBuilder

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

def config(args, path):
    data = {
            "infra": args.infra,
            "port": args.port,
            "addrs":  [ f"10.1.1.{i + 1}" for i in range(args.size + 1) ],
            "saddrs": [ f"10.1.0.{i + 1}" for i in range(args.size + 1) ],
            "params": {
                "hyperparameter": args.fanout * 2,
                "rate": args.rate, 
                "duration": args.duration,
                "fanout": args.fanout, 
                "depth": args.depth,
            },
            "commands": [],
            "runs": [ 
                {
                    "name": "BEST",
                    "strategy": {
                        "best": True,
                        "key": "p90"
                    }
                },
                {
                    "name": "WORST",
                    "strategy": {
                        "best": False,
                        "key": "p90"
                    }
                },
                {
                    "name": "RAND",
                    "strategy": {
                        "best": False,
                        "key": "p90"
                    },
                }
            ],
    }

    if args.infra == "docker" and args.mode != "default":
        if args.mode == "mcast":
            tb  = TreeBuilder(arr=data["addrs"], depth=data['params']['depth'], fanout=data['params']['fanout'])
            ret = tb.mcast(rate=data['params']['rate'], duration=data['params']['duration'])
            data["commands"].extend(ret.buf)

        elif args.mode == "udp":
            tb  = TreeBuilder(arr=data["addrs"], depth=1, fanout=len(data["addrs"][1:]))
            ret = tb.parent(rate=data['params']['rate'], duration=data['params']['duration'])
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

