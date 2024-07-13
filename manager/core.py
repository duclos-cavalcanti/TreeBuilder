from .manager       import Manager
from .worker        import Worker
from .types         import Experiment, Logger
from .lemondrop     import LemonDrop

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
    L.record(f"{args.name.upper()} UP")

    try:
        M.establish()
        L.record(f"CONNECTED[{len(M.workers)}]")

        for i,run in enumerate(exp.runs):
            L.state(f"STATE[RUN={run.data['name']}] {i}/{total}")

            # lemondrop
            if run.data["name"] == "LEMON":
                OWD = []
                for i,result in enumerate(M.lemon(run)): 
                    OWD.append([ item["p50"] for item in result["items"] ])
                    L.record(f"ROW: {i}/{len(M.workers)}")

                LD = LemonDrop(OWD=OWD, VMS=M.workers, K=run.tree.nmax, D=run.tree.dmax, F=run.tree.fanout)
                mapping, P, converged, elapsed = LD.solve()
                run.tree.root.id = mapping[0][1]
                run.tree.n_add([ m[1] for m in mapping[1:] ])
                L.record(f"LEMON TREE[{run.tree.name}] CONVERGENCE={converged} TOOK {elapsed} SECONDS")


            # heuristic
            else:
                for result in M.build(run):
                    addrs = [ d for d in result["selected"] ]
                    run.tree.n_add(addrs)
                    run.pool.n_remove(addrs)
                    run.data["stages"].append(result)
                    L.record(f"TREE[{run.tree.name}] SELECTION[{run.tree.n}/{run.tree.nmax}]: PARENT[{result['root']}] => CHILDREN {[ a for a in result['selected'] ]}")

            # store tree
            run.data["tree"] = run.tree.get()
            
            # evaluate tree
            result = M.evaluate(run)
            run.data["perf"] = result
            L.record(f"TREE[{run.tree.name}] PERFORMANCE[{result['selected'][0]}]: {result['items'][0]['p90']}")
            
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
    L.record(f"{args.name.upper()} UP")

    try:
        W.start()

    except Exception as e:
        L.error("INTERRUPTED!")
        raise e

    finally:
        L.flush()
        W.node.socket.close()

