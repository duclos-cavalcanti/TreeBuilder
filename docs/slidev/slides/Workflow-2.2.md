---
layout: two-cols-header
---

# Manager x Worker: Workflow [i = 2.2]

- <span style="color:#0070C0;font-style:bold;">ACTION: ROOT</span>

1. Manager: Tells root to be _Parent_
2. Parent: 
    1. Creates required Parent Job 
    2. Contacts Children
    3. Append their Jobs as dependencies
    4. Execs and Replies with Parent Job
3. Manager: Starts Timer Job _(1.2 * duration)_

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
    class="absolute right-17% top-40%"
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

<div
    alt="NodeJobs"
    style="transform: scale(1.1)"
    class="absolute right-17% bottom-5%"
>

```mermaid
block-beta
    columns 3
    M("Manager"):1
    space
    MJ("J<sub>0</sub> = sleep(dur * 1.2)"):1

    M --> MJ

    P("Parent"):1
    space
    PJ("J<sub>0</sub> = ./parent [args] "):1

    P --> PJ

    C("Child"):1
    space
    CJ("J<sub>0</sub> = ./child [args] "):1

    C --> CJ

    style MJ fill:#000000;color:#FFFFFF
    style PJ fill:#000000;color:#FFFFFF
    style CJ fill:#000000;color:#FFFFFF
```

</div>

<TUMLogo variant="white" />
