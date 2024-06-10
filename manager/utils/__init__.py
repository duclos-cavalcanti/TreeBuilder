import os
import subprocess

def format_addr( addr:str, diff:int=1000):
    split = addr.split(":")
    ip    = split[0]
    port  = int(split[1]) - diff
    return f"{ip}:{port}"

def try_execute(command:str, wdir=None):
    ret = 0
    out = ""
    err = ""

    try: 
        ret, out, err = execute(command, wdir)
        return out

    except Exception as e:
        print("OUTPUT: \n{out}")
        raise(e)

def execute(command:str, wdir=None):
    if not wdir: 
        wdir = os.getcwd()

    ret = 0
    out = ""
    err = ""

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

    finally: 
        if ret != 0:
            raise RuntimeError()

    return ret, out, err

