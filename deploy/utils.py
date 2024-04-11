import sys
import os
import re
import subprocess
import hcl
import json

def get_ts(f:str):
    if not os.path.isfile(f):
        raise RuntimeError(f"Not a file: {f}")
    
    ts = os.path.getmtime(f)
    return ts

def read_hcl(f:str):
    data = None
    with open(f, 'r') as fp: data = hcl.load(fp)
    return data

def write_hcl(f:str, data):
    with open(f, 'w') as fp: 
        json.dump(data, fp)


def lexecute(command:str, wdir=None, verbose=False):
    command = re.sub(r'[\s\n]+', ' ', command)
    p = subprocess.Popen(command.split(), 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         cwd=wdir)
                         
    if verbose:
        print(f"{command}")
        for line in p.stdout: 
            print(line.decode('utf-8'), end='')

    p.wait()

    if p.returncode != 0: 
        err = p.stderr.read().decode('utf-8')
        print(err, file=sys.stderr)
        raise RuntimeError(f"Error[{p.returncode}]: {command}")

def execute(command:str, wdir=None, verbose=False):
    ret, out, err = try_execute(command, wdir)
    if ret == 0:
        if verbose: 
            print(out.decode('utf-8'))
        return
    else:
        print(f"COMMAND FAILED: '{command}'")
        print(f"STDOUT:")
        print(f"{out.decode('utf-8')}")
        exit(ret)

def try_execute(command:str, wdir=None):
    if not wdir: wdir = os.getcwd()
    try:
        arr = command.split()
        p = subprocess.Popen(arr, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             cwd=wdir)
        out, err = p.communicate()
        ret = p.returncode
    except Exception as e:
        raise(e)

    return ret, out, err
