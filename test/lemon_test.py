import pytest
import numpy as np

from manager import *

L = Logger()

class TestLemonDropClass:
    def tostring(self, matrix:np.ndarray):
        ret = "\n".join(str(row) for row in matrix)
        return f"{ret}"

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

        OWD = np.array([
            [  0.0, 12.5, 28.1, 15.3,  9.8, 11.6, 14.2, 25.9, 13.7, 10.5],
            [ 12.5,  0.0, 22.4, 11.0, 13.2, 17.8, 10.1, 20.3, 14.9, 15.6],
            [ 28.1, 22.4,  0.0, 23.6, 18.3, 24.5, 21.7, 16.2, 19.0, 27.5],
            [ 15.3, 11.0, 23.6,  0.0, 14.1, 19.9, 12.8, 18.7, 16.5, 18.4],
            [  9.8, 13.2, 18.3, 14.1,  0.0, 10.9, 13.0, 21.8, 12.6,  9.2],
            [ 11.6, 17.8, 24.5, 19.9, 10.9,  0.0, 18.6, 27.3, 17.4, 11.1],
            [ 14.2, 10.1, 21.7, 12.8, 13.0, 18.6,  0.0, 19.5, 15.7, 16.3],
            [ 25.9, 20.3, 16.2, 18.7, 21.8, 27.3, 19.5,  0.0, 22.1, 26.4],
            [ 13.7, 14.9, 19.0, 16.5, 12.6, 17.4, 15.7, 22.1,  0.0, 14.8],
            [ 10.5, 15.6, 27.5, 18.4,  9.2, 11.1, 16.3, 26.4, 14.8,  0.0],
        ])

        LOAD = np.array([
            [0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        ])

        LD = LemonDrop(OWD=OWD.tolist(), VMS=workers, K=K, D=D, F=F)

        assert LOAD.all() == LD.LOAD.all()

        # mapping, converged, elapsed = LD.solve()

        max_arr = [ 
           1000,
           10000,
           10000,
           10000,
           10000,
           10000,
           10000,
           10000,
           10000,
           10000
        ]

        e_arr = [
            1.0e-4,
            7.7e-5,
            6.0e-5,
            4.6e-5,
            3.6e-5,
            2.8e-5,
            2.2e-5,
            1.7e-5,
            1.3e-5,
            1.0e-5
        ]

        for epsilon, max_i in zip(e_arr, max_arr):
            mapping = []
            # epsilon = 0.45e-4
            # max_i   = 100000

            P, converged, elapsed = LD.FAQ(OWD, LOAD, epsilon, max_i)

            for i in range(LD.K):
                idx = np.argmax(P[i])
                value = LD.VMS[idx]
                mapping.append((idx, value))

            L.log(f"LEMONDROP TOOK {elapsed} SECONDS: [EPS={epsilon} MAX={max_i} CONVERGED={converged}]")
            for i in range(K):
                idx, addr = mapping[i]
                # L.log(f"NODE_{i} => VM[{idx}]: {addr}")

            assert np.all(np.sum(P, axis=0) == 1)
            assert np.all(np.sum(P, axis=1) == 1)
            assert np.all((P == 0) | (P == 1))
