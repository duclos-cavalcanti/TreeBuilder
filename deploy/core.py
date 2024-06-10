import os
import argparse
import yaml

from .utils import *

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

def config(args):
    config = "plans/default.yaml"
    port   = 9091
    addrs  = [ f"10.1.1.{i}:{port}" for i in range(args.pool + 1) ]
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

def plan(args):
    wdir = os.path.join(os.getcwd(), "infra", "terra", args.infra)
    if not os.path.isdir(wdir): raise RuntimeError(f"Not a directory: {wdir}")

    compress(f"{wdir}/extract")
    out = try_execute(f"terraform init", wdir=wdir)
    out = try_execute(f"terraform plan -out=tf.plan -var mode=default -var pool={args.pool}", wdir=wdir)
    with open(f"{wdir}/plan.log", "w") as file: file.write(out.decode("utf-8"))
    config(args)

def deploy(args):
    wdir = os.path.join(os.getcwd(), "infra", "terra", args.infra)
    if not os.path.isdir(wdir): raise RuntimeError(f"Not a directory: {wdir}")

    lexecute(f"terraform apply tf.plan", wdir=wdir)

def destroy(args):
    wdir = os.path.join(os.getcwd(), "infra", "terra", args.infra)
    if not os.path.isdir(wdir): raise RuntimeError(f"Not a directory: {wdir}")

    lexecute(f"terraform destroy -auto-approve", wdir=wdir)

def parse(rem=None):
    arg_def = argparse.ArgumentParser(
        description='Module to automate terraform stack management.',
        epilog='Example: core.py -a plan -i gcp'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        required=True,
        choices=["plan", "deploy", "destroy"],
        dest="action",
    )

    arg_def.add_argument(
        "-i", "--infra",
        type=str,
        required=False,
        default="gcp",
        choices=["docker", "gcp"],
        dest="infra",
    )

    arg_def.add_argument(
        "-f", "--fanout",
        type=int,
        default=2,
        required=False,
        dest="fanout",
    )

    arg_def.add_argument(
        "-d", "--depth",
        type=int,
        default=2,
        required=False,
        dest="depth",
    )

    arg_def.add_argument(
        "-r", "--rate",
        type=int,
        default=10,
        required=False,
        dest="rate",
    )

    arg_def.add_argument(
        "-t", "--time",
        type=int,
        default=10,
        required=False,
        dest="duration",
    )

    arg_def.add_argument(
        "-p", "--pool",
        type=int,
        default=9,
        required=False,
        dest="pool",
    )

    if not rem: args = arg_def.parse_args()
    else: args = arg_def.parse_args(rem)

    return args

def main(rem):
    args = parse(rem)

    match args.action:
        case "plan":    plan(args)
        case "deploy":  deploy(args)
        case "destroy": destroy(args)
        case _:         raise NotImplementedError()

    return

if __name__ == "__main__":
    main(rem=None)
