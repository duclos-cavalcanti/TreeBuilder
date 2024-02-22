from . import base

class GCP(base.Cloud):
    __instance="c2d-highcpu-8"
    __base = {
        "name": "REPLACE",
        "type": "compute.v1.instance",
        "properties": {
            "zone": "us-east4-c",
            "machineType": f"zones/us-east4-c/machineTypes/{__instance}",
            "serviceAccounts": {
                "email": "multicast-service-vm@multicast1.iam.gserviceaccount.com",
                "scopes": [
                    "https://www.googleapis.com/auth/cloud-platform",
                ]
            },
            "disks": {
                "deviceName": "boot",
                "type": "PERSISTENT",
                "boot": "true",
                "autoDelete": "true",
                "initializeParams": "true",
            },
            "networkInterfaces": {},
            "metadata": {
                "items": {
                    "key": "startup-script-url",
                    "value": "REPLACE",
                }
            },
        }
    }

    def __init__(self):
        print("GCP Initialized")

    def print(self):
        """docstring for print"""
        print(self.__base)
        
    pass
