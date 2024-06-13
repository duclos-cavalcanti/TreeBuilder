from .core import plan, deploy, destroy

import os
import argparse

def parse():
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
        "-m", "--mode",
        type=str,
        required=False,
        default="default",
        choices=["default", "test", "udp", "mcast"],
        dest="mode",
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
        "-s", "--size",
        type=int,
        default=9,
        required=False,
        dest="size",
    )

    arg_def.add_argument(
        "-p", "--port",
        type=int,
        default=9091,
        required=False,
        dest="port",
    )

    args = arg_def.parse_args()
    return args

def main():
    args = parse()

    wdir = os.path.join(os.getcwd(), "infra", "terra", args.infra)
    if not os.path.isdir(wdir): 
        raise RuntimeError(f"Not a directory: {wdir}")

    match args.action:
        case "plan":    plan(args, wdir)
        case "deploy":  deploy(args, wdir)
        case "destroy": destroy(args, wdir)
        case _:         raise NotImplementedError()

    return

if __name__ == "__main__":
    main()
