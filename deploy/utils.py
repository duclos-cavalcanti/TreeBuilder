import os
import subprocess

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

def lexecute(command:str, wdir=None):
    if not wdir: wdir = os.getcwd()

    ret = 0
    out = "" 
    err = ""

    try:
        arr = command.split()
        p = subprocess.Popen(arr, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            cwd=wdir)
                         
        print(f"{command}")
        for line in p.stdout: print(line.decode('utf-8'), end='')

        p.wait()

        ret = p.returncode
        out = p.stdout.read().decode('utf-8')
        err = p.stderr.read().decode('utf-8')

    except Exception as e:
        raise(e)

    finally: 
        if ret != 0:
            raise RuntimeError()

    return ret, out, err


def execute(command:str, wdir=None):
    if not wdir: wdir = os.getcwd()

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
