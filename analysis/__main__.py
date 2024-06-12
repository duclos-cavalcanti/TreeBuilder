import argparse

from .core import pull, process

def parse():
    arg_def = argparse.ArgumentParser(
        description='Script to automate data analysis.',
        epilog='Example: main.py --action/-a pull -p <prefix>'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        choices=["pull", "process"],
        required=True,
        dest="action",
    )

    arg_def.add_argument(
        "-p", "--prefix",
        type=str,
        required=True,
        dest="prefix",
    )

    args = arg_def.parse_args()
    return args

def main():
    args = parse()

    match args.action:
        case "pull":    pull(args)
        case "process": process(args)
        case _:         raise NotImplementedError()

    return


if __name__ == "__main__":
    main()
