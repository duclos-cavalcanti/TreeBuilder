import subprocess
import os
import shutil
import tarfile

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

def gcopy(src:str, dst:str, bucket:str="gs://exp-results-nyu-systems-multicast"):
    os.system(f"gcloud storage cp --recursive {bucket}/{src}* {dst}")

def pull(args):
    if args.infra == "gcp":
        res = gpull(args.prefix)
        src = res.split('/')[-2]
        dst = os.path.join(os.getcwd(), "analysis", "data")
        path = os.path.join(os.getcwd(), "analysis", "data", src)

        if os.path.isdir(path):
            print(f"FOLDER ALREADY EXISTS: {path}")
            return

        gcopy(src, dst)
        extract(path)
        return

    elif args.infra == "docker":
        dir = isdir("infra/terra/docker/modules/default/volume")
        src = finddir(dir=dir, patt=f"treefinder-docker-{args.prefix}")
        dst = isdir("analysis/data")
        shutil.move(src,  dst)
        print(f"MOVED: {src} -> {dst}")
        extract(f"{dst}/{src.split('/')[-1]}")
        return

    else:
        raise NotImplementedError()
