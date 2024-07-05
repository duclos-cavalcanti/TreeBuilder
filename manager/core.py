from .manager       import Manager
from .worker        import Worker
from .types         import Experiment, Logger

import os
import json

def read(schema):
    default = os.path.join(os.getcwd(), "schemas", "default.json")

    with open(schema if schema else default, 'r') as file: 
        data = json.load(file)

    return data

def manager(args):
    schema = read(args.schema)
    exp    = Experiment(schema)
    total  = len(exp.runs)

    L = Logger()
    M = Manager(name=args.name, ip=args.addr, port=args.port, workers=exp.workers, map=exp.map) 

    try:
        M.establish()

        for i,run in enumerate(exp.runs):
            L.state(f"STATE[RUN={run.data['name']}] {i}/{total}")

            # build tree
            for result in M.build(run):
                addrs = [ d for d in result["selected"] ]
                run.tree.n_add(addrs)
                run.pool.n_remove(addrs)
                run.data["stages"].append(result)

            # store tree
            run.data["tree"] = run.tree.get()

            # evaluate tree
            result = M.evaluate(run)
            run.data["perf"] = result

            # record run
            L.event({"RUN": run.data})

    except Exception as e:
        L.error("INTERRUPTED!")
        raise e

    finally:
        L.flush()
        M.node.socket.close()

    L.record("FINISHED!")

def worker(args):
    schema = read(args.schema)
    exp = Experiment(schema)

    L = Logger()
    W = Worker(name=args.name, ip=args.addr, port=args.port, manager=exp.manager, map=exp.map) 

    try:
        W.start()

    except Exception as e:
        L.error("INTERRUPTED!")
        raise e

    finally:
        L.flush()
        W.node.socket.close()

