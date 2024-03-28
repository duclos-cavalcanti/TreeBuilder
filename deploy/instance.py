import os
import yaml
import datetime

def _timestamp():
    cur = datetime.datetime.now()
    cur = cur.strftime("%H:%M:%S")
    cur = cur[:8]
    cur = cur.replace(":", "")
    return cur

class Instance():
    def __init__(self):
        self.zone = 'us-east4-c'
        self.disks      = {
            'autoDelete': True,
            'boot': True,
            'deviceName': 'boot',
            'initializeParams': {
                'sourceImage': 'projects/multicast1/global/images'
            },
            'type': 'PERSISTENT'
        }
        self.machineType = "zones/us-east4-c/machineTypes"
        self.metadata = {
            'items': [
                {   
                    'key': 'startup-script', 
                    'value': 'ls /'
                },
            ]
        }
        self.networkInterfaces = [
            {
                'accessConfigs': [
                    {'networkTier': 'PREMIUM', 'type': 'ONE_TO_ONE_NAT'}
                ],
                'network': 'projects/multicast1/global/networks/multicast-management',
                'networkIP': '10.1.1.255',
                'nicType': 'GVNIC',
                'stackType': 'IPV4_ONLY',
                'subnetwork': 'projects/multicast1/regions/us-east4/subnetworks/multicast-management'
            },
            {
                'network': 'projects/multicast1/global/networks/multicast-service',
                'networkIP': '10.0.1.255',
                'nicType': 'GVNIC',
                'stackType': 'IPV4_ONLY',
                'subnetwork': 'projects/multicast1/regions/us-east4/subnetworks/multicast-service'
            }
        ]
        self.serviceAccounts = [
            {
                'email': 'multicast-service-vm@multicast1.iam.gserviceaccount.com',
                'scopes': ['https://www.googleapis.com/auth/cloud-platform']
            }
        ]

    def set_ips(self, ip:str):
        raise(NotImplementedError)

    def set_disk(self, disk="multicast-ebpf-zmq-grub-disk"):
        src = self.disks["initializeParams"]["sourceImage"]
        src = f"{src}/{disk}"
        self.disks["initializeParams"]["sourceImage"] = src

    def set_machine(self, machine:str="c2d-highcpu-8"):
        self.machineType = f"{self.machineType}/{machine}"

    def set_zone(self, zone="us-east4-c"):
        self.zone = f"{zone}"

    def generate(self, name):
        ts = _timestamp()
        data = {
            'resources': [
                {
                    'name': f"{name}",
                    'properties': {
                        'disks': [self.disks],
                        'machineType': self.machineType,
                        'metadata': self.metadata,
                        'networkInterfaces': self.networkInterfaces,
                        'serviceAccounts': self.serviceAccounts,
                        'zone': self.zone
                    },
                    'type': 'compute.v1.instance'
                }
            ]
        }
        ret = f"build/stack_{ts}.yaml"
        with open(ret, "w") as stream: yaml.dump(data, stream)
        return ret
