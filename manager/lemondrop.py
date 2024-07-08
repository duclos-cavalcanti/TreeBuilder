import time
import cvxpy as cp
import numpy as np

from typing import Tuple

from .types    import *

class LemonDrop():
    def __init__(self, N:int, K:int, D:int, F:int):
        self.K      = K
        self.N      = N
        self.OWD    = np.zeros((N, N), dtype=float)
        self.LOAD   = self.load(K, N, D, F)
        self.L      = Logger()

    def load(self, K:int, N:int, D:int, F:int) -> np.ndarray:
        mat  = np.zeros((K, K), dtype=float)
        pmat = np.zeros((N, N), dtype=float)
        row  = 0
        col  = 1
        for i in range(D):
            nodes = F ** i
            for _ in range(nodes):
                for _ in range(F):
                    mat[row, col] 
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
        self.check()

    def check(self):
        ret = np.all(np.diag(self.OWD) == 0.0)
        if ret: 
            return
        else:   
            for row in self.OWD: print(' '.join(map(str, row)))
            raise RuntimeError("OWD Matrix has non-zero diagonal")

    def solve(self, workers:List[str]) -> Tuple[List[str] , float]:
        self.L.debug(message=f"LEMONDROP PRE-SOLVE", data={"OWD": self.OWD.tolist(), "LOAD": self.LOAD.tolist()})
        start = time.time()
        P = self.FAQ()
        end   = time.time()
        M = self.mapping(P, workers)
        self.L.debug(message=f"LEMONDROP POST-SOLVE", data={"P": P.tolist(), "M": M,  "TIME": (end - start)})
        return M, (end - start)

    def mapping(self, P:np.ndarray, arr:List[str]) -> List[str]:
        ret = []

        if P.shape != (self.K, self.K):
            raise ValueError(f"P should be of shape ({self.K}, {self.K}) but is of shape {P.shape}")

        if len(arr) != self.N:
            raise ValueError(f"Workers should have length {self.N} but have length {len(arr)}")

        for i in range(self.K):
            idx = np.argmax(P[i])
            value = arr[idx]
            ret.append(value)

        return ret

    def cmapping(self, P:List, arr:List[str]) -> List[str]:
        ret = []
        for i in range(len(P)):
            idx = np.argmax(P[i])
            value = arr[idx]
            ret.append(value)

    def cFAQ(self,  k=15, thresh=0.1, max_i=10000) -> List:
        RTT = self.OWD * self.LOAD
        
        # Ensure the matrix is positive semi-definite
        PSD_RTT = RTT - np.min(np.linalg.eigvals(RTT)) * np.eye(len(RTT))

        # Define the boolean optimization variable
        V = cp.Variable(len(RTT), boolean=True)

        objective   = cp.Minimize(cp.quad_form(s_vec, PSD_RTT))
        constraints = [ cp.sum(V) == k ]
        problem     = cp.Problem(objective, constraints)

        problem.solve(solver=cp.GUROBI, verbose=True, max_iters=max_i)
        self.L.log(problem.status)

        if problem.status in ["infeasible", "unbounded"]:
            print("NOT SOLVED OPTIMALLY")

        solution = V.value
        # solution = [i for i,v in enumerate(solution) if v > thresh]
        solution = sorted(range(len(solution)), key=lambda i: solution[i], reverse=True)

        self.L.log(str(solution[:self.K]))
        return solution[:self.K]

    def FAQ(self, epsilon=1e-6, max_i=100) -> np.ndarray:
        # P(0) = 11T, P(0) is a doubly stochastic matrix of shape (K, N)
        P = np.ones((self.N, self.N)) / self.N

        i = 0 # iteration
        s = 0 # stopping condition

        # Λ = LOAD_MATRIX: self.LOAD
        # Δ = OWD_MATRIX:  self.OWD

        while s == 0:
            # GRADIENT WITH RESPECT TO CURRENT SOLUTION
            # ∇f(P(i)) = ΛP(i)T Δ + ΔP(i)T ΛT
            # grad = -(self.LOAD @ P @ self.OWD.T) - (self.LOAD.T @ P @ self.OWD)
            # grad = self.LOAD @ P @ self.OWD.T + self.OWD @ P @ self.LOAD.T
            grad = self.LOAD @ P @ self.OWD.T + self.OWD @ P @ self.LOAD.T

            # DIRECTION WHICH MINIMIZES 1ST ORDER APPROX OF f(P)
            # Q(i) = argmin_{P ∈ D} trace(∇f(P(i))^T P)
            Q       = self._direction(grad, P)

            # BEST STEP SIZE IN CHOSEN DIRECTION
            # α(i) = min_{α ∈ [0,1]} f(P(i) + αQ(i))
            alpha   = self._step(P, Q)

            # UPDATE OUR CURRENT SOLUTION
            # P(i+1) = P(i) + alpha * Q(i)
            P_NEXT  = P + alpha * (Q - P)

            # STOPPING CONDITIONS
            if np.linalg.norm(P_NEXT - P, ord='fro') < epsilon:
                s = 1

            if i >= max_i:
                s = 1
            
            P = P_NEXT
            i += 1

        # P(FINAL) = argmin_{P ∈ P} ||P(i-1)P^T||_F
        P_FINAL = self._project(P)

        return P_FINAL

    def _direction(self, grad, P):
        """
        Returns: Q

        Q is/represents a permutation matrix:
            - A permutation matrix is a square binary matrix 
              that has exactly one entry of 1 in each row and 
              each column, and 0s elsewhere.

            - The goal of Q is to provide an optimal reordering 
              of the elements in P to minimize the objective function.

            - This is done effectively by measuring the alignment 
              of P with the gradient via Q, since we want the best 
              direction Q that minimizes said alignment.
        """

        Q = cp.Variable(grad.shape)

        # First order approximation that minimizes the gradient descent
        objective = cp.Minimize(cp.trace(grad.T @ Q))

        # Doubly stochastic matrix
        constraints = [
            Q >= 0,                  # All entries of Q should be non-negative
            cp.sum(Q, axis=0) == 1,  # Each column should sum to 1
            cp.sum(Q, axis=1) == 1   # Each row should sum to 1
        ]

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.GUROBI)

        return Q.value

    def _step(self, P, Q):
        alpha = cp.Variable()
        P_NEXT = P + alpha * (Q - P)

        # objective = cp.Minimize(alpha)
        # objective = cp.Minimize(cp.trace(self.LOAD @ P_NEXT.T @ self.OWD.T))
        objective = cp.Minimize(cp.trace(self.LOAD @ P_NEXT.T @ self.OWD.T @ P_NEXT))

        constraints = [
                alpha >= 0, 
                alpha <= 1
                # cp.trace(self.LOAD @ P_NEXT.T @ self.OWD.T @ P_NEXT) <= cp.trace(self.LOAD @ P.T @ self.OWD.T @ P)
        ]

        problem     = cp.Problem(objective, constraints)
        problem.solve(solver=cp.GUROBI)

        return alpha.value

    def _project(self, P):
        P_PROJECTED = np.zeros_like(P)
        for i in range(len(P)): P_PROJECTED[i, np.argmax(P[i])] = 1
        return P_PROJECTED
