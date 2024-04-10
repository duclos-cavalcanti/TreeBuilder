import os
import shutil
import argparse

# import ipdb
# ipdb.set_trace()

from .utils import execute,lexecute
from .utils import read_hcl, write_hcl
from python_terraform import Terraform

def build(args):
    pwd = os.getcwd()
    file = f"{pwd}/project.tar.gz"
    if not os.path.exists(file): 
        raise RuntimeError("No compressed project file!")

    infra = args.infra
    if infra == "docker":
        wdir = os.path.join(os.getcwd(), "deploy", "terra", "packer")
        if not os.path.isdir(wdir): 
            raise RuntimeError(f"Not a directory: {wdir}")

        src = os.path.join(os.getcwd(), "deploy", "terra", "commands.hcl")
        dst = os.path.join(os.getcwd(), "deploy", "terra", "packer" , "commands.pkr.hcl")
        shutil.copy(src, dst)

        lexecute(f"packer init .", wdir=wdir)
        lexecute(f"packer validate -var file={file} .", wdir=wdir)
        lexecute(f"packer build -var file={file} . ", wdir=wdir, verbose=True)
    else:
        raise NotImplementedError()

def deploy(args):
    infra = args.infra
    wdir = os.path.join(os.getcwd(), "deploy", "terra", infra)
    if not os.path.isdir(wdir): 
        raise RuntimeError(f"Not a directory: {wdir}")

    tf = Terraform(working_dir=wdir)
    var = {
        'name' :        "test",
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
        choices=["build", "deploy", "delete"],
        dest="action",
    )

    arg_def.add_argument(
        "-i", "--infra",
        type=str,
        required=True,
        choices=["docker", "gcp"],
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
        case "build":   build(args)
        case "deploy":  deploy(args)
        case "delete":  delete(args)

    return


if __name__ == "__main__":
    main(rem=None)
