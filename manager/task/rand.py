from ..message      import *
from ..types        import Run, ItemDict, ResultDict
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
                "id": f"rand-{run.tree.root.id}",
                "root": run.tree.next(),
                "key": run.data["strategy"]["key"],
                "select": 1, 
                "rate": run.data["parameters"]["rate"],
                "duration": run.data["parameters"]["duration"],
                "items": [],
                "selected": []
        }

        for _ in range(run.tree.fanout):    
            data["selected"].append(run.pool.select())
        
        self.L.debug(message=f"TASK EVAL[{Flag.Name(job.flag)}][{job.id}:{job.addr}]", data=data)
        return data
