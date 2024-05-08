import yaml
import subprocess

from typing import Tuple, List

def read_yaml(f:str):
    data = {}
    with open(f, 'r') as file:
        data = yaml.safe_load(file)
    return data

def lexecute(command:str, wdir=None) -> Tuple[int, List]:
    out = []
    p = subprocess.Popen(command.split(), 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         cwd=wdir)
                         
    print(f"{command}")
    for line in p.stdout: 
        l = line.decode('utf-8')
        out.append(l)
        print(l, end='')

    p.wait()
    return p.returncode, out
