import pytest
import numpy as np

from manager import *

L = Logger()

class TestLemonDropClass:
    S = Seed()

    def test_a(self):
        workers = [ 
                   "10.1.1.1", 
                   "10.1.1.2", 
                   "10.1.1.3", 
                   "10.1.1.4", 
                   "10.1.1.5", 
                   "10.1.1.6", 
                   "10.1.1.7", 
                   "10.1.1.8", 
                   "10.1.1.9", 
                   "10.1.1.10", 
        ]

        N = 10 
        K = 7 
        D = 2 
        F = 2

        OWD = np.random.uniform(low=0.1, high=10.0, size=(N, N))
        np.fill_diagonal(OWD, 0)
        OWD = OWD.tolist()

        LD = LemonDrop(N=N, K=K, D=D, F=F)

        for i in range(N):
            items = []
            for value in OWD[i] :
                item:ItemDict = {
                        "addr":     workers[i],
                        "p90":      0.0,
                        "p75":      0.0,
                        "p50":      value,
                        "p25":      0.0,
                        "stddev":   0.0,
                        "recv":     0,
                }
                items.append(item)

            LD.owdi(i, items)
            L.record(f"ROW: {i + 1}/{len(workers)}")

        narr, diff = LD.solve(workers)
        tree = Tree(name="LEMON", root=narr[0], fanout=F, depth=D, arr=narr[1:])

        L.log(f"LEMONDROP TOOK {diff} SECONDS")
        L.log(f"TREE: {tree}")

        assert len(narr)    == K
        assert tree.depth   == D
        assert tree.fanout  == F
        assert tree.root.id == narr[0]
