import os
import subprocess

def lexecute(command:str, wdir=None):
    if not wdir: wdir = os.getcwd()

    ret = 0
    out = bytes() 
    err = bytes()

    try:
        p = subprocess.Popen(command, 
                            shell=True,
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE, 
                             cwd=wdir)
                         
        print(f"{command}")

        for line in p.stdout: 
            print(line.decode('utf-8'), end='')

        p.wait()

        ret = p.returncode
        out = p.stdout.read()
        err = p.stderr.read()

    except Exception as e:
        raise(e)

    finally: 
        if ret != 0:
            print(f"RETURN[{ret}]:")
            print(err.decode('utf-8'))
            raise RuntimeError()

    return out


def execute(command:str, wdir=None):
    if not wdir: wdir = os.getcwd()

    ret = 0
    out = bytes()
    err = bytes()

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
            print(err.decode('utf-8'))
            raise RuntimeError()

    return ret, out, err
