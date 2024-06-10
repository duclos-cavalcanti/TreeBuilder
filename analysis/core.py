import argparse
import subprocess
import os
import shutil
import tarfile
import csv

def run(command:str, verbose:bool=False) -> list[str]:
    ret = subprocess.run(command.split(" "), stdout=subprocess.PIPE, text=True)
    arr = ret.stdout.strip().split('\n')
    if verbose:
        for a in arr:
            print(a)

    return arr

# treefinder-06-10-14:21:46

def pull(args):
    print(f"PULLING: {args.prefix}")
    def gpull(prefix:str):
        arr = run("gcloud storage ls gs://exp-results-nyu-systems-multicast/")
        for a in arr:
            if prefix in a:
                dir = a.split("/")[-2]
                root = os.path.join(os.getcwd(), "analysis", "data")
                path = os.path.join(os.getcwd(), "analysis", "data", dir)
                if os.path.isdir(path):
                    print(f"Bucket {dir} already pulled down!")
                else:
                    run(f"gcloud storage cp --recursive gs://exp-results-nyu-systems-multicast/{dir}* {root}")
                return path
        raise RuntimeError(f"No bucket found on GCP matching prefix: {prefix}")


    def extract(src:str):
        for f in os.listdir(src):
            if f.endswith(".tar.gz"):
                with tarfile.open(os.path.join(src, f)) as tar:
                    tar.extractall(path=src)
                    print(f"Decompressed: {f}")

    dir = gpull(args.prefix)
    extract(f"{dir}")

def process(args):
    raise NotImplementedError()

def parse(rem=None):
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

    if not rem: args = arg_def.parse_args()
    else: args = arg_def.parse_args(rem)

    return args

def main(rem):
    args = parse(rem)

    match args.action:
        case "pull":    pull(args)
        case "process": process(args)
        case _:         raise NotImplementedError()

    return


if __name__ == "__main__":
    main(rem=None)
