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

    def cFAQ(self, RTT:np.ndarray,  k=15, thresh=0.1, max_i=10000) -> List:
        # RTT = self.OWD * self.LOAD
        
        # Ensure the matrix is positive semi-definite
        PSD_RTT = RTT - np.min(np.linalg.eigvals(RTT)) * np.eye(len(RTT))

        # Define the boolean optimization variable
        V = cp.Variable(len(RTT), boolean=True)

        objective   = cp.Minimize(cp.quad_form(V, PSD_RTT))
        constraints = [ cp.sum(V) == k ]
        problem     = cp.Problem(objective, constraints)

        problem.solve(solver=cp.GUROBI, verbose=True, max_iters=max_i)
        self.L.log(problem.status)

        if problem.status in ["infeasible", "unbounded"]:
            print("NOT SOLVED OPTIMALLY")

        solution = V.value
        solution = [i for i,v in enumerate(solution) if v > thresh]

        self.L.log(str(solution))
        return solution

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

        if OWD.shape != (self.N, self.N):
            raise RuntimeError(f"OWD SHAPE: {OWD.shape}")

        if LOAD.shape != (self.N, self.N):
            raise RuntimeError(f"LOAD SHAPE: {LOAD.shape}")

        self.L.debug(message=f"OWD[{OWD.shape}]: \n{self.to_string(OWD)}")
        self.L.debug(message=f"LOAD[{LOAD.shape}]:\n{self.to_string(LOAD)}")

        while s == 0:
            self.L.debug(message=f"I: {i}")
            self.L.debug(message=f"P[{P.shape}]:\n{self.to_string(P)}")

            # GRADIENT WITH RESPECT TO CURRENT SOLUTION
            # ∇f(P(i)) = - Λ P(i) Δ_T - Λ_T P(i) Δ
            grad = - ( (LOAD @ P @ OWD.T) + (LOAD.T @ P @ OWD) )
            self.L.debug(message=f"Gradient[{grad.shape}]:\n{self.to_string(grad)}")

            # DIRECTION WHICH MINIMIZES 1ST ORDER APPROX OF f(P)
            # Q(i) = argmin_{P ∈ D} trace(∇f(P(i))_T P)
            Q = cp.Variable(grad.shape)
            objective = cp.Minimize(cp.trace(grad.T @ Q))
            constraints = [
                Q >= 0,                  # All entries of Q should be non-negative
                cp.sum(Q, axis=0) == 1,  # Each column should sum to 1
                cp.sum(Q, axis=1) == 1   # Each row should sum to 1
            ]

            problem = cp.Problem(objective, constraints)
            problem.solve(solver=cp.GUROBI)

            Q = Q.value
            self.L.debug(message=f"Q[{Q.shape}]:\n{self.to_string(Q)}")

            # BEST STEP SIZE IN CHOSEN DIRECTION
            # α(i) = min_{α ∈ [0,1]} f(P(i) + α * Q(i))
            #                        f(P(i)) = trace(Λ * P * Δ_T * P_T)
            alpha     = cp.Variable()
            PV = cp.vec(P)
            QV = cp.vec(Q)
            K  = cp.kron(LOAD @ OWD.T, np.eye(self.N))
            K  = (K + K.T) / 2

            T1 = cp.quad_form(PV, K)
            T2 = 2 * alpha * cp.sum(cp.multiply(cp.quad_form(QV, K), PV))
            T3 =  alpha**2 * cp.quad_form(QV, K)

            objective = cp.Minimize(T1 + T2 + T3)
            constraints = [
                    alpha >= 0, 
                    alpha <= 1,
            ]
            problem     = cp.Problem(objective, constraints)
            problem.solve(solver=cp.GUROBI, verbose=True)

            alpha     = alpha.value
            self.L.debug(message=f"ALPHA: {alpha}")

            # UPDATE OUR CURRENT SOLUTION
            # P(i+1) = P(i) + alpha * Q(i)
            P_NEXT  = P + alpha * Q

            # STOPPING CONDITIONS
            if np.linalg.norm(P_NEXT - P, ord='fro') < epsilon or i >= max_i:
                s = 1

            P = P_NEXT
            i += 1

        # PROJECTION OF P ONTO P[FINAL]
        # P(FINAL) = argmin_{P ∈ P} || P(i-1)P_T ||_F
        P_FINAL = np.zeros_like(P)
        for i in range(len(P)): 
            P_FINAL[i, np.argmax(P[i])] = 1

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

    def _directionH(self, grad, P):
        Q = np.zeros_like(grad)
        largest = np.argmax(grad, axis=1)
        for i in range(grad.shape[0]):
            Q[i, largest[i]] = 1
        return Q

    def _step(self, P, Q):
        """
        - We must have a positive-semi-definite matrix within the cp.trace() 
          function. A PSD matrix has:
            + Eigenvalues: All eigenvalues are non-negative.
            + Trace (sum of diagonal elements) is non-negative.

          This is needed because:
            + Convexity of Trace: 
                * The trace function is linear, and therefore convex. 
                  However, to guarantee the convexity of the overall 
                  objective function, the matrix argument of the trace 
                  must be positive semidefinite.
            + Quadratic Form: 
                * The expression within cp.trace(...) represents a 
                  quadratic form. The trace of a quadratic form is convex 
                  if and only if the matrix defining the quadratic form 
                  is positive semidefinite.
            + Convex Optimization: 
                * The FAQ algorithm relies on convex optimization techniques 
                  to find efficient solutions. Ensuring the convexity of the 
                  objective function is crucial for the reliability and convergence 
                  of the solver.

         CONDITIONS:
        - LOAD is reasonable to assume it's a non-negative matrix
        - OWD is generally symmetric and positive since OWD delay
          from VM i to VM j is usually similar to the delay from 
          VM j to VM i.
        - P and Q are doubly stochastic matrices: 
            + all rows and columns sum to 1 
            + all entries are non-negative
            + Doesn't gurantee overall product to be PSD, but 
              it helps maintain the non-negativity of the resulting matrix.
        """
        alpha   = cp.Variable()

        #          => ( Λ @ (P + alpha * Q) @ Δ ) @ (P + alpha * Q).T
        Z       = P + (alpha * Q)
        objective = cp.Minimize(cp.trace((self.LOAD @ Z @ self.OWD.T) @ Z.T))
        constraints = [
                alpha >= 0, 
                alpha <= 1,
        ]

        problem     = cp.Problem(objective, constraints)
        problem.solve(solver=cp.GUROBI)
        return alpha.value

    def _project(self, P):
        P_PROJECTED = np.zeros_like(P)
        for i in range(len(P)): P_PROJECTED[i, np.argmax(P[i])] = 1
        return P_PROJECTED
