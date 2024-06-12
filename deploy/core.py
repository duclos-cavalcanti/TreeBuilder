from .utils import *

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

def config(args, wdir):
    config = "plans/default.yaml" if args.infra == "gcp" else "plans/docker.yaml"
    addrs   = [ f"10.1.1.{i + 1}:{args.port}" for i in range(args.size + 1) ]
    saddrs  = [ f"10.1.0.{i + 1}:{args.port}" for i in range(args.size + 1) ]
    data = {
            "infra": args.infra,
            "addrs": addrs,
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

    with open(f"{wdir}/data.json", "w") as file: 
        json.dump({
                "port":     args.port,
                "addrs":    [ a.split(":")[0] for a in data["addrs"] ],
                "saddrs":   [ a.split(":")[0] for a in saddrs ]
                }, file)

    return data

def plan(args):
    wdir = os.path.join(os.getcwd(), "infra", "terra", args.infra)
    if not os.path.isdir(wdir): raise RuntimeError(f"Not a directory: {wdir}")

    compress(f"{wdir}/extract")
    config(args, wdir)
    execute(f"terraform init", wdir=wdir)
    out = lexecute(f"terraform plan -out=tf.plan -var mode={args.mode}", wdir=wdir)
    with open(f"{wdir}/plan.log", "w") as file: file.write(out.decode('utf-8'))

def deploy(args):
    wdir = os.path.join(os.getcwd(), "infra", "terra", args.infra)
    if not os.path.isdir(wdir): raise RuntimeError(f"Not a directory: {wdir}")

    lexecute(f"terraform apply tf.plan", wdir=wdir)

def destroy(args):
    wdir = os.path.join(os.getcwd(), "infra", "terra", args.infra)
    if not os.path.isdir(wdir): raise RuntimeError(f"Not a directory: {wdir}")

    lexecute(f"terraform destroy -auto-approve", wdir=wdir)

