import os
import sys
import subprocess
import argparse
import yaml

STACK   = "duclos-dev"

DEPLOY  =   f"gcloud deployment-manager -q deployments create {STACK} --config"
DELETE  =   f"gcloud deployment-manager -q deployments delete {STACK}"
COPY    =   f"gcloud storage cp"

def upload(src, dst, origin="cdm-templates-nyu-systems-multicast"):
    command=f"{COPY} {src} gs://{origin}/{dst}"
    subprocess.run(command, shell=True)

def pkg():
    package = "bundle.tar.gz"
    if os.path.exists(package):
        os.remove(package)

    command = f"tar -czf {package} --exclude={package} --exclude analysis --exclude .git -C ./dom-tenant-service/ ."
    subprocess.run(command, shell=True)

    upload(package, package)
    return

def template():
    def load_file(n):
        with open(n, "r") as f:
            return str(f.read())

    def load_yaml(n):
        with open(n, "r") as stream:
            return yaml.safe_load(stream)
    
    def write_yaml(n, data):
        with open(n, "w") as stream:
            yaml.dump(data, stream)

    ret = "./vms/instance.yaml"
    base = "./vms/base.yaml"
    instances = [ "client", "proxy", "recipient"]

    data = load_yaml(base)
    for i in (0, 1, 2):
        typ = instances[i]
        name = data["resources"][i]["name"] 

        if name == typ:
            data["resources"][i]["properties"]["metadata"]["items"][0]["value"] = load_file(f"./vms/startup/{typ}.sh")
        else:
            print(f"Unexpected yaml file format, name of resource is {name} and expected: {typ}")
            sys.exit(1)

    write_yaml(ret, data)
    return ret

def deploy():
    instance = template()
    pkg()
    command = f"{DEPLOY} {instance}"
    subprocess.run(command, shell=True)

def delete():
    command = f"{DELETE} ${STACK}"
    subprocess.run(command, shell=True)

def parse():
    arg_def = argparse.ArgumentParser()
    arg_def.add_argument(
        "action",
        choices=["deploy", "delete", "package"],
        help="Example: python3 main.py create deploy"
    )

    return arg_def.parse_args()

def main():
    args = parse()

    match args.action:
        case "deploy":
            deploy()
        case "delete":
            return
        case "package":
            pkg()


if __name__ == "__main__":
    main()
