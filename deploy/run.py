import subprocess
import argparse

from . import gen

def store(src, dst, origin=f"duclos-dev-storage"):
    command=f"gcloud storage cp {src} gs://{origin}/{dst}"
    subprocess.run(command, shell=True)
    return

def template(name="vanilla"):
    i = gen.Instance()
    i.set_disk(disk="multicast-ebpf-zmq-grub-disk")
    i.set_machine(machine="c2d-highcpu-8")
    i.set_zone(zone="us-east4-c")
    return i.generate(name)

def deploy(stack="duclos-dev"):
    config = template()
    command = f"gcloud deployment-manager -q deployments create {stack} --config {config}"
    print(f"LAUNCHED: {config}")
    subprocess.run(command, shell=True)
    return

def delete(stack="duclos-dev"):
    command = f"gcloud deployment-manager -q deployments delete {stack}"
    subprocess.run(command, shell=True)
    return

def instance(args):
    if (not args.name): 
        raise ValueError("name argument was not passed to instance action!")

    if (not args.command): 
        raise ValueError("command argument was not passed to instance action!")

    command = f"gcloud compute instances {args.command} {args.name} --zone 'us-east4-c' --project multicast1"
    subprocess.run(command, shell=True)

    if args.command == "start":
        print(f"SSH: gcloud compute ssh --zone 'us-east4-c' {args.name} --tunnel-through-iap --project 'multicast1'")

def parse(rem=None):
    arg_def = argparse.ArgumentParser(
        description='Script to automate GCP stack launch.',
        epilog='Example: main.py --action/-a pull -p <prefix>'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        required=True,
        choices=["deploy", "delete", "instance"],
        dest="action",
    )

    arg_def.add_argument(
        "-c", "--command",
        type=str,
        required=False,
        choices=["start", "reset", "suspend", "stop", "describe"],
        dest="command",
    )

    arg_def.add_argument(
        "-n", "--name",
        type=str,
        required=False,
        dest="name",
    )

    if not rem: args = arg_def.parse_args()
    else: args = arg_def.parse_args(rem)

    return args

def run(rem):
    args = parse(rem)
    # for arg, value in vars(args).items():
    #         print(f"{arg}: {value}")

    match args.action:
        case "deploy":  deploy()
        case "delete":  delete()
        case "instance": instance(args)

    return


if __name__ == "__main__":
    run(rem=None)
