import glob
import os
import shutil
import tarfile
import csv

from typing import List

def rnd(val:float, precision:int=2):
    ret = val
    ret = round(ret, precision)
    ret = f"{ret}"
    return  ret

def bounded(reference:float, value:float, perc:float):
    lower = (reference * ( (100 - perc) / 100 ) )
    upper = (reference * ( 1 + (perc) / 100 ) )
    return (lower <= value <= upper)

def read_csv(f:str, header:bool=True):
    data = []
    with open(f, 'r') as csvfile:
        reader = csv.reader(csvfile)
    
        # skip header
        if header: next(reader)

        for row in reader: data.append(row)
    return data

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

def findfile(files:List, id:str, patt:str="child"):
    for i,f in enumerate(files):
        name = f.split("/")[-1]
        if patt in name and id in name:
            return i
    raise RuntimeError(f"No file found matching {patt}")

def globfiles(path:str, patt:str):
    files = glob.glob(os.path.join(path, f"{patt}"))
    names = [ f.split("/")[-1] for f in files ]
    return files, names

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

