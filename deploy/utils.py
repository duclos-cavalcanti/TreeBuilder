import os
import subprocess
import hcl

def read_hcl(f:str):
    data = None
    with open(f, 'r') as fp:
        data = hcl.load(fp)
    return data

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
        print(f"STDERR:")
        print(f"{err.decode('utf-8')}")
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
