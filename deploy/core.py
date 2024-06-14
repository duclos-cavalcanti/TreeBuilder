from .utils  import *
from manager import TreeBuilder

import os
import yaml
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

def data(args, path):
    data = {
            "infra": args.infra,
            "port": args.port,
            "rate": args.rate, 
            "duration": args.duration,
            "fanout": args.fanout, 
            "depth": args.depth,
            "addrs":  [ f"10.1.1.{i + 1}" for i in range(args.size + 1) ],
            "saddrs": [ f"10.1.0.{i + 1}" for i in range(args.size + 1) ],
            "commands": []
    }

    if args.infra == "docker" and args.mode != "default":
        if args.mode == "mcast":
            tb  = TreeBuilder(arr=data["addrs"], depth=data['depth'], fanout=data['fanout'])
            ret = tb.mcast(rate=data['rate'], duration=data['duration'])
            data["commands"].extend(ret.buf)

        elif args.mode == "udp":
            tb  = TreeBuilder(arr=data["addrs"], depth=1, fanout=len(data["addrs"][1:]))
            ret = tb.parent(rate=data['rate'], duration=data['duration'])
            data["commands"].extend(ret.buf)

        else:
            raise NotImplementedError()

    with open(path, "w") as file: 
        json.dump(data, file, indent=4)

    return data

def config(data):
    y = {
            "infra": data['infra'],
            "addrs": [ f"{a}:{data['port']}" for a in data['addrs'] ],
            "params": {
                "hyperparameter":   data["fanout"] * 2,
                "rate":             data["rate"],
                "duration":         data["duration"],
                "fanout":           data["fanout"],
                "depth":            data["depth"],
            }, 
            "runs": [ 
                {
                    "name": "BEST",
                    "strategy": {
                        "best": True
                    }
                },
                {
                    "name": "WORST",
                    "strategy": {
                        "best": False
                    }
                },
                {
                    "name": "RAND",
                    "strategy": {
                        "best": True
                    },
                }
            ],
    }

    config = "schemas/default.yaml" if data["infra"] == "gcp" else "schemas/docker.yaml"
    with open(config, "w") as file: 
        yaml.dump(y, file, sort_keys=False)

    return data

def plan(args, wdir):
    compress(f"{wdir}/extract")
    config(data(args, f"{wdir}/data.json"))
    lexecute(f"terraform init", wdir=wdir)
    lexecute(f"terraform plan -out=tf.plan -var mode={args.mode}", wdir=wdir)

def deploy(args , wdir):
    lexecute(f"terraform apply tf.plan", wdir=wdir)

def destroy(args, wdir):
    lexecute(f"terraform destroy -auto-approve", wdir=wdir)

