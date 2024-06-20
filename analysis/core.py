import subprocess
import os
import shutil

from .parse import Parser
from .plot  import Plotter
from .utils import *

def pull(args):
    if args.infra == "gcp":
        command = "gcloud storage ls gs://exp-results-nyu-systems-multicast/"
        ret     = subprocess.run(command.split(), stdout=subprocess.PIPE, text=True)
        arr     = ret.stdout.strip().split('\n')
        for a in arr:
            if args.prefix in a:
                dir = a.split("/")[-2]
                root = os.path.join(os.getcwd(), "analysis", "data")
                path = os.path.join(os.getcwd(), "analysis", "data", dir)
                if not os.path.isdir(path):
                    os.system(f"gcloud storage cp --recursive gs://exp-results-nyu-systems-multicast/{dir}* {root}")
                    extract(path)

                return

        raise RuntimeError(f"No bucket found on GCP matching: {args.prefix}")

    if args.infra == "docker":
        dir = isdir("infra/terra/docker/modules/default/volume")
        src = find(dir=dir, pattern=f"treefinder")
        dst = isdir("analysis/data")
        shutil.move(src,  dst)
        extract(f"{dst}/{src.split('/')[-1]}")

def process(args):
    if args.infra == "docker":
        dir = isdir("analysis/data")
        dir = find(dir=dir, pattern=f"treefinder-{args.infra}")
        P = Plotter(Parser(dir=os.path.join(dir, "logs")))
        P.plot(dir)

