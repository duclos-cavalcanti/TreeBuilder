from .manager import Manager
from .worker  import Worker

import os
import yaml

def manager(args):
    plan = os.path.join(os.getcwd(), "plans", "default.yaml")
    if args.yaml: 
        plan = args.yaml

    with open(plan, 'r') as file: 
        plan = yaml.safe_load(file)

    M = Manager(plan, name=args.name, ip=args.addr, port=args.port) 
    M.go()

def worker(args):
    W = Worker(name=args.name, ip=args.addr, port=args.port) 
    W.go()
