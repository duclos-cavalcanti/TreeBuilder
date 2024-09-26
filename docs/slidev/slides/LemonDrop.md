---
layout: two-cols-header
---

# State-of-the-Art: LemonDrop

- Method of Selecting/Scheduling VMs on a cluster
- NP-Hard

<img 
    alt="Heuristic"
    style="transform: translate(-50%, -50%) scale(0.7)"
    src="/images/FAQ.png"
    class="absolute top-60% left-50%"
/>

<TUMLogo variant="white" />

<!-- --- -->
<!-- layout: two-cols-header -->
<!-- --- -->
<!---->
<!-- # State-of-the-Art: LemonDrop -->
<!-- - Λ = LOAD_MATRIX: LOAD -->
<!-- - Δ = OWD_MATRIX:  OWD -->
<!-- - Min(trace(Λ * P * Δ_T * P_T )) -->
<!---->
<!-- <div  -->
<!--     alt="sequenceDiagram" -->
<!--     style="transform: scale(0.8)" -->
<!--     class="absolute top-5% left-30%" -->
<!-- > -->
<!---->
<!-- ```py  -->
<!-- # i=0, s=0, P(0) = 11T, a doubly stochastic matrix, i: iteration, s: stopping condition -->
<!-- P = np.ones((self.N, self.N)) / self.N -->
<!-- while s == 0: -->
<!--     # ∇f(P(i)) = - Λ P(i) Δ_T - Λ_T P(i) Δ -->
<!--     grad = - (LOAD @ P @ OWD.T) - (LOAD.T @ P @ OWD) -->
<!--     # Q(i) = argmin_{P ∈ D} trace(∇f(P(i))_T P) , Hungarian Algorithm / LAP -->
<!--     Q = np.zeros((self.N, self.N)) -->
<!--     row, col = optimize.linear_sum_assignment(-grad) -->
<!--     Q[row, col] = 1 -->
<!--     # BEST STEP SIZE IN CHOSEN DIRECTION: α(i) = min_{α ∈ [0,1]} f(P(i) + α * Q(i)) -->
<!--     result = optimize.minimize_scalar( -->
<!--                 lambda alpha: np.trace(LOAD @ (P + alpha * Q) @ OWD.T @ (P + alpha * Q).T),  -->
<!--                 bounds=(0, 1),  -->
<!--                 method='bounded' -->
<!--     ) -->
<!--     alpha = result.x -->
<!--     # UPDATE OUR CURRENT SOLUTION: P(i+1) = P(i) + alpha * Q(i) -->
<!--     P_NEXT  = P + (alpha * Q) -->
<!--     # STOPPING CONDITIONS -->
<!--     if np.linalg.norm(P_NEXT - P, ord='fro') < epsilon: -->
<!--         converged = True -->
<!--         s = 1 -->
<!--     if i >= max_i: -->
<!--         s = 1 -->
<!--     P = P_NEXT -->
<!--     i += 1 -->
<!-- # PROJECTION OF P ONTO P[FINAL]: # P(FINAL) = argmin_{P ∈ P} || P(i-1)P_T ||_F -->
<!-- P_FINAL = np.zeros((self.N, self.N)) -->
<!-- row, col = optimize.linear_sum_assignment(-P)  -->
<!-- P_FINAL[row, col] = 1 -->
<!-- return P_FINAL, converged, (time.time() - start) -->
<!-- ``` -->
<!-- </div> -->

<TUMLogo variant="white" />
