import os
import shutil
import argparse

# import ipdb
# ipdb.set_trace()

from .utils import execute,lexecute
from .utils import read_hcl, write_hcl
from python_terraform import Terraform

def get_ts(f1:str, f2:str):
    if not os.path.isfile(f1):
        raise RuntimeError(f"Not a file: {f1}")

    if not os.path.isfile(f2):
        raise RuntimeError(f"Not a file: {f2}")
    
    mtime_f1 = os.path.getmtime(f1)
    mtime_f2 = os.path.getmtime(f2)
    
    return mtime_f1, mtime_f2

def update(dst:str):
    if dst == "packer":
        src = os.path.join(os.getcwd(), "deploy", "terra", "commands.hcl")
        dst = os.path.join(os.getcwd(), "deploy", "terra", "packer" , "commands.pkr.hcl")
    elif dst == "gcp":
        src = os.path.join(os.getcwd(), "deploy", "terra", "commands.hcl")
        dst = os.path.join(os.getcwd(), "deploy", "terra", "gcp" , "commands.tf")
    else:
        raise NotImplementedError()

    m1, m2 = get_ts(src, dst)
    if m1 > m2: # commands.hcl has been changed recently
        print(f"UPDATING: {src} -> {dst}")
        shutil.copy(src, dst)

    return

def build():
    wdir = os.path.join(os.getcwd(), "deploy", "terra", "packer")
    if not os.path.isdir(wdir): 
        raise RuntimeError(f"Not a directory: {wdir}")

    update("packer")
    lexecute("packer init .", wdir=wdir)
    lexecute("packer validate .", wdir=wdir)
    lexecute("packer build .", wdir=wdir, verbose=True)

def create(args):
    infra = args.infra
    wdir = os.path.join(os.getcwd(), "deploy", "terra", infra)
    if not os.path.isdir(wdir): 
        raise RuntimeError(f"Not a directory: {wdir}")

    tf = Terraform(working_dir=wdir)
    var = {
        'name' :        "client",
        'pwd':          os.getcwd(),
        'entry':        os.path.join(os.getcwd(), "deploy", "terra", "docker", "entry.sh"),
        'exposed_port': 8082,
    }

    ret, stdout, stderr = tf.init()
    if ret != 0:
        print(stderr)
        err = f"[{ret}] Terraform initialization of {wdir} failed!"
        raise RuntimeError(err)

    ret, stdout, stderr = tf.apply(skip_plan=True, var=var)
    if ret != 0:
        print(stderr)
        err = f"[{ret}] Terraform apply failed!"
        raise RuntimeError(err)

    return

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
