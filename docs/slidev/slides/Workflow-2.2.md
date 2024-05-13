---
layout: two-cols-header
---

# Manager x Worker: Workflow [i = 2.2]

- <span style="color:#0070C0;font-style:bold;">ACTION: ROOT</span>

1. Manager: Tells root to be _Parent_
2. Parent: 
    1. Creates required Parent Job 
    2. Contacts Children, Get Child Job Structs
    3. Creates/Appends Reports
    4. Execs and Replies with Parent Job
3. Creates/Appends Report

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
        C["RPRT"]
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
        B["JP: ./parent [args]"] 
    end

    JC("<font color=white>C_Jobs:"):1
    block:citems
        columns 1
        C["JC: ./child [args]"] 
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
        A["JP_ID => RP"] 
    end

    RP("<font color=black>P_Reports:")
    block:pitems
        columns 1
        B["JP_ID => RC"] 
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
            +data = [ Job ]
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

    M->>P: COMM=PARENT
    P->>C: COMM=CHILD
    C->>P: JOB[C]
    P->>M: JOB[P]
```
</div>

<TUMLogo variant="white" />
