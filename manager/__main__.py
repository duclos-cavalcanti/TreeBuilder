from .core import manager, worker

import argparse

def parse():
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
        "-s", "--schema",
        type=str,
        default="",
        required=False,
        dest="schema",
    )

    arg_def.add_argument(
        "-n", "--name",
        type=str,
        default="",
        required=True,
        dest="name",
    )

    args = arg_def.parse_args()
    return args

def main():
    args = parse()

    match args.action:
        case "manager": manager(args)
        case "worker":  worker(args)
        case _:         raise NotImplementedError()

    return

if __name__ == "__main__":
    main()
