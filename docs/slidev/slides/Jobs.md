---
layout: two-cols-header
---

# Tree-Finder: Jobs/Tasks

- Nodes send/recv Messages
- Manager deploys Jobs { Parent, Mcast, Lemon }
- Data-Structures describe: 
    - Node's Command 
    - Node's Tree Position
- Manager aggregates results

<!-- <div  -->
<!--     alt="sequenceDiagram" -->
<!--     style="transform: translate(-50%, -50%) scale(1.2)" -->
<!--     class="absolute top-75% left-50%" -->
<!-- > -->

<div 
    alt="sequenceDiagram"
    style="transform: scale(1.2)"
    class="absolute top-20% right-10%"
>

```mermaid
sequenceDiagram
    participant M as Manager
    participant W1 as W1:ROOT
    participant W2 as W2:CHILD
    participant W3 as W3:CHILD

    M->>W1: COMMAND

    W1->>W2: COMMAND
    W1->>W3: COMMAND

    W1->>W2: PROBE
    W2->>W1: JOB/ACK

    W1->>W3: PROBE
    W3->>W1: JOB/ACK

    M->>W1: PROBE
    W1->>M: JOB/ACK
```
</div>


<div 
    alt="Classes"
    style="transform: scale(0.7)"
    class="absolute bottom--1% left-25%"
>

```mermaid
graph TB
    subgraph Tree [Parent D=1, F=2]
        direction TB
        W1["W<sub>1</sub>"]
        W2["W<sub>2</sub>"]
        W3["W<sub>3</sub>"]

        W1 --> W2
        W1 --> W3

        style W1 fill:#000000,color:#fff
    end
```

</div>

<div 
    alt="Classes"
    style="transform: scale(0.8)"
    class="absolute bottom-0% right-28%"
>

```mermaid
graph TB
    subgraph Tree [Mcast D=2, F=2]
        direction TB
        W1["W<sub>1</sub>"]
        W2["W<sub>2</sub>"]
        W3["W<sub>3</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>5</sub>"]
        W6["W<sub>6</sub>"]
        W7["W<sub>7</sub>"]

        W1 --> W2
        W1 --> W3

        W2 --> W4
        W2 --> W5

        W3 --> W6
        W3 --> W7

        style W1 fill:#000000,color:#fff
    end
```

</div>

<div 
    alt="Classes"
    style="transform: scale(0.7)"
    class="absolute bottom-0% right-6%"
>

```mermaid
graph TB
    W1["W<sub>1</sub>"]
    W2["W<sub>2</sub>"]
    W3["W<sub>3</sub>"]

    subgraph Tree [Lemon N=3]
        direction LR
        W1 --> W2
        W1 --> W3
    end

    subgraph Tree [Lemon B]
        direction LR
        W2 --> W1
        W2 --> W3
    end

    subgraph Tree [Lemon B]
        direction LR
        W3 --> W1
        W3 --> W2
    end

    style W1 fill:#000000,color:#fff
    style W2 fill:#000000,color:#fff
    style W3 fill:#000000,color:#fff
```

</div>

<div 
    alt="Classes"
    style="transform: scale(0.7)"
    class="absolute bottom--5% left-2%"
>

```mermaid
classDiagram
    class Command{
        string addr = "W1";
        int32  layer=1, fanout=2;
        int32  select=2, rate=10K, duration=10;
        string[] instr = [
            "./command_1", 
            "./command_2", 
            "./command_3" 
        ]
        string[] data = ["W2", "W3"];
    }

    style Command fill:#000000,color:#fff
```

</div>

<TUMLogo variant="white" />
