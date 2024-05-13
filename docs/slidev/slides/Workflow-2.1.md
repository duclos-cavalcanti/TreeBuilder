---
layout: two-cols-header
---

# Manager x Worker: Workflow [Step_i = 2.1]

- <span style="color:#0070C0;font-style:bold;">ACTION: ROOT</span>
1. Select root from pool <span style="color:#FF0000; font-style:italic;">( idx=2 )</span>
2. Commands Root/Parent: `./parent <args`
    1. Commands children: `./child <args`
    2. Store their Jobs `JC`
    3. Starts Job `JP` and returns it via ACK
3. Pushes: `Step=REPORT` and stores `JP`

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
        C["JP: ./parent [args]"] 
        D["____"] 
        Y["____"] 
    end

    space
    block:citems
        columns 1
        E["JC0: ./child [args]"] 
        F["JC1: ./child [args]"] 
        G["JC2: ./child [args]"] 
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
    style="transform: scale(1.0)"
    class="absolute left-9% bottom-22%"
>

```mermaid
classDiagram
    class Message_P{
            +id   = 1
            +ts   = 1715280981565948
            +type = COMMAND
            +flag = PARENT
            +data = [ rate, dur, w_addr_0, w_addr_1, w_addr_3 ]
    }

    class Message_C{
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
    alt="Message_ACK"
    style="transform: scale(0.6)"
    class="absolute left-12% bottom-0%"
>

```mermaid
classDiagram
    class Message_P_ACK{
            +id   = 1
            +ts   = 1715280981565948
            +type = ACK
            +flag = NONE
            +data = [ JP ]
    }

    class Message_C_ACK{
            +id   = 1
            +ts   = 1715280981565948
            +type = ACK
            +flag = NONE
            +data = [ JC ]
    }
    %% style Message fill:#0070C0,color:#fff
```

</div>

::right::

<div 
    alt="ManagerxWorker"
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

    M->>P: COMM=PARENT
    P->>C0: COMM=CHILD
    C0->>P: JOB[C]
    P->>C1: COMM=CHILD
    C1->>P: JOB[C]
    P->>C2: COMM=CHILD
    C2->>P: JOB[C]
    P->>M: JOB[P]
```

</diV>

<TUMLogo variant="white" />
