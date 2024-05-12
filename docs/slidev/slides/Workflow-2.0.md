---
layout: two-cols-header
---

# Manager x Worker: Workflow [i = 2]

- <span style="color:#0070C0;font-style:bold;">ACTION: ROOT</span>
1. Select root from pool <span style="color:#FF0000; font-style:italic;">( idx=2 )</span>
2. Commands root to be _Parent_
3. Creates/Pushes: `Step=REPORT`

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
>

```mermaid
classDiagram
    class Message{
            +id   = 1
            +ts   = 1715280981565948
            +type = COMMAND
            +flag = PARENT
            +data = [ rate, dur, w_addr_0, w_addr_1, w_addr_3 ]
    }
    %% style Message fill:#0070C0,color:#fff
```

</div>

<div 
    alt="Seq"
    style="transform: scale(0.8)"
    class="absolute left-13% bottom-5%"
>

```mermaid
graph LR
    M[<font color=white>Manager]
    W["W<sub>2</sub>"] 

    M --> W
    W --> M

    style M fill:#FF0000
```

</div>

::right::

```mermaid
graph LR 
    M[<font color=white>Manager]
    style M fill:#FF0000
    subgraph Worker_Pool
        direction TB
        W0["W<sub>0</sub>"] 
        W1["W<sub>1</sub>"]
        W2["<font color=white>W<sub>2</sub>"]
        W3["W<sub>3</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>5</sub>"]
        W6["W<sub>6</sub>"]

        style W2 fill:#FF0000

        W0 -.- W1
        W0 -.- W2

        W1 -.- W3
        W1 -.- W4

        W2 -.- W5
        W2 -.- W6

    end
    M --> Worker_Pool
```

<TUMLogo variant="white" />
