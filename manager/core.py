from .manager import Manager
from .worker  import Worker
from .ds      import LOG_LEVEL

import os
import argparse

def manager(args):
    plan = os.path.join(os.getcwd(), "plans", "default.yaml")
    if args.yaml: plan = args.yaml

    M = Manager(plan, args.name, ip=args.addr, port=args.port, LOG_LEVEL=LOG_LEVEL.NONE) 
    M.go()

def worker(args):
    W = Worker(args.name, ip=args.addr, port=args.port, LOG_LEVEL=LOG_LEVEL.NONE) 
    W.go()

def parse(rem=None):
    arg_def = argparse.ArgumentParser(
        description='Module to automate terraform stack management.',
        epilog='Example: core.py -a create -m docker'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        required=False,
        default="manager",
        choices=["manager", "worker"],
        dest="action",
    )

    arg_def.add_argument(
        "-i", "--ip",
        type=str,
        required=True,
        dest="addr",
    )

    arg_def.add_argument(
        "-p", "--port",
        type=int,
        default=8081,
        required=False,
        dest="port",
    )

    arg_def.add_argument(
        "-y", "--yaml",
        type=str,
        default="",
        required=False,
        dest="yaml",
    )

    arg_def.add_argument(
        "-n", "--name",
        type=str,
        default="",
        required=True,
        dest="name",
    )

    if not rem: args = arg_def.parse_args()
    else: args = arg_def.parse_args(rem)

    return args

def main(rem):
    args = parse(rem)

    match args.action:
        case "manager": manager(args)
        case "worker":  worker(args)

    return

