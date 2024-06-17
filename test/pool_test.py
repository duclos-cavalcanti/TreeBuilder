import pytest

from manager import *

L = Logger()

class TestPoolClass:
    S = Seed()

    def test_a(self):
        P1 = self.build(size=10)
        P2 = self.build(size=10)
        for _ in range(100):
            S1 = P1.slice()
            S2 = P2.slice()
            L.log(f"P1[{P1.seed}] SELECTED: {S1}")
            L.log(f"P2[{P2.seed}] SELECTED: {S2}")
            assert S1 == S2

    def build(self, size:int, k:int=4):
        P = Pool([ f"n_{i}" for i in range(size) ] , k, self.S.get())

        return P
