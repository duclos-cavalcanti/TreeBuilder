import yaml

from enum import Enum
from typing import List

class LOG_LEVEL(Enum):
    NONE = 1 
    DEBUG = 2 
    ERROR = 3

def dict_to_arr(d:dict) -> List:
    ret = []
    for _,v in d.items(): ret.append(str(v))
    return ret

def read_yaml(f:str):
    data = {}
    with open(f, 'r') as file:
        data = yaml.safe_load(file)
    return data
