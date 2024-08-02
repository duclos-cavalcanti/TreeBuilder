from .manager       import Manager
from .worker        import Worker
from .types         import Experiment, Logger
from .lemondrop     import LemonDrop

import os
import json
import time
import copy

def read(schema):
    default = os.path.join(os.getcwd(), "schemas", "default.json")

    with open(schema if schema else default, 'r') as file: 
        data = json.load(file)

    return data

def manager(args):
    schema  = read(args.schema)
    exp     = Experiment(schema)
    total   = len(exp.runs)
    buf     = []

    L = Logger()

    M = Manager(name=args.name, ip=args.addr, port=args.port, workers=exp.workers, map=exp.map) 
    L.record(f"{args.name.upper()} UP")

    try:
        M.establish()
        L.record(f"CONNECTED[{len(M.workers)}]")

        for i,run in enumerate(exp.runs):
            name    = run.data["name"]
            expr    = f"[RUN={run.data['name']}] {i + 1}/{total}"
            start   = time.time()

            L.state(f"STATE{expr}")

            # building tree with lemondrop
            if "LEMON" in name:
                for j,ret in enumerate(M.lemon(run, interval=10)): 
                    result, elapsed = ret
                    buf.append([ item["p50"] for item in result["items"] ])
                    L.record(f"LEMON RESULT: {j + 1}/{len(M.workers)} {expr}")

                run.data["timers"]["build"] = (time.time() - start)

                LD = LemonDrop(OWD=buf, VMS=M.workers, K=run.tree.nmax, D=run.tree.dmax, F=run.tree.fanout)
                mapping, converged, elapsed = LD.solve(epsilon=run.data["parameters"]["epsilon"], max_i=run.data["parameters"]["max_i"])
                run.data["timers"]["convergence"]  = elapsed
                run.data["parameters"]["converge"] = converged
                run.tree.root.id                   = mapping[0][1]
                run.tree.n_add([ m[1] for m in mapping[1:] ])
                L.record(f"TREE[{run.tree.name}] CONVERGENCE={converged} TOOK {elapsed} SECONDS {expr}")

                buf.clear()

            # building tree with rng
            elif name == "RAND":
                for i, result in enumerate(M.rand(run)):
                    addrs = [ d for d in result["selected"] ]
                    run.tree.n_add(addrs)
                    L.record(f"TREE[{run.tree.name}] SELECTION[ROOT: {result['root']} => {run.tree.n}/{run.tree.nmax}]: {expr}")

            # building tree with heuristic
            else:
                for i,ret in enumerate(M.build(run)):
                    result, elapsed = ret
                    addrs = [ d for d in result["selected"] ]
                    run.tree.n_add(addrs)
                    run.pool.n_remove(addrs)
                    run.data["stages"].append(result)
                    run.data["timers"]["stages"].append(elapsed)
                    L.record(f"TREE[{run.tree.name}] SELECTION[ROOT: {result['root']} => {run.tree.n}/{run.tree.nmax}]: {expr}")
                    L.record(f"STAGE TOOK {elapsed} seconds")

                run.data["timers"]["build"] = (time.time() - start)

            # store tree
            run.data["tree"] = run.tree.get()
            
            # evaluate tree
            perfs = len(run.data["perf"])
            for i in range(perfs):
                result, elapsed = M.evaluate(run)
                run.data["perf"][i]            = result
                run.data["timers"]["perf"][i]  = elapsed
                L.record(f"TREE[{run.tree.name}] PERFORMANCE[{result['selected'][0]}] I={i + 1}/{perfs}: {result['items'][0]['p90']} {expr}")
                L.record(f"EVALUATION TOOK {elapsed} seconds")
            

            # record run
            run.data["timers"]["total"] = (time.time() - start)
            L.event({"RUN": run.data})

            # rebuild
            for k in range(run.data["parameters"]["rebuild"]):
                L.record(f"REBUILDING TREE[{run.tree.name}]")
                run.data["name"] = f"{name}-REBUILD-{k+1}"
                run.tree.name    = run.data["name"]

                start  = time.time()
                parent = None
                max    = 0
                addr   = ""
                for perf in run.data["perf"]:
                    rmax  = perf['items'][0]['p90']
                    raddr = perf['selected'][0]

                    if rmax > max: 
                        max  = rmax
                        addr = raddr

                for lnode in run.tree.leaves():
                    if lnode.id == addr:
                        parent = lnode.parent
                        break

                if parent is None:
                    raise RuntimeError(f"IDENTIFYING BAD LEAF FAILED!")

                root      = parent.id
                children  = [ c.id for c in parent.children ]

                stage     = time.time()
                result    = M.rebuild(run, root, children)
                addrs     = [ d    for d in result["selected"] ]
                elapsed   = time.time() - stage

                run.data["stages"].clear()
                run.data["timers"]["stages"].clear()
                run.data["stages"].append(result)
                run.data["timers"]["stages"].append(elapsed)
                L.record(f"TREE[{run.tree.name}] SELECTION[ROOT: {result['root']} => {run.tree.n}/{run.tree.nmax}]: {expr}")
                L.record(f"STAGE TOOK {elapsed} seconds")

                for i,a in enumerate(addrs):
                    L.record(f"TREE[{run.tree.name}] REPLACING {children[i]} => {a}")
                    parent.children[i].id = a
                    if a not in children: run.pool.remove(a)
                    else:                 children.pop(children.index(a))

                for c in children: 
                    run.pool.add(c)

                for i in range(perfs):
                    result, elapsed = M.evaluate(run)
                    run.data["perf"][i]            = result
                    run.data["timers"]["perf"][i]  = elapsed
                    L.record(f"TREE[{run.tree.name}] PERFORMANCE[{result['selected'][0]}] I={i + 1}/{perfs}: {result['items'][0]['p90']} {expr}")
                    L.record(f"EVALUATION TOOK {elapsed} seconds")

                run.data["timers"]["total"] = (time.time() - start)
                L.event({"RUN": run.data})

    except Exception as e:
        L.error("INTERRUPTED!")
        raise e

    finally:
        L.flush()
        M.flush()
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

    L.record("FINISHED!")
