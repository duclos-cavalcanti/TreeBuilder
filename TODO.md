# TO-DO

- [X] warmup ,lemondrop no warmup, extra flag to binaries
- [X] lemondrop multiple roots attempt => see if root repeats itself
- [X] lemondrop with and without stress
- [X] worst tree for every best? R: No, only p90
- [ ] rebuild leaf mechanism
- [X] 30 second evaluation

## Heuristic

### Ideas:
- difference between 99% latency of worst leaf and 99% latency of best leaf
    - informs how much each leaf should hold data for
- measure each machine, and look at stddev 
- look at measurements first, before you create/include them in a heuristic

### Faster 
- [ ] parallel layers for parent x child jobs

### Bridging into LemonDrop
- [ ] make our medians closer
- [ ] leaf rebuild 
- [ ] sensory mechanism to perceive worsening performance in tree 
    - latency profile
- [ ] root selection mechanism: 
    - cloudy forecast: loopback is a metric of some sort
    - select based off of subset of pool before tree construction.
    - select based off of remaining pool and first proxy layer
