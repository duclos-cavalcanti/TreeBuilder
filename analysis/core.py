import subprocess
import os
import shutil
import tarfile

from .parse import parse

def run(command:str) -> list[str]:
    ret = subprocess.run(command.split(" "), stdout=subprocess.PIPE, text=True)
    arr = ret.stdout.strip().split('\n')
    return arr

def extract(src:str):
    for f in os.listdir(src):
        if f.endswith(".tar.gz"):
            with tarfile.open(os.path.join(src, f)) as tar:
                tar.extractall(path=src)
                print(f"DECOMPRESSED: {f}")

def pull(args):
    if args.infra == "gcp":
        print(f"PULLING: {args.prefix}")
        if not args.prefix: 
            raise RuntimeError("Need prefix to pull data from GCP")

        arr = run("gcloud storage ls gs://exp-results-nyu-systems-multicast/")
        for a in arr:
            if args.prefix in a:
                dir = a.split("/")[-2]
                root = os.path.join(os.getcwd(), "analysis", "data")
                path = os.path.join(os.getcwd(), "analysis", "data", dir)
                if os.path.isdir(path):
                    print(f"Bucket {dir} already pulled down!")
                else:
                    run(f"gcloud storage cp --recursive gs://exp-results-nyu-systems-multicast/{dir}* {root}")

                extract(f"{path}")
                return

        raise RuntimeError(f"No bucket found on GCP matching: {args.prefix}")

    if args.infra == "docker":
        dir = os.path.join(os.getcwd(), "infra/terra/docker/modules/default/volume")
        if not os.path.isdir(dir): 
            raise RuntimeError(f"Not a directory: {dir}")

        for d in os.listdir(dir):
            subdir = os.path.join(dir, d)
            if os.path.isdir(subdir):
                if "treefinder" in  d:
                    dst = os.path.join(os.getcwd() , "analysis", "data")
                    shutil.move(subdir,  dst)
                    print(f"PULLING: {subdir}")
                    return

        raise RuntimeError("No directory found locally")

def process(args):
    if args.infra == "docker":
        dir = os.path.join(os.getcwd() , "analysis", "data")
        if not os.path.isdir(dir): 
            raise RuntimeError(f"Not a directory: {dir}")

        for d in os.listdir(dir):
            subdir = os.path.join(dir, d)
            if os.path.isdir(subdir):
                if f"treefinder-{args.infra}" in  d:
                    extract(subdir)
                    print(f"PROCESSING: {d}")
                    return parse(subdir)

        raise RuntimeError("No directory found locally")

    else:
        raise NotImplementedError()
