from typing     import TypedDict, List

class ItemDict(TypedDict):
    addr: str 
    p90: float 
    p75: float 
    p50: float 
    p25: float 
    stddev: float 
    mean: float 
    recv: int

class ResultDict(TypedDict):
    id: str
    root: str
    key:  str
    select: int 
    rate: int 
    duration: int
    items: List[ItemDict]
    selected: List[str]

class StrategyDict(TypedDict):
    key: str 
    reverse: bool 

class ParametersDict(TypedDict):
    num: int
    choices: int
    hyperparameter: int 
    rate: int 
    duration: int 
    evaluation: int 
    warmup: int
    epsilon: float 
    max_i: int
    converge: bool
    stress: bool

class TreeDict(TypedDict):
    name: str 
    depth: int 
    fanout: int 
    n: int 
    max: int 
    root: str 
    nodes: List[str]

class TimersDict(TypedDict):
    build: float
    stages:  List[float]
    convergence: float
    perf:  List[float]
    total: float

class RunDict(TypedDict):
    name:str 
    strategy: StrategyDict
    parameters: ParametersDict
    tree: TreeDict
    pool: List[str] 
    stages: List[ResultDict]
    perf: List[ResultDict]
    timers: TimersDict
