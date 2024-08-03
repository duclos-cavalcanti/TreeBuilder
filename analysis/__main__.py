import argparse
import subprocess
import os
import shutil
import tarfile

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
        "-m", "--mode",
        type=str,
        required=False,
        default="default",
        choices=["default"],
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

    args = arg_def.parse_args()
    return args

def extract(dir:str):
    print(f"Extracting: {dir}")
    for f in os.listdir(dir):
        if f.endswith(".tar.gz"):
            name = f.split(".tar.gz")[0]
            path = os.path.join(dir, name)
            os.mkdir(path)
            with tarfile.open(os.path.join(dir, f)) as tar:
                tar.extractall(path=path)
                print(f"DECOMPRESSED: {f}")

def isdir(dir:str):
    path = os.path.join(os.getcwd(), f"{dir}")
    if os.path.isdir(path): return path
    raise RuntimeError(f"Not a directory: {path}")

def finddir(dir:str, patt:str):
    for d in os.listdir(dir):
        subdir = os.path.join(dir, d)
        if os.path.isdir(subdir):
            if patt in d:
                return subdir
    raise RuntimeError(f"No directory found matching {patt}")

def gpull(prefix:str):
    command = "gcloud storage ls gs://exp-results-nyu-systems-multicast/"
    ret     = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)
    arr     = ret.stdout.strip().split('\n')
    for a in arr:
        if prefix in a:
            print(f"PULLING {a}")
            return a

    raise RuntimeError(f"No bucket found on GCP matching: {prefix}")

def pull(args):
    if args.infra == "gcp":
        res = gpull(args.prefix)
        src = res.split('/')[-2]
        dst = os.path.join(os.getcwd(), "analysis", "data")
        path = os.path.join(os.getcwd(), "analysis", "data", src)

        if os.path.isdir(path):
            print(f"FOLDER ALREADY EXISTS: {path}")
            return
        
        bucket = "gs://exp-results-nyu-systems-multicast"
        os.system(f"gcloud storage cp --recursive {bucket}/{src}* {dst}")
        extract(path)

    elif args.infra == "docker":
        dir = isdir("infra/terra/docker/modules/default/volume")
        src = finddir(dir=dir, patt=f"treefinder-docker-{args.prefix}")
        dst = isdir("analysis/data")
        shutil.move(src,  dst)
        print(f"MOVED: {src} -> {dst}")
        extract(f"{dst}/{src.split('/')[-1]}")

    else:
        raise NotImplementedError()

def main():
    args = parse()

    if not args.prefix and args.infra != "docker": 
        raise RuntimeError("Need prefix to pull data from GCP/Cloud")

    match args.action:
        case "pull":     pull(args)
        case _:         raise NotImplementedError()

    return


if __name__ == "__main__":
    main()
