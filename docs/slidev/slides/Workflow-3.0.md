---
layout: two-cols-header
---

# Manager x Worker: Workflow [i = 3.0]

- <span style="color:#0070C0;font-style:bold;">ACTION: REPORT</span>

1. Pops next report
2. Sleeps until trigger timestamp
3. Send pending job to owner (Report)
    1. Parent has received reports on children 
    2. Parent has also finished its job
    3. Parent sends back all job results


<div
    alt="StepQ"
    style="transform: scale(0.6)"
    class="absolute top--5 left-30% right-0 bottom-0"
>
```mermaid
block-beta
    Q("<font color=white>StepQ")
    space
    block:items
        columns 1
        A["<del>CONN</del>"] 
        B["<del>ROOT</del>"] 
        C["<del>RPRT</del>"] 
    end

    Q --> items

    style Q fill:#FF0000
```
</div>

<div
    alt="Pool"
    style="transform: scale(0.6)"
    class="absolute top--5 left-60% right-0 bottom-0"
>

```mermaid
block-beta
    P("<font color=white>Pool ")
    space
    block:workers
        columns 3
        W0["W<sub>0</sub>"] 
        W1["W<sub>1</sub>"]
        W2["<font color=black>W<sub>2</sub>"]
        W3["W<sub>3</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>5</sub>"]
        W6["W<sub>6</sub>"]
    end
    P-->workers
    style P fill:#0070C0
    style W2 fill:#000000
```
</div>

<div
    alt="JobQ"
    style="transform: scale(0.6)"
    class="absolute top-18% left-30% right--1% bottom-0"
>
```mermaid
block-beta
    columns 2
    JM("<font color=white>M_Jobs:"):1
    block:mitems
        columns 1
        A["____"] 
    end

    JP("<font color=white>P_Jobs:"):1
    block:pitems
        columns 1
        B["<del>JP: ./parent [args]</del>"] 
    end

    JC("<font color=white>C_Jobs:"):1
    block:citems
        columns 1
        C["<del>JC: ./child [args]</del>"] 
    end

    style JM fill:#000000
    style JP fill:#000000
    style JC fill:#000000
```
</div>

<div
    alt="RepQ"
    style="transform: scale(0.6)"
    class="absolute top-18% left-60% right--1% bottom-0"
>
```mermaid
block-beta
    columns 2
    RM("<font color=black>M_Reports:")
    block:mitems
        columns 1
        A["<del>JP_ID => RP</del>"] 
    end

    RP("<font color=black>P_Reports:")
    block:pitems
        columns 1
        B["<del>JP_ID => RC</del>"] 
    end

    RC("<font color=black>C_Reports:")
    block:citems
        columns 1
        C["___________"] 
    end

    style RM fill:#DAD7CB
    style RP fill:#DAD7CB
    style RC fill:#DAD7CB
```
</div>

::left::

<div 
    alt="Message"
    style="transform: scale(0.8)"
    class="absolute left-10% bottom-0%"
>

```mermaid
classDiagram
    class Message{
            +id   = 1
            +ts   = 1715280981565948
            +type = ACK
            +flag = NONE
            +data = [ Job_P, Job_C ]
    }
```

</div>

::right::

<div
    alt="Seq"
    style="transform: scale(1.2)"
    class="absolute right-20% bottom-5%"
>

```mermaid
sequenceDiagram
    participant M as Manager
    participant P as Parent
    participant C as Child

    Note right of M: Sleep...
    C->>P: JOB_END[C]
    P->>P: JOB_END[P]
    M->>P: COMM=REPORT
    P->>M: Job_END[P], JOB_END[C]
```
</div>

<TUMLogo variant="white" />
