import yaml

def read_yaml(f:str):
    data = {}
    with open(f, 'r') as file:
        data = yaml.safe_load(file)
    return data
