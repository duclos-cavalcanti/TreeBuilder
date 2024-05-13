from enum import Enum

class LOG_LEVEL(Enum):
    NONE = 1 
    DEBUG = 2 
    ERROR = 3

RED = "\033[31m"
GRN = "\033[92m"
CLR = "\033[0m"

def print_color(text:str, color):
    print(f"{color}{text}{CLR}")

def print_arr(arr:list, header:str):
    print(f"{header}: {{")
    for i,a in enumerate(arr): print(f"\t{i} => {a}")
    print("}")
