from typing import List
from collections import OrderedDict

class DQueue():
    def __init__(self):
        self.D = OrderedDict()

    def push(self, key, value):
        self.D[key] = value

    def get(self, k):
        ret = self.D.get(k)
        if ret is None:
            raise RuntimeError()
        else: 
            return ret

    def pop(self):
        if not self.D: 
            return None, None
        else:
            key, value = self.D.popitem(last=False)
            return key, value

class SQueue():
    def __init__(self, arr:List=[]):
        self.Q = arr

    def peak(self):
        if len(self.Q) == 0: 
            return None
        return self.Q[0]

    def pop(self):
        if len(self.Q) == 0: 
            return None
        el = self.Q[0]
        self.Q.pop(0)
        return el

    def push(self, el) -> None:
        self.Q.append(el)

    def __str__(self):
        return self.Q.__str__()

