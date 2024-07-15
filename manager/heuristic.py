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

EXPRESSIONS = {
    "p90":          lambda x, k="p90": x[k],
    "p75":          lambda x, k="p75": x[k],
    "p50":          lambda x, k="p50": x[k],
    "stddev":       lambda x, k="stddev": x[k],
    "heuristic":    lambda x: x["p90"]*0.3 + x["stddev"]*0.7
}

class Heuristic():
    def __init__(self, strategy:StrategyDict, command:Command, job:Job):
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

        data:ResultDict = {
                "root": job.addr,
                "key": strategy["key"],
                "select": command.select, 
                "rate": command.rate,
                "duration": command.duration,
                "items": items,
                "selected": []
        }

        self.strategy:StrategyDict = strategy
        self.flag                  = job.flag
        self.data:ResultDict       = data

        if strategy["key"] not in EXPRESSIONS and strategy["key"] != "NONE":
            raise RuntimeError(f"Invalid Key: {strategy['key']}")

    def process(self, key:str=""):
        key     = self.data["key"] if not key else key
        items   = self.data["items"]
        select  = self.data["select"]
        reverse = self.strategy["reverse"]

        l = EXPRESSIONS[key]

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
