from .manager import Manager
from .worker  import Worker
from .utils   import LOG_LEVEL

import argparse
import time

def manager(args):
    M = Manager(args.name, ip=args.addr, port=args.port, LOG_LEVEL=LOG_LEVEL.NONE) 
    M.run()

def worker(args):
    W = Worker(args.name, ip=args.addr, port=args.port, LOG_LEVEL=LOG_LEVEL.NONE) 
    W.run()

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
        "-s", "--script",
        type=str,
        default="",
        required=False,
        dest="script",
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

