from .message  import *
from .types    import *

from typing     import List

import heapq

KEYS = [
    "p90",
    "p75",
    "p50",
    "stddev",
]

HMAP = {
    "heuristic": lambda x: x["p90"]*0.3 + x["stddev"]*0.7
}

for key in KEYS:
    HMAP[key] = lambda x, k=key: x[k]

class Heuristic():
    def __init__(self, strategy:StrategyDict, command:Command, job:Job):
        self.strategy:StrategyDict = strategy
        self.flag = job.flag
        self.data:ResultDict = {
                "root": job.addr,
                "key": self.strategy["key"],
                "select": command.select, 
                "rate": command.rate,
                "duration": command.duration,
                "items": self.items(job),
                "selected": []
        }

        if strategy["key"] not in HMAP:
            raise RuntimeError(f"Invalid Key: {strategy['key']}")

    def items(self, job:Job) -> List[ItemDict]:
        items = []
        for j,i in enumerate(range(0, len(job.floats), 5)):
            item: ItemDict = {
                    "addr":     job.data[j],
                    "p90":      job.floats[i],
                    "p75":      job.floats[i + 1],
                    "p50":      job.floats[i + 2],
                    "p25":      job.floats[i + 3],
                    "stddev":   job.floats[i + 4],
                    "recv":     job.integers[j],
            }
            items.append(item)

        return items

    def process(self, key:str=""):
        key     = self.data["key"] if not key else key
        items   = self.data["items"]
        select  = self.data["select"]
        reverse = self.strategy["reverse"]

        l = HMAP[key]

        # parent job
        if self.flag == Flag.PARENT: 
            sorted = heapq.nsmallest(len(items), items, key=l)
            if reverse: 
                self.data["selected"] = [ s["addr"] for s in [ w for w in reversed(sorted[(-1 * select):]) ] ]
            else:       
                self.data["selected"] = [ s["addr"] for s in sorted[:select] ]

        # mcast job
        else:        
            sorted = heapq.nlargest(len(items),  items, key=l)
            self.data["selected"] = [ s["addr"] for s in sorted[:select] ]

        for i in range(len(self.data["items"])):
            self.data["items"][i] = sorted[i]
