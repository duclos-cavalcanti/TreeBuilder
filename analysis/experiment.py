from typing import List, TypedDict

class Performance(TypedDict):
    root: str 
    key: str 
    data: List[dict]
    params: dict 
    selected: List[str]

class Stage(TypedDict):
    root: str 
    key: str 
    data: List[dict]
    params: dict 
    selected: List[str]
    pool: List 

class Data(TypedDict):
    name: str 
    strategy: dict 
    params: dict 
    pool: List 
    tree: dict 
    stages: List[Stage] 
    perf: dict

class Experiment():
    def __init__(self):
        self.data:Data = {
                "name": "", 
                "strategy": {},
                "params": {},
                "pool": [],
                "tree": {},
                "stages": [],
                "perf": {}
        }

    def stage(self, root:str, key:str, data:List[dict], params:dict, selected:List[str], pool:List[str]):
        s:Stage = {
                "root": root, 
                "key": key,
                "data": data,
                "params": params,
                "selected": selected,
                "pool": pool
        }
        self.data["stages"].append(s)

    def performance(self, root:str, key:str, data:List[dict], params:dict, selected:List[str]):
        p = {
                "root": root, 
                "key": key,
                "data": data,
                "params": params,
                "selected": selected,
        }
        self.data["perf"] = p

