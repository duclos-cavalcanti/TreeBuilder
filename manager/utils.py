import sys

from itertools import zip_longest

RED = "\033[31m"
GRN = "\033[92m"
YLW = "\033[33m"
CLR = "\033[0m"

def print_color(text:str, color:str, end='\n'):
    print(f"{color}{text}{CLR}", end=end)

def print_LR(a, b, c, d, f=sys.stdout):
    left  = [ f"{c}" ] + f"{a}".split('\n')
    right = [ f"{d}" ] + f"{b}".split('\n')
    
    max_width = max(len(line) for line in left)
    for l, r in zip_longest(left, right, fillvalue=''):
        print(f"{l:<{max_width}}  {r}", file=f)
