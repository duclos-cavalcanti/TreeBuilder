import os
import argparse

from .utils import execute,lexecute
from python_terraform import Terraform

def build():
    wdir = os.path.join(os.getcwd(), "deploy", "terra", "packer")
    if not os.path.isdir(wdir): 
        raise RuntimeError(f"Not a directory: {wdir}")

    execute("packer init .", wdir=wdir)
    execute("packer validate .", wdir=wdir)
    lexecute("packer build .", wdir=wdir, verbose=True)

def create(args):
    infra = args.image
    wdir = os.path.join(os.getcwd(), "deploy", "terra", infra)
    if not os.path.isdir(wdir): 
        raise RuntimeError(f"Not a directory: {wdir}")

    plan = f"{wdir}/{infra}.out"
    tf = Terraform(working_dir=wdir)
    if tf.init() != 0:
        raise RuntimeError(f"Terraform initialization of {dir} failed!")
    
    tf.plan(out=plan)
    tf.apply(plan)
    tf.output()

def deploy(args):
    return

def delete(args):
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
        choices=["build", "create", "deploy", "delete"],
        dest="action",
    )

    arg_def.add_argument(
        "-i", "--infra",
        type=str,
        required=True,
        choices=["gcp", "docker", "packer"],
        dest="infra",
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
        case "build":   build()
        case "create":  create(args)
        case "deploy":  deploy(args)
        case "delete":  delete(args)

    return


if __name__ == "__main__":
    main(rem=None)
