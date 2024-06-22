from typing     import TypedDict, List

class ItemDict(TypedDict):
    addr: str 
    p90: float 
    p75: float 
    p50: float 
    p25: float 
    stddev: float 
    recv: int

class Parameters(TypedDict):
    select: int 
    rate: int
    duration: int
    packets: int

class ResultDict(TypedDict):
    root: str
    key:  str
    select: int 
    rate: int 
    duration: int
    items: List[ItemDict]
    selected: List[str]

class StrategyDict(TypedDict):
    key: str 
    expr: dict
    reverse: bool 
    rand: bool 

class ParametersDict(TypedDict):
    hyperparameter: int 
    rate: int 
    duration: int 

class TreeDict(TypedDict):
    name: str 
    depth: int 
    fanout: int 
    n: int 
    max: int 
    root: str 
    nodes: List[str]

class RunDict(TypedDict):
    name:str 
    strategy: StrategyDict
    parameters: ParametersDict
    tree: TreeDict
    pool: List[str] 
    stages: List[ResultDict]
    perf: ResultDict
