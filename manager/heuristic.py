from .message  import *
from .types    import *

from typing     import List

import heapq

KEYS = [
    "p90",
    "p50",
    "stddev",
]

EXPRESSIONS = {
    "p90":          lambda x, k="p90": x[k],
    "p50":          lambda x, k="p50": x[k],
    "stddev":       lambda x, k="stddev": x[k],
    "heuristic":    lambda x: x["p90"]*0.3 + x["stddev"]*0.7,
    "NONE":         lambda x, k="p90": x[k],
}

class Heuristic():
    def __init__(self, data:ResultDict, strategy:StrategyDict):
        self.data:ResultDict       = data
        self.strategy:StrategyDict = strategy

        if data["key"] not in EXPRESSIONS and data["key"] != "NONE":
            raise RuntimeError(f"Invalid Key: {strategy['key']}")

    def process(self):
        key     = self.data["key"]
        items   = self.data["items"]
        select  = self.data["select"]
        reverse = self.strategy["reverse"]

        l = EXPRESSIONS[key]

        sorted = heapq.nsmallest(len(items), items, key=l)
        if reverse: self.data["selected"] = [ s["addr"] for s in [ w for w in reversed(sorted[(-1 * select):]) ] ]
        else:       self.data["selected"] = [ s["addr"] for s in sorted[:select] ]

        for i in range(len(self.data["items"])):
            self.data["items"][i] = sorted[i]
