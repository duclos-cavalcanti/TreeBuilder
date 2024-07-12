import time
import numpy as np

from scipy import optimize
from typing import Tuple

from .types    import *

class LemonDrop():
    def __init__(self, N:int, K:int, D:int, F:int):
        self.K      = K
        self.N      = N
        self.OWD    = np.zeros((N, N), dtype=float)
        self.LOAD   = self.load(K, N, D, F)
        self.L      = Logger()

    def to_string(self, matrix:np.ndarray):
        ret = "\n".join(str(row) for row in matrix)
        return f"{ret}"

    def load(self, K:int, N:int, D:int, F:int) -> np.ndarray:
        mat  = np.zeros((K, K), dtype=float)
        pmat = np.zeros((N, N), dtype=float)
        row  = 0
        col  = 1
        for i in range(D):
            nodes = F ** i
            for _ in range(nodes):
                for _ in range(F):
                    mat[row, col] = 1
                    col += 1
                row += 1

        pmat[:mat.shape[0], :mat.shape[1]] = mat
        return pmat

    def owdi(self, i:int, arr:List[ItemDict]):
        values = []

        for a in arr:
            values.append(a["p50"])

        if len(values) != self.N:
            raise ValueError(f"Array length must be {self.N} / but is of length {len(values)}")

        self.OWD[i, :] = values

    def check(self, OWD, LOAD):
        if OWD.shape != (self.N, self.N):
            raise RuntimeError(f"OWD SHAPE: {OWD.shape}")

        if LOAD.shape != (self.N, self.N):
            raise RuntimeError(f"LOAD SHAPE: {LOAD.shape}")

        ret = np.all(np.diag(OWD) == 0.0)
        if not ret: 
            print(self.to_string(OWD))
            raise RuntimeError("OWD Matrix has non-zero diagonal")

        return

    def pre_solve(self):
        data = {
                "OWD":  self.OWD.tolist(),
                "LOAD": self.LOAD.tolist(),
        }
        self.L.debug(message=f"LEMONDROP PRE-SOLVE")
        self.L.debug(message=f"OWD: \n{self.to_string(self.OWD)}")
        self.L.debug(message=f"LOAD:\n{self.to_string(self.LOAD)}")

    def post_solve(self, P:np.ndarray, M:List, time:float):
        data = {
                "P":  P.tolist(),
                "M":  M,
                "TIME": time,
        }
        self.L.debug(message=f"LEMONDROP POST-SOLVE")
        self.L.debug(message=f"P: \n{self.to_string(P)}")
        self.L.debug(message=f"M: \n{M}")

    def solve(self, workers:List[str]) -> Tuple[List[str] , float]:
        self.check(self.OWD, self.LOAD)
        self.pre_solve()
        start = time.time()
        P = self.FAQ(self.OWD, self.LOAD)
        end   = time.time()
        M = self.mapping(P, workers)
        self.post_solve(P, M, (end - start))
        return M, (end - start)

    def mapping(self, P:np.ndarray, arr:List[str]) -> List[str]:
        ret = []

        if P.shape != (self.N, self.N):
            raise ValueError(f"P should be of shape ({self.N}, {self.N}) but is of shape {P.shape}")

        if len(arr) != self.N:
            raise ValueError(f"Workers should have length {self.N} but have length {len(arr)}")

        for i in range(self.K):
            idx = np.argmax(P[i])
            value = arr[idx]
            ret.append(value)

        return ret

    def FAQ(self, OWD:np.ndarray, LOAD:np.ndarray, epsilon=1e-6, max_i=100) -> np.ndarray:
        """
        1. Initialize P (doubly stochastic matrix).
        2. While a stopping condition isn't met:
            1. Calculate the gradient.
            2. Find the direction (Q) that minimizes the first-order approximation of the objective function.
            3. Determine the best step size (alpha) in the chosen direction.
            4. Update the current solution (P).
        3. Project the final solution (P).
        4. Return the final solution (P_FINAL).
        """
        # P(0) = 11T, a doubly stochastic matrix, i: iteration, s: stopping condition
        P = np.ones((self.N, self.N)) / self.N
        i = 0
        s = 0

        # Λ = LOAD_MATRIX: LOAD
        # Δ = OWD_MATRIX:  OWD
        # 
        # GOAL:
        # Minimize => trace(Λ * P * Δ_T * P_T ) (3.1)

        while s == 0:
            # GRADIENT WITH RESPECT TO CURRENT SOLUTION
            # ∇f(P(i)) = - Λ P(i) Δ_T - Λ_T P(i) Δ
            grad = - (LOAD @ P @ OWD.T) - (LOAD.T @ P @ OWD)

            # DIRECTION WHICH MINIMIZES 1ST ORDER APPROX OF f(P)
            # Q(i) = argmin_{P ∈ D} trace(∇f(P(i))_T P)
            # Hungarian Algorithm / LAP
            Q = np.zeros((self.N, self.N))
            row, col = optimize.linear_sum_assignment(-grad)
            Q[row, col] = 1

            # BEST STEP SIZE IN CHOSEN DIRECTION
            # α(i) = min_{α ∈ [0,1]} f(P(i) + α * Q(i))
            result = optimize.minimize_scalar(
                        lambda alpha: np.trace(LOAD @ (P + alpha * Q) @ OWD.T @ (P + alpha * Q).T), 
                        bounds=(0, 1), 
                        method='bounded'
            )
            alpha = result.x

            # UPDATE OUR CURRENT SOLUTION
            # P(i+1) = P(i) + alpha * Q(i)
            P_NEXT  = P + (alpha * Q)

            # STOPPING CONDITIONS
            if np.linalg.norm(P_NEXT - P, ord='fro') < epsilon or i >= max_i:
                s = 1

            P = P_NEXT
            i += 1

        # PROJECTION OF P ONTO P[FINAL]
        # P(FINAL) = argmin_{P ∈ P} || P(i-1)P_T ||_F
        # Hungarian Algorithm / LAP
        P_FINAL = np.zeros_like(P)
        row, col = optimize.linear_sum_assignment(-P) 
        P_FINAL[row, col] = 1
        return P_FINAL

