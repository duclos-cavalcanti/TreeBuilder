from .manager import Manager
from .worker  import Worker

import os
import yaml

def manager(args):
    schema = os.path.join(os.getcwd(), "schemas", "default.yaml")
    if args.yaml: 
        schema = args.yaml

    with open(schema, 'r') as file: 
        schema = yaml.safe_load(file)

    M = Manager(schema, name=args.name, ip=args.addr, port=args.port) 
    M.go()

def worker(args):
    W = Worker(name=args.name, ip=args.addr, port=args.port) 
    W.go()
