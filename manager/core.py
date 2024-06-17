from .manager import Manager
from .worker  import Worker

import os
import json

def manager(args):
    schema = os.path.join(os.getcwd(), "schemas", "default.json")
    if args.schema: schema = args.schema

    with open(schema, 'r') as file: 
        schema = json.load(file)

    M = Manager(schema, name=args.name, ip=args.addr, port=args.port) 
    M.go()

def worker(args):
    W = Worker(name=args.name, ip=args.addr, port=args.port) 
    W.go()
