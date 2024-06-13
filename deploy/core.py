from .utils  import *
from manager import Tree

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

def variables(args, path):
    data = {
            "port": args.port,
            "addrs":  [ f"10.1.1.{i + 1}" for i in range(args.size + 1) ],
            "saddrs": [ f"10.1.0.{i + 1}" for i in range(args.size + 1) ],
            "commands": []
    }

    if args.infra == "docker" and args.mode != "default":
        if args.mode == "mcast":
            t = Tree(name="mcast", root=data["addrs"][0], fanout=args.fanout, depth=args.depth, arr=data["addrs"][1:]) 
            if not t.full(): raise RuntimeError("List of addresses does not form a tree")

            def callback(_, node, buf):
                if len(node.children) > 0:
                    c   =   f"./bin/mcast -a "
                    c   +=  f" ".join(f"{n.id}:{args.port}" for n in node.children)
                    c   +=  f" -r {args.rate} -d {args.duration}"
                    c   +=  f" -i {node.id} -p {args.port}"
                    if node.parent is None: c += " -R"
                else:
                    c   =   f"./bin/mcast "
                    c   +=  f" -r {args.rate} -d {args.duration}"
                    c   +=  f" -i {node.id} -p {args.port}"
                buf.append(c)

            t.traverse(callback, data["commands"])

        elif args.mode == "udp":
            t = Tree(name="udp", root=data["addrs"][0], fanout=len(data["addrs"][1:]), depth=1, arr=data["addrs"][1:]) 
            if not t.full(): raise RuntimeError("List of addresses does not form a tree")

            def callback(_, node, buf):
                if len(node.children) > 0:
                    c   =  f"./bin/parent -a "
                    c   +=  f" ".join(f"{n.id}:{args.port}" for n in node.children)
                    c   +=  f" -r {args.rate} -d {args.duration}"
                else:
                    c   =  f"./bin/child -i {node.id} -p {args.port}"
                    c   += f" -r {args.rate} -d {args.duration}"
                buf.append(c)

            t.traverse(callback, data["commands"])

        else:
            raise NotImplementedError()

    with open(path, "w") as file: 
        json.dump(data, file, indent=4)

    return data

def config(args, d):
    config = "plans/default.yaml" if args.infra == "gcp" else "plans/docker.yaml"
    data = {
            "infra": args.infra,
            "addrs": [ f"{a}:{args.port}" for a in d["addrs"] ],
            "params": {
                "hyperparameter":   args.fanout * 2,
                "rate":             args.rate,
                "duration":         args.duration,
                "fanout":           args.fanout,
                "depth":            args.depth,
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

    with open(config, "w") as file: 
        yaml.dump(data, file, sort_keys=False)

    return data

def plan(args, wdir):
    compress(f"{wdir}/extract")
    config(args, variables(args, f"{wdir}/data.json"))
    lexecute(f"terraform init", wdir=wdir)
    lexecute(f"terraform plan -out=tf.plan -var mode={args.mode}", wdir=wdir)

def deploy(args , wdir):
    lexecute(f"terraform apply tf.plan", wdir=wdir)

def destroy(args, wdir):
    lexecute(f"terraform destroy -auto-approve", wdir=wdir)

