import subprocess
import argparse

import instance

def store(src, dst, origin=f"duclos-dev-storage"):
    command=f"gcloud storage cp {src} gs://{origin}/{dst}"
    subprocess.run(command, shell=True)
    return

def template(name="vanilla"):
    i = instance.Instance()
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

def parse():
    arg_def = argparse.ArgumentParser(
        description='Script to automate GCP stack launch.',
        epilog='Example: main.py --action/-a pull -p <prefix>'
    )

    arg_def.add_argument(
        "-a", "--action",
        type=str,
        choices=["deploy", "delete"],
        dest="action",
    )

    return arg_def.parse_args()

def main():
    args = parse()

    match args.action:
        case "deploy": deploy()
        case "delete": delete()

    return


if __name__ == "__main__":
    main()
