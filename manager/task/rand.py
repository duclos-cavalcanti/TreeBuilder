
from ..message      import *
from ..types        import Run, ResultDict, ItemDict
from .task          import Task

from typing     import List, Tuple

class Rand(Task):
    def build(self, run:Run) -> Command:
        return Command()

    def handle(self, command:Command) -> Tuple[Job, List[Command]]:
        return Job(), [ Command() ]

    def process(self) -> Job:
        return Job()

    def evaluate(self, job:Job, run:Run) -> ResultDict:
        data:ResultDict = {
                "root": run.tree.next(),
                "key": run.data["strategy"]["key"],
                "select": 1, 
                "rate": run.data["parameters"]["rate"],
                "duration": run.data["parameters"]["duration"],
                "items": [],
                "selected": []
        }
        arr = run.pool.slice()
        for a in arr:                       
            item: ItemDict = {
                    "addr":     a,
                    "p90":      0.0,
                    "p75":      0.0,
                    "p50":      0.0,
                    "p25":      0.0,
                    "stddev":   0.0,
                    "recv":     0,
            }
            data["items"].append(item)

        for _ in range(run.tree.fanout):    
            data["selected"].append(run.pool.select(arr))
        
        return data
