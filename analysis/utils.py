import os 
import tarfile

from typing import List

def isdir(dir:str):
    path = os.path.join(os.getcwd(), f"{dir}")
    if os.path.isdir(path): return path
    raise RuntimeError(f"Not a directory: {path}")

def find(dir:str, pattern:str):
    for d in os.listdir(dir):
        subdir = os.path.join(dir, d)
        if os.path.isdir(subdir):
            if pattern in d:
                return subdir

    raise RuntimeError(f"No directory found matching {pattern}")

def extract(dir:str):
    print(f"Extracting: {dir}")
    for f in os.listdir(dir):
        if f.endswith(".tar.gz"):
            with tarfile.open(os.path.join(dir, f)) as tar:
                tar.extractall(path=dir)
                print(f"DECOMPRESSED: {f}")

def iswithin(arr:List[str]):
    pass
