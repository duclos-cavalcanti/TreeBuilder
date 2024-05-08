import yaml
import subprocess

def read_yaml(f:str):
    data = {}
    with open(f, 'r') as file:
        data = yaml.safe_load(file)
    return data

def lexecute(command:str, wdir=None):
    p = subprocess.Popen(command.split(), 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         cwd=wdir)
                         
    print(f"{command}")
    for line in p.stdout: 
        print(line.decode('utf-8'), end='')

    p.wait()
    return p.returncode
