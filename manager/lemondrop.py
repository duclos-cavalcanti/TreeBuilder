import time
import cvxpy as cp
import numpy as np

class LemonDrop():
    def __init__(self):
        pass
 
def solve_miqp_min(rtt_mat, k=15, thresh=.1):
    
    start = time.time()
    psd_rtt_mat = rtt_mat - min(np.linalg.eigvals(rtt_mat))* np.eye(len(rtt_mat))
    s_vec = cp.Variable(len(rtt_mat), boolean=True)

    # Compute average of n^2 edges in matrix formed by graph of n vertices.
    objective = cp.Minimize(cp.quad_form(s_vec, psd_rtt_mat ))
    constraints = [ sum(s_vec) == k ] # Get k elements from n
    
    prob = cp.Problem(objective, constraints)
    status = prob.solve(solver=cp.GUROBI, TimeLimit=10)  # solve using gurobi solver
    print(status)  # print the human-readable status
    if prob.status in ["infeasible", "unbounded"]:
        print("NOT SOLVED OPTIMALLY")
    
    sol = s_vec.value
    qp_idx_min = [i for i,v in enumerate(sol) if v > thresh]
    end = time.time()
    
    elapsed_time = end - start
    
    return qp_idx_min, elapsed_time, prob.status
