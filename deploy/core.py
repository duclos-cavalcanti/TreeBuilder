import os
import subprocess
import argparse

from python_terraform import Terraform

def deploy(args):
    return

def delete(args):
    return

def create(args):
    wdir = os.path.join(os.getcwd(), "terra", args.mode)
    if not os.path.isdir(wdir): 
        raise RuntimeError(f"Not a directory: {wdir}")

    tf = Terraform(working_dir=wdir)
    if tf.init() != 0:
        raise RuntimeError(f"Terraform initialization of {dir} failed!")

    return

def parse(rem=None):
    arg_def = argparse.ArgumentParser(
        description='Module to automate terraform stack management.',
        epilog='Example: core.py -a create -m docker'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        required=True,
        choices=["create", "deploy", "delete"],
        dest="action",
    )

    arg_def.add_argument(
        "-m", "--mode",
        type=str,
        required=True,
        choices=["gcp", "docker"],
        dest="mode",
    )

    arg_def.add_argument(
        "-n", "--name",
        type=str,
        required=False,
        dest="name",
    )

    if not rem: args = arg_def.parse_args()
    else: args = arg_def.parse_args(rem)

    return args

def main(rem):
    args = parse(rem)
    # for arg, value in vars(args).items(): print(f"{arg}: {value}")

    match args.action:
        case "create":  create(args)
        case "deploy":  deploy(args)
        case "delete":  delete(args)

    return


if __name__ == "__main__":
    main(rem=None)
