# TO-DO

- [X] warmup: lemondrop no warmup, extra flag to binaries
- [X] lemondrop multiple roots attempt => see if root repeats itself
- [X] lemondrop with and without stress
- [X] worst tree for every best? R: No, only p90
- [X] rebuild leaf mechanism
- [X] 30 second evaluation

## Thesis 
- [ ] State of the Art in Background?
- [ ] Title too long of Jasper? 
- [ ] Title too long of MA? 
- [ ] How should supervisors be shown?
- [ ] 60 Pages considering Bibliography, Appendix, etc ?
- [ ] Abbreviations should be linked/referenced?
- [ ] List of Figures?
- [ ] Table of Contents: Appendix name document isn't shown


## Heuristic

### Ideas:
- difference between 99% latency of worst leaf and 99% latency of best leaf
    - informs how much each leaf should hold data for
- measure each machine, and look at stddev 
- look at measurements first, before you create/include them in a heuristic

### Faster 
- [ ] parallel layers for parent x child jobs

### Bridging into LemonDrop
- [ ] make our medians closer!
- [ ] Heuristic Expression: 
    - take into account median? 
    - take into account positive standard deviation only?
- [X] rebuild leaf mechanism
- [ ] sensory mechanism to perceive worsening performance in tree 
    - latency profile?
- [ ] root selection mechanism: 
    - cloudy forecast: loop-back is a metric of some sort
    - select based off of subset of pool before tree construction.
    - select based off of remaining pool and first proxy layer


- BUILD PARALLELISM 
- DO LEMONDROP ONLY EXPERIMENT


- prefix: 
- GCP_100R_5K_H2_1710441710691032
- GCP_100R_5K_H2_1710540104743877

- run a couple of times the rand thing
