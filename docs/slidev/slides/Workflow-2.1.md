---
layout: two-cols-header
---

# Manager x Worker: Workflow [i = 2.1]

- <span style="color:#0070C0;font-style:bold;">ACTION: ROOT</span>
1. Connects to workers/children
2. Commands worker to be _Child_
    1. Starts Job: `./child <args`
3. Starts Job: `./parent <args`

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
            +flag = CHILD
            +data = [ child_addr_i, host_addr ]
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
    P[<font color=white>Parent]
    C["C<sub>i</sub>"] 

    P --> C
    C --> P

    style P fill:#FF0000
```

</div>

::right::

<div 
    alt="ManagerxWorker"
    style="transform: scale(1.1)"
    class="absolute top-35% right-16%"
>
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

        style W0 fill:#00FF00
        style W1 fill:#00FF00
        style W3 fill:#00FF00
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

</diV>

<div 
    alt="Parent_x_Children"
    style="transform: scale(0.8)"
    class="absolute top-65% right-13%"
>
```mermaid
graph LR
    subgraph Parent_x_Children
        direction TB
        P[<font color=white>P]
        style P fill:#FF0000

        C0["C<sub>0</sub>"] 
        C1["C<sub>1</sub>"]
        C3["C<sub>3</sub>"]

        style C0 fill:#00FF00
        style C1 fill:#00FF00
        style C3 fill:#00FF00

        P --> C0
        P --> C1
        P --> C3
    end
```
</diV>

<TUMLogo variant="white" />
