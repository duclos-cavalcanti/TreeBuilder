import yaml

from typing import List

def dict_to_arr(d:dict) -> List:
    ret = []
    for _,v in d.items(): ret.append(str(v))
    return ret

def read_yaml(f:str):
    data = {}
    with open(f, 'r') as file:
        data = yaml.safe_load(file)
    return data
