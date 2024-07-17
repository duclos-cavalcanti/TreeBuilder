import time
import numpy as np

from scipy import optimize
from typing import Tuple

from .types    import *

class LemonDrop():
    def __init__(self, OWD:List[List[float]], VMS:List[str], K:int, D:int, F:int):
        self.VMS    = [ v for v in VMS ]
        self.K      = K
        self.N      = len(VMS)
        self.OWD    = self.owd(OWD)
        self.LOAD   = self.load(D, F)
        self.L      = Logger()

    def load(self, D:int, F:int) -> np.ndarray:
        mat  = np.zeros((self.K, self.K), dtype=float)
        pmat = np.zeros((self.N, self.N), dtype=float)
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

    def owd(self, matrix:List[List[float]]):
        OWD = np.zeros((self.N, self.N), dtype=float)
        for i, row in enumerate(matrix):
            if len(row) != self.N: 
                raise RuntimeError(f"OWD ROW HAS LENGTH {len(row)} != {self.N}")
            OWD[i, :] = row
        return OWD

    def solve(self, epsilon=1e-4, max_i=1000) -> Tuple[List[Tuple[int, str]], np.ndarray, bool, float]:
        if self.OWD.shape != (self.N, self.N):
            raise RuntimeError(f"OWD SHAPE[{self.OWD.shape}] not ({self.N}, {self.N})")

        if not np.all(np.diag(self.OWD) == 0.0): 
            raise RuntimeError("OWD Matrix has non-zero diagonal")

        if self.LOAD.shape != (self.N, self.N):
            raise RuntimeError(f"LOAD SHAPE[{self.LOAD.shape}] not ({self.N}, {self.N})")

        data = {}
        OWD_DICT  = {}
        LOAD_DICT = {}

        for i, row in enumerate(self.OWD):
            data[f"OWD[{i}]"]  = row

        for i, row in enumerate(self.LOAD):
            data[f"LOAD[{i}]"]  = row

        self.L.debug(message=f"LEMONDROP PRE-SOLVE:", data=data)

        M = []
        P, converged, elapsed = self.FAQ(self.OWD, self.LOAD, epsilon, max_i)

        if P.shape != (self.N, self.N):
            raise RuntimeError(f"P SHAPE[{P.shape}] not ({self.N}, {self.N})")

        for i in range(self.K):
            idx = np.argmax(P[i])
            value = self.VMS[idx]
            M.append((idx, value))

        for i, row in enumerate(P):
            data[f"P[{i}]"]  = row

        for i, row in enumerate(M):
            data[f"M[{i}]"]  = row

        self.L.debug(message=f"LEMONDROP POST-SOLVE:", data=data)

        return M, P, converged, elapsed

    def FAQ(self, OWD:np.ndarray, LOAD:np.ndarray, epsilon=1e-4, max_i=1000) -> Tuple[np.ndarray, bool, float]:
        """
        1. Initialize P (doubly stochastic matrix).
        2. While a stopping condition isn't met:
            1. Calculate the gradient.
            2. Find the direction (Q) that minimizes the first-order approximation of the objective function.
            3. Determine the best step size (alpha) in the chosen direction.
            4. Update the current solution (P).
        3. Project the final solution (P).
        4. Return the final solution (P_FINAL).

        Conditions: 
            thresh/epsilon = 1e-6 | Examples: 0.1, 1e-3, 1e-6
            max_i = 100, 1000 or 10000

            ML: epsilon is chosen as 1e-5, 1e-6 and max_i as 100s or 1000s
            Structural Optimization: epsilon might be 1e-3 with a few hundred iters
        """
        # Λ = LOAD_MATRIX: LOAD
        # Δ = OWD_MATRIX:  OWD

        # GOAL:
        # Minimize => trace(Λ * P * Δ_T * P_T ) (3.1)
        start = time.time()

        # P(0) = 11T, a doubly stochastic matrix, i: iteration, s: stopping condition
        P = np.ones((self.N, self.N)) / self.N
        i = 0
        s = 0

        converged = False
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
            if np.linalg.norm(P_NEXT - P, ord='fro') < epsilon:
                converged = True
                s = 1

            if i >= max_i:
                s = 1

            P = P_NEXT
            i += 1

        # PROJECTION OF P ONTO P[FINAL]
        # P(FINAL) = argmin_{P ∈ P} || P(i-1)P_T ||_F
        # Hungarian Algorithm / LAP
        P_FINAL = np.zeros((self.N, self.N))
        row, col = optimize.linear_sum_assignment(-P) 
        P_FINAL[row, col] = 1
        return P_FINAL, converged, (time.time() - start)

    def cFAQ(self, OWD:np.ndarray, LOAD:np.ndarray) -> Tuple[List[int], bool, float]:
        """
        1. Initialize P (doubly stochastic matrix).
        2. While a stopping condition isn't met:
            1. Calculate the gradient.
            2. Find the direction (Q) that minimizes the first-order approximation of the objective function.
            3. Determine the best step size (alpha) in the chosen direction.
            4. Update the current solution (P).
        3. Project the final solution (P).
        4. Return the final solution (P_FINAL).

        Conditions: 
            epsilon = 1e-6
        """
        import cvxpy as cp

        # Λ = LOAD_MATRIX: LOAD
        # Δ = OWD_MATRIX:  OWD

        # GOAL:
        # Minimize => trace(Λ * P * Δ_T * P_T ) (3.1)
        start = time.time()
        thresh = .1

        RTT = LOAD @ OWD
        P   = RTT - min(np.linalg.eigvals(RTT))* np.eye(len(RTT))
        S   = cp.Variable(len(RTT), boolean=True)

        objective   = cp.Minimize(cp.quad_form(S, P))
        constraints = [sum(S) == self.K]
        problem     = cp.Problem(objective, constraints)
        converged   = False

        problem.solve(solver=cp.GUROBI, TimeLimit=10)
        if problem.status in ["infeasible", "unbounded"]:
            converged = True

        result = [i for i,v in enumerate(S.value) if v > thresh]
        return result, converged, (time.time() - start)

