from . import base
from . import aws
from . import gcp

def cloud(type:str) -> base.Cloud:
    if (type == "gcp"):
        return gcp.GCP()
    elif (type == "aws"):
        return aws.AWS()
    else:
        raise NotImplementedError(f"No cloud class for {type}")

