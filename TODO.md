- [ ] Manager
    - [ ] Make Parent Jobs parallel on a layer-basis
    - [ ] Add variable deadline cut-off to jobs 
    - [ ] Add `ng-stress` to LemonDrop Job 
    - [ ] Is warmup necessary?
    - [ ] how many different worst trees are needed?
    - [ ] implement root selection mechanism

```
 - difference between 99% latency of worst leaf and 99% latency of best leaf
 - informs how much each leaf should hold data for
 - measure each machine, and look at stddev 
 - look at measurements first, before you create/include them in a heuristic
```

- implement warm up
- look at stats, from there see a good time frame for parent jobs 
- make lemondrop find multiple trees, see if root is always chosen 
- 30 seconds for evaluation period
- make a better heuristic expression
- compare
