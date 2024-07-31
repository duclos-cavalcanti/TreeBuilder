# TO-DO

- [X] warmup ,lemondrop no warmup, extra flag to binaries
- [X] lemondrop multiple roots attempt => see if root repeats itself
- [X] lemondrop with and without stress
- [X] worst tree for every best? R: No, only p90
- [ ] new heuristic to capture stddev/variance across intervals
- [X] new sensing job, how do latency profiles look like?
- [ ] parallel layers for parent x child jobs
- [ ] root selection mechanism
- [X] 30 second evaluation

## Heuristic

### Root Selection 
1. Select based off of subset of pool before tree construction.
2. Select based off of remaining pool and first proxy layer

### Ideas:
```
 - difference between 99% latency of worst leaf and 99% latency of best leaf
 - informs how much each leaf should hold data for
 - measure each machine, and look at stddev 
 - look at measurements first, before you create/include them in a heuristic
```

