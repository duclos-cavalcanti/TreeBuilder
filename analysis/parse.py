import os
import json

from typing  import List
from manager import RunDict

class Parser():
    def __init__(self, dir:str, infra:str):
        self.map                = {}
        self.runs:List[RunDict] = self.read(dir)
        self.schema             = self.load(dir, infra)

        assert(len(self.runs) == len(self.schema["runs"]))

    def read(self, dir:str):
        file = os.path.join(dir, "events.log")
        events = []
        with open(file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    events.append(event)

                except json.JSONDecodeError as e:
                    print(f"Error parsing line: {line.strip()} - {e}")

        runs:List[RunDict]   = []
        for e in events:
            if "RUN" in e:
                runs.append(e["RUN"])

        return runs

    def load(self, dir:str, infra:str):
        f = "docker.json" if infra == "docker" else "default.json"
        file   = os.path.join(dir, f)

        with open(file, 'r') as f: 
            schema = json.load(f)

        self.map[schema["addrs"][0]] = "M_0"
        for i,addr in enumerate(schema["addrs"][1:]):
            name = f"W_{i}"
            self.map[addr] = name

        return schema
