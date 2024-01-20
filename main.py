import os
import sys
import subprocess
import argparse
import yaml

STACK   = "duclos-dev"
BUCKET  = "duclos-dev-storage"
CONFIG  = "./build/instance.yaml"

DEPLOY  =   f"gcloud deployment-manager -q deployments create {STACK} --config"
DELETE  =   f"gcloud deployment-manager -q deployments delete {STACK}"
COPY    =   f"gcloud storage cp"

def upload(src, dst, origin=f"{BUCKET}"):
    command=f"{COPY} {src} gs://{origin}/{dst}"
    subprocess.run(command, shell=True)
    return

def pkg():
    folder="dom-tenant-service"
    package = "bundle.tar.gz"
    if os.path.exists(package):
        os.remove(package)

    command = f"tar -czf ./build/{package} --exclude .git -C ./{folder}/ ."
    subprocess.run(command, shell=True)

    upload(f"./build/{package}", package)
    upload("./assets/startup/base.sh", "base.sh")
    upload("./assets/startup/client.sh", "client.sh")
    upload("./assets/startup/proxy.sh", "proxy.sh")
    upload("./assets/startup/recipient.sh", "recipient.sh")
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
    instances = [ "base-dev", "client-dev", "proxy-dev", "recipient-dev"]

    data = load_yaml(base)
    for i in range(len(data["resources"])):
        name = data["resources"][i]["name"] 

        if name not in instances:
            print(f"Unexpected yaml file format, name of resource is {name}, not found in instances array!")
            sys.exit(1)

        script = instances[instances.index(name)][:-len("-dev")]
        startup = f"""
            #!/bin/bash
            pushd /home/uab2005/
            gcloud storage cp gs://{BUCKET}/{script}.sh ./{script}.sh 
            chmod +x ./{script}.sh 
            ./{script}.sh
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
        case "deploy":
            deploy()
        case "delete":
            delete()

    return


if __name__ == "__main__":
    main()
