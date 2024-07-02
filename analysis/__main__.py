import argparse

from .core import pull, process, generate

def parse():
    arg_def = argparse.ArgumentParser(
        description='Script to automate data analysis.',
        epilog='Example: main.py --action/-a pull -p <prefix> [-v yes]'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        choices=["pull", "process", "generate"],
        required=True,
        dest="action",
    )

    arg_def.add_argument(
        "-m", "--mode",
        type=str,
        required=False,
        default="default",
        choices=["default", "udp", "mcast"],
        dest="mode",
    )

    arg_def.add_argument(
        "-p", "--prefix",
        type=str,
        required=False,
        dest="prefix",
    )

    arg_def.add_argument(
        "-i", "--infra",
        type=str,
        choices=["docker", "gcp"],
        required=False,
        default="docker",
        dest="infra",
    )

    arg_def.add_argument(
        "-v", "--view",
        type=str,
        required=False,
        default="",
        dest="view",
    )

    args = arg_def.parse_args()
    return args

def main():
    args = parse()

    if not args.prefix and args.infra != "docker": 
        raise RuntimeError("Need prefix to pull data from GCP/Cloud")

    match args.action:
        case "pull":     pull(args)
        case "process":  process(args)
        case "generate": generate(args)
        case _:         raise NotImplementedError()

    return


if __name__ == "__main__":
    main()
