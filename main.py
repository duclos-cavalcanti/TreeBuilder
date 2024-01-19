import os
import sys
import subprocess
import argparse
import yaml

STACK   = "duclos-dev"
BUCKET  = "cdm-templates-nyu-systems-multicast"

DEPLOY  =   f"gcloud deployment-manager -q deployments create {STACK} --config"
DELETE  =   f"gcloud deployment-manager -q deployments delete {STACK}"
COPY    =   f"gcloud storage cp"

def upload(src, dst, origin=f"{BUCKET}"):
    command=f"{COPY} {src} gs://{origin}/{dst}"
    subprocess.run(command, shell=True)
    return

def pkg():
    package = "bundle.tar.gz"
    if os.path.exists(package):
        os.remove(package)

    command = f"tar -czf {package} --exclude={package} --exclude analysis --exclude .git -C ./dom-tenant-service/ ."
    subprocess.run(command, shell=True)

    upload(package, package)
    upload("./scripts/client.sh", "client.sh")
    upload("./scripts/proxy.sh", "proxy.sh")
    upload("./scripts/recipient.sh", "recipient.sh")
    return

def template():
    def load_yaml(n):
        with open(n, "r") as stream:
            return yaml.safe_load(stream)
    
    def write_yaml(n, data):
        with open(n, "w") as stream:
            yaml.dump(data, stream)

    base = "./templates/base.yaml"
    instance = "./templates/instance.yaml"
    instances = [ "client", "proxy", "recipient"]

    data = load_yaml(base)
    for i in (0, 1, 2):
        name = data["resources"][i]["name"] 
        if instances[i] not in data["resources"][i]["name"]:
            print(f"Unexpected yaml file format, name of resource is {name}, no relation to {instances[i]}!")
            sys.exit(1)

        startup = f"#!/bin/bash\ngcloud storage cp gs://{BUCKET}/{instances[i]}.sh ./{instances[i]}.sh\nchmod +x ./{instances[i]}.sh\n./{instances[i]}.sh\n"
        data["resources"][i]["properties"]["metadata"]["items"][0]["value"] = startup

    write_yaml(instance, data)
    return

def deploy():
    template = "./templates/instance.yaml"
    if not os.path.exists(template):
        print(f"Template file doesn't exist: {template}!")
        sys.exit(1)

    command = f"{DEPLOY} {template}"
    subprocess.run(command, shell=True)
    return

def delete():
    command = f"{DELETE} ${STACK}"
    subprocess.run(command, shell=True)
    return

def parse():
    arg_def = argparse.ArgumentParser()
    arg_def.add_argument(
        "action",
        choices=["template", "deploy", "delete", "package"],
        help="Example: python3 main.py <action>"
    )

    return arg_def.parse_args()

def main():
    args = parse()

    match args.action:
        case "template":
            template()
        case "package":
            pkg()
        case "deploy":
            deploy()
        case "delete":
            delete()


if __name__ == "__main__":
    main()
