import hashlib

from typing import List

class Job():
    def __init__(self, addr:str="", command:str="", arr:List=[], deps:List=[]):
        if len(arr) > 0:
            if len(arr) <= 6 : 
                raise RuntimeError(f"Arr has incorrect length: {arr}")
            self.from_arr(arr)
        else:
            self.id         = self.hash(f"{addr}{command}")
            self.pid        = 0
            self.addr       = addr
            self.command    = command
            self.end        = False
            self.ret        = -1
            self.out        = "NONE"
        self.deps = deps

    def __str__(self):
        output = [f"{{"]
        output.append(f"\tID={self.id}")
        output.append(f"\tPID={self.pid}")
        output.append(f"\tADDR={self.addr}")
        output.append(f"\tCOMM={self.command}")
        output.append(f"\tEND={self.end}")
        output.append(f"\tRET={self.ret}")
        output.append(f"\tOUT={self.out}")
        output.append(f"}}")
        return "\n".join(output)


    def hash(self, string:str) -> str: 
        bytes = string.encode('utf-8')
        hash = hashlib.sha256(bytes)
        return hash.hexdigest()

    def is_resolved(self) -> bool: 
        for d in self.deps:
            if d.end == False: 
                return False
        return True

    def to_arr(self) -> List:
        ret = []
        ret.append(f"{self.id}")
        ret.append(f"{self.pid}")
        ret.append(f"{self.addr}")
        ret.append(f"{self.command}")
        ret.append(f"{self.end}")
        ret.append(f"{self.ret}")
        ret.append(f"{self.out}")
        return ret

    def from_arr(self, arr:List):
        self.id         = arr[0]
        self.pid        = arr[1]
        self.addr       = arr[2]
        self.command    = arr[3]
        self.end        = True if arr[4] == "True" else False
        self.ret        = arr[5]
        self.out        = arr[6]
