import os
import json
import subprocess

from manager  import Timer, TreeBuilder, RunDict, StrategyDict, ParametersDict, TreeDict, ResultDict, TimersDict
from datetime import datetime

def execute(command:str, wdir=None):
    if not wdir: wdir = os.getcwd()

    ret = 0
    out = bytes() 
    err = bytes()

    try:
        print(f"{command}")

        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=wdir)
        for line in p.stdout: 
            print(line.decode('utf-8'), end='')

        p.wait()

        ret = p.returncode
        out = p.stdout.read()
        err = p.stderr.read()

    except Exception as e:
        raise(e)

    finally: 
        if ret != 0:
            print(f"ERR[{ret}]:")
            print(err.decode('utf-8'))
            raise RuntimeError()

    return out

def run(name:str, key:str, args, epsilon:float=1e-4, max_i:int=1000, stress:bool=False):
    r:RunDict = RunDict({
            "name": name,
            "strategy": StrategyDict({
                "key": key, 
                "reverse": name == "WORST",
            }), 
            "parameters": ParametersDict({
                "num": args.num,
                "choices": args.choices,
                "rebuild": 0,
                "hyperparameter": args.fanout * 2,
                "rate": args.rate, 
                "duration": args.duration,
                "evaluation": args.evaluation,
                "warmup": args.warmup,
                "epsilon": epsilon, 
                "max_i": max_i,
                "converge": False,
                "stress": stress,
            }),
            "tree": TreeDict({
                "name": "", 
                "depth": args.depth, 
                "fanout": args.fanout,
                "n": 0, 
                "max": 0,
                "root": "",
                "nodes": []
            }), 
            "pool": [],
            "stages": [],
            "perf":  [ ResultDict({
                "id": "",
                "root": "",
                "key": key,
                "select": 0, 
                "rate": args.rate,
                "duration": args.duration,
                "items": [],
                "selected": []
            }) for _ in range(args.num) ], 
            "timers": TimersDict({
                    "build": 0.0,
                    "stages": [],
                    "convergence": 0.0,
                    "perf": [ 0.0 for _ in range(args.num) ],
                    "total": 0.0,
            })
    })
    return r

def runs(args):
    runs  = []
    names = [ "BEST" ]
    keys  = [ "p90", "p50", "heuristic" ]

    if args.infra == "gcp":
        if args.mode == "default":
            # for name in names:
            #     for key in keys:
            #         r = run(name, key, args)
            #         r["parameters"]["rebuild"] = args.rebuild
            #         runs.append(r)

            # runs.append(run(name="WORST",  key="p90",  args=args))
            # runs.append(run(name="RAND",   key="NONE", args=args))

            runs.append(run(name="LEMON-A",           key="NONE", args=args, epsilon=1e-4,     max_i=1000,     stress=False))
            runs.append(run(name="LEMON-B",           key="NONE", args=args, epsilon=2.2e-5,   max_i=10000,    stress=False))
            runs.append(run(name="LEMON-C",           key="NONE", args=args, epsilon=1.7e-5,   max_i=100000,   stress=False))

            runs.append(run(name="LEMON-A-STRESS",    key="NONE", args=args, epsilon=1e-4,     max_i=1000,     stress=True))
            runs.append(run(name="LEMON-B-STRESS",    key="NONE", args=args, epsilon=2.2e-5,   max_i=10000,    stress=True))
            runs.append(run(name="LEMON-C-STRESS",    key="NONE", args=args, epsilon=1.7e-5,   max_i=100000,   stress=True))

        else:
            raise NotImplementedError()
    else:
        if args.mode == "default":
            runs.append(run(name="BEST",  key="heuristic",  args=args))

        if args.mode == "lemondrop":
            hyperparameters = [ (1e-4, 1000), (5.5e-5, 10000), (1e-5, 10000) ]
            for tup in hyperparameters:
                epsilon, max_i = tup
                runs.append(run(name="LEMON", key="NONE", args=args, epsilon=epsilon, max_i=max_i))

    return runs

def commands(args, addrs):
    commands = []

    match args.mode:
        case "mcast":
            tb  = TreeBuilder(arr=addrs, depth=args.depth, fanout=args.fanout)
            ret = tb.mcast(rate=args.rate, duration=args.duration, id="example", warmup=args.warmup)
            commands.extend(ret.buf)

        case "udp":
            tb  = TreeBuilder(arr=addrs, depth=1, fanout=len(addrs[1:]))
            ret = tb.parent(rate=args.rate, duration=args.duration, id="example", warmup=args.warmup)
            commands.extend(ret.buf)

        case "lemon":
            t = Timer()
            future = t.future_ts(args.duration + 25)
            commands.extend( [ f"./bin/lemon -i {addr} -p {6066} -s docker -f {future}" for addr in addrs[1:]] )

        case _: 
            pass

    return commands

def config(args, path):
    base_addr   = "10.1.1." if args.infra == "docker" else "10.1.25."
    base_saddr  = "10.1.0." if args.infra == "docker" else "10.0.25."
    addrs       = [ f"{base_addr}{i + 1}" for i in range(args.size + 1) ]
    saddrs      = [ f"{base_saddr}{i + 1}" for i in range(args.size + 1) ]
    names       = [ "manager" ] + [ f"worker{i}" for i in range(args.size) ]
    data        = {
            "infra": args.infra,
            "suffix": datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
            "port": args.port,
            "addrs": addrs,
            "saddrs": saddrs,
            "names": names,
            "map": {},
            "commands": commands(args, addrs) if (args.infra == "docker" and args.mode != "default") else [],
            "runs": runs(args),
    }

    for addr, name in zip(data["addrs"], data["names"]):
        data["map"][f"{addr}:{data['port']}"] = name

    with open(path, "w") as file: 
        json.dump(data, file, indent=4)

    del data["commands"]

    with open("schemas/default.json", "w") as file: 
        json.dump(data, file, indent=4)

    return data

def build(args, wdir):
    command=f"packer build -force -var-file=./variables.pkr.hcl {args.infra}.pkr.hcl"
    execute(f"{command}", wdir=wdir)

def plan(args, wdir):
    config(args, f"{wdir}/extract/data.json")
    command = "tar --exclude=jasper \
		           --exclude=project.tar.gz \
		           --exclude=.git \
		           --exclude=.gitkeep \
		           --exclude=.gitignore \
		           --exclude=.gitmodules \
		           --exclude=examples \
		           --exclude=lib \
		           --exclude=build \
		           --exclude=docs \
		           --exclude=.cache \
		           --exclude=terra \
		           --exclude=infra \
		           --exclude=analysis \
		           --exclude-vcs-ignores \
		           -zcvf"

    execute(f"{command} {wdir}/extract/project.tar.gz .")
    execute(f"terraform init", wdir=wdir)
    execute(f"terraform plan -out=tf.plan -var mode={args.mode}", wdir=wdir)

def deploy(args , wdir):
    execute(f"terraform apply tf.plan", wdir=wdir)

def destroy(args, wdir):
    execute(f"terraform destroy -auto-approve", wdir=wdir)

