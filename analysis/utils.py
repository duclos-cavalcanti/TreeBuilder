import os
import shutil

from typing import List

def mkdir(dir:str):
    if os.path.isdir(dir): shutil.rmtree(dir)
    os.mkdir(dir)

def bounded(reference:float, value:float, perc:float):
    lower = (reference * ( (100 - perc) / 100 ) )
    upper = (reference * ( 1 + (perc) / 100 ) )
    return (lower <= value <= upper)

def rnd(val:float, precision:int=2):
    ret = val
    ret = round(ret, precision)
    ret = f"{ret}"
    return  ret 
