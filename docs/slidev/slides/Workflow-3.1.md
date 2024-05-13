---
layout: two-cols-header
---

# Manager x Worker: Workflow [Step_i = 3.1]

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
        W1["<font color=white>W<sub>1</sub>"]
        W2["<font color=white>W<sub>2</sub>"]
        W3["<font color=white>W<sub>3</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>5</sub>"]
        W6["W<sub>6</sub>"]
        style P fill:#0070C0
        style W2 fill:#FF0000
        style W1 fill:#0070C0
        style W3 fill:#0070C0
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
        A["<del>JP  </del>"] 
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
    alt="ManagerxWorker"
    style="transform: scale(1.1)"
    class="absolute bottom-13% right-16%"
>
```mermaid
graph LR 
    M[<font color=white>Manager]
    style M fill:#FF0000
    subgraph Tree
        direction TB
        W0["<font color=white>W<sub>2</sub>"]
        W1["<font color=white>W<sub>1</sub>"]
        W2["<font color=white>W<sub>3</sub>"]
        W3["<font color=black>W<sub>3</sub>"]
        W4["<font color=black>W<sub>4</sub>"]
        W5["<font color=black>W<sub>5</sub>"]
        W6["<font color=black>W<sub>6</sub>"]

        W0 -.- W1
        W0 -.- W2

        W1 -.- W3
        W1 -.- W4

        W2 -.- W5
        W2 -.- W6

        style W0 fill:#FF0000
        style W1 fill:#0070C0
        style W2 fill:#0070C0
        style W3 fill:#000000
        style W4 fill:#000000
        style W5 fill:#000000
        style W6 fill:#000000
    end
    M --> Tree
```

</diV>

<TUMLogo variant="white" />
