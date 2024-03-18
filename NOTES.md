# Notes

Assumptions: 

- Lemons are lemons relative to other nodes / positioning in the cloud
- Cloud display high latency variance and inconsistent VM behaviour 
    - QAP Solver to find approximate best solution does not translate well to reality.

### 0. [CloudEx](https://www.sigops.org/s/conferences/hotos/2021/papers/hotos21-s06-ghalayini.pdf)

### 1. [Jasper](https://arxiv.org/abs/2402.09527)

__Jasper__ was made to be a scalable and fair multicast prototype for financial exchanges in the cloud. In the context of High-Frequency Trading (HFT), data regarding the market state has to be disseminated to a large number of market agents at extremely low latencies, as well as done so in an acceptably fair manner. That means, all market agents should be able to perceive an equal market state within any given moment, as well as be notified of changes to said state simultaneously. This ensures a fair and balanced playing field among participants.

There is interest both in academia and in the industry to move the current financial exchange infrastructure to the public cloud. The benefits are clear and among others include better scalability, a more robust infrastructure, flexible resource allocation and potential cost savings. However, a major and understandable concern is the feasibility to implement a fair multicast service for a large number of market participants within acceptable latencies. The public cloud does not currently offer such a service or hardware that supports _multicasting_ for cloud tenants.

Jasper, in a quick summary, employs a tree-like structure of VMS in the cloud, combined with DPDK kernel bypassing and shallow copies of packets to illustrate a competitive prototype of _multicasting_ on the cloud up to 1000 and even 5000 recipients.

### 2. [LemonDrop](https://searchworks.stanford.edu/view/14423035)
A method for selecting/scheduling VM's within a given cloud cluster optimized for an application's latency needs.

#### 1. Assumptions
- VM's within a given class instance are not equally strong.
- VM's are NOT interchangeable.

#### 2. Core
1. An accurate clock-synchronization algorithm. [[Hyugens]](https://www.usenix.org/system/files/conference/nsdi18/nsdi18-geng.pdf)

This algorithm uncovers fine-grained anomalies in one-way delays (OWD) between VM-pairs. Clock synchronization is a crucial 
and integral part of latency measurement among distributed systems.

2. An Algorithm that best selects/schedules the best `K` out of `N` VMs.

Together with the inter-VM OWD measurements and the supplied application's communication pattern, LemonDrop 
formulates and solves a natural Quadratic Assignment Problem (QAP) to perform it's selection and scheduling of 
VM's.

The QAP was originally proposed in 1957 and considers a setting where there are `N` Facilities, `N` Locations and one
objective: 

- Assign _facilities_ to _locations_, such that traffic flow between facilities is __minimized__.

LemonDrop reframes said problem in a way that (a) services within an application are treated as 
_facilities_ and (b) the VMs themselves are the _locations_. When LemonDrop __approximately__ solves 
the framed QAP, it becomes clear that indeed VMs of the same type are not equally strong and optimally 
deploying a service on a better pool of VMs can drastically improve performance of a given application.

LemonDrop has two aims (1) VM Selection and (2) VM Scheduling. Both of these steps are done 
simultaneously  as a part of the solution of the framed QAP. The needed inputs are: 

i) __The OWD Matrix__:
Given `N` VMs, all-to-all probe mesh is run to obtain one-way delays among the set. Each pair 
of VMs exchange 44-byte UDP packets.

ii) __The Application Load-Matrix__: The Load-Matrix captures the normalized number of requests
made by application node `k` to application node `l` per unit time. This can be obtained through:
+ Kubernetes, delivered through tools such as Jaeger and Zipkin or
+ Google Logging (glog)

The Load-Matrix can be obtained offline and can therefore impose no additional overhead during run-time. LemonDrop 
can also work without this input, however with it there are significant enhancements to it's effectiveness.

- Scheduling
    + Considering `N` equal to `L`, meaning for every application node, there is one suitable VM.
    + Hadamard Product of the Matrices (OWD and Load) from `i,j` to `L` captures the total distance traveled by the requests of the application per unit-time.
    + If service node i was assigned to VM i. It reflects the “in-network time” of the requests for this assignment of service nodes to VMs.
    + The VM scheduling problem aims to minimize this “in-network time” by finding the best 1-1 assignment of service nodes onto the VMs.
    + Minimize "in-network" time of permutation to solve scheduling.

- Optimization 
    + QAP is known to be NP-Hard
    + [FAQ](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0121002) Algorithm used to obtain locally optimal solution.
        - O(n^3)
        - Outperforms 94% of evaluations in QAPLIB
- Selection
    + Extension of the scheduling formulation.
    + Now, there are  N > L VMs from which we must choose the best L VMs and then assign service nodes to these VMs.
    + Determine OWD Matrix NxN as usual.
    + Pad Load Matrix.
    + Proceed with QAP Formulation. 
    + Utilize cost function trace. 
    + The VMs associated with the first L rows of the optimal assignment P ⇤ are our selected VMs.

#### 3. Conclusions
- Detects a _Lemon_ VM within a couple of minutes.
- Shown to significantly reduce median and tail latencies in benchmark applications.
- Offering improvements in performance and fairness.


## Meeting

### Topics
- [ ] Kickoff Presentation
    - [ ] Length 5 Minutes?
    - [ ] How much time into Background/Jasper/Financial Exchanges?
    - [ ] How specific or robust should be initial Heuristic Proposal'?
    - [ ] Date Slides are to available before Kickoff (1 Week?)
- [ ] Dry-Run Kickoff

### Questions
- [X] Jasper Latency: 100s of microseconds 
- [X] Clockworks Sync: 
    - Daemon Software 
    - Error is in 10s of nanoseconds 

### Study
- [ ] VM Co-Location? Is it a necessary variable for Jasper?
- [ ] "In-Network-Time"? What is the Hadamard Product of the Matrices expressing?
- [ ] Understand 3.2.1 Entirely: QAP Framing and Solving
    - [ ] Hadamard Product, Trace, Permutation P


