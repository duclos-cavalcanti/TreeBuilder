import os
import sys
import subprocess
import argparse
import yaml

STACK   = "duclos-dev"
CONFIG  = "./build/instance.yaml"
BUCKET  = "duclos-dev-storage"

DEPLOY  =   f"gcloud deployment-manager -q deployments create {STACK} --config"
DELETE  =   f"gcloud deployment-manager -q deployments delete {STACK}"
COPY    =   f"gcloud storage cp"

def upload(src, dst, origin=f"{BUCKET}"):
    command=f"{COPY} {src} gs://{origin}/{dst}"
    subprocess.run(command, shell=True)
    return

def pkg_scripts():
    upload("./assets/client.sh", "client.sh")
    upload("./assets/proxy.sh", "proxy.sh")
    upload("./assets/recipient.sh", "recipient.sh")

def pkg():
    package = "bundle.tar.gz"
    if os.path.exists(package):
        os.remove(package)

    command = f"tar -czf {package} --exclude .git -C ./src/ ."
    subprocess.run(command, shell=True)
    upload(package, package)

    pkg_scripts()
    return

def template():
    def load_yaml(n):
        with open(n, "r") as stream:
            return yaml.safe_load(stream)
    
    def write_yaml(n, data):
        with open(n, "w") as stream:
            yaml.dump(data, stream)

    base = "./assets/base.yaml"
    instance = CONFIG
    instances = [ "client", "proxy", "recipient"]

    data = load_yaml(base)
    for i in (0, 1, 2):
        name = data["resources"][i]["name"] 
        if instances[i] not in data["resources"][i]["name"]:
            print(f"Unexpected yaml file format, name of resource is {name}, no relation to {instances[i]}!")
            sys.exit(1)

        startup = f"""
            #!/bin/bash
            pushd /home/uab2005/
            gcloud storage cp gs://{BUCKET}/{instances[i]}.sh ./{instances[i]}.sh 
            chmod +x ./{instances[i]}.sh 
            ./{instances[i]}.sh
            popd
        """        
        data["resources"][i]["properties"]["metadata"]["items"][0]["value"] = startup

    write_yaml(instance, data)
    return

def deploy():
    if not os.path.exists(CONFIG):
        print(f"Template file doesn't exist: {CONFIG}!")
        sys.exit(1)

    command = f"{DEPLOY} {CONFIG}"
    subprocess.run(command, shell=True)
    return

def delete():
    command = f"{DELETE} {STACK}"
    subprocess.run(command, shell=True)
    return

def parse():
    arg_def = argparse.ArgumentParser()
    arg_def.add_argument(
        "action",
        choices=["template", "deploy", "delete", "package", "scripts"],
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
        case "scripts":
            pkg_scripts()
        case "deploy":
            deploy()
        case "delete":
            delete()

    return


if __name__ == "__main__":
    main()
