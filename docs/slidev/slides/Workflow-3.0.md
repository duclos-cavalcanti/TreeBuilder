---
layout: two-cols-header
---

# Manager x Worker: Workflow [Step_i = 3.0]

- <span style="color:#0070C0;font-style:bold;">ACTION: REPORT</span>

1. Pops next report
2. Sleeps until trigger timestamp
3. Asks Report on pending job to owner
    1. Parent has received reports on children 
    2. Parent has also finished its job
    3. Parent sends results

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
    style="transform: scale(0.9)"
    class="absolute top-13% left-60% right-0 bottom-0"
>

```mermaid
block-beta
    M("<font color=white>Manager")
    space
    P("<font color=white>Pool ")
    space
    block:workers
        columns 3
        W0["W<sub>0</sub>"] 
        W1["W<sub>1</sub>"]
        W2["<font color=white>W<sub>2</sub>"]
        W3["W<sub>3</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>5</sub>"]
        W6["W<sub>6</sub>"]
        style P fill:#0070C0
        style W2 fill:#FF0000
        style W0 fill:#00FF00
        style W1 fill:#00FF00
        style W3 fill:#00FF00
    end
    M-->P
    P-->workers

    style M fill:#FF0000
    style P fill:#0070C0
```
</div>

<div
    alt="JobQ"
    style="transform: scale(0.6)"
    class="absolute top-18% left-30% right--1% bottom-0"
>
```mermaid
block-beta
    J("<font color=white>Jobs")
    space
    block:items
        columns 1
        A["JP  "] 
        B["____"] 
        X["____"] 
    end

    space

    block:pitems
        columns 1
        C["<del>JP: ./parent [args]</del>"] 
        D["____"] 
        Y["____"] 
    end

    space
    block:citems
        columns 1
        E["<del>JC0: ./child [args]</del>"] 
        F["<del>JC1: ./child [args]</del>"] 
        G["<del>JC2: ./child [args]</del>"] 
    end

    J --> items
    A --> C
    C --> E

    style J fill:#000000
```
</div>

::left::

<div 
    alt="Message"
    style="transform: scale(0.8)"
    class="absolute left-10% bottom-15%"
>

```mermaid
classDiagram
    class Message{
            +id   = 1
            +ts   = 1715280981565948
            +type = REPORT
            +flag = PARENT
            +data = [ ]
    }

    class Message_ACK{
            +id   = 1
            +ts   = 1715280981565948
            +type = ACK
            +flag = NONE
            +data = [ Results ]
    }
```

</div>

::right::

<div
    alt="Seq"
    style="transform: scale(1.3)"
    class="absolute bottom-13% right-19%"
>

```mermaid
sequenceDiagram
    participant M as Manager
    participant P as P
    participant C0 as C0
    participant C1 as C1
    participant C2 as C2

    Note right of M: Sleep...
    C0->>P: JOB_END[C0]
    C1->>P: JOB_END[C1]
    C2->>P: JOB_END[C2]
    P->>P:  JOB_END[P]
    M->>P: COMM=REPORT
    P->>M: RESULTS
```
</div>

<TUMLogo variant="white" />