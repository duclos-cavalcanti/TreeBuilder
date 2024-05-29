---
layout: default
---

# Summary

1. Establish connection to workers
2. Do for [ `best`, `worst`, `random`] trees:
    1. Choose `root`
    2. Until Tree is complete
        1. Start `parent x child` jobs
        2. Probe for results
        3. When done: modify `Tree` and `Pool` accordingly
    2. Store results

<div 
    alt="States"
    style="transform: scale(1.1)"
    class="absolute bottom-13% left-16%"
>
```mermaid
graph LR 
    C[<font color=white>CONN]
    R[<font color=white>ROOT]
    P[<font color=white>MCST]

    C --> R
    R --> R
    R --> P
    P --> R

    style C fill:#000000
    style R fill:#000000
    style P fill:#000000
```

</diV>

<div
    alt="Pool"
    style="transform: scale(0.8)"
    class="absolute top-13% left-50% right-0 bottom-0"
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
        W2["W<sub>2</sub>"]
        W3["W<sub>3</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>5</sub>"]
        W6["W<sub>6</sub>"]
        W7["W<sub>7</sub>"]
    end
    M-->P
    P-->workers

    style M fill:#FF0000
    style P fill:#0070C0
```
</div>

<div
    alt="Manager"
    style="transform: scale(0.8)"
    class="absolute bottom-10% right-10%"
>

```mermaid
graph TB
    subgraph Tree
        direction TB
        W0["W<sub>2</sub>"] 
        W1["W<sub>1</sub>"]
        W2["W<sub>0</sub>"]
        W3["W<sub>5</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>3</sub>"]
        W6["W<sub>6</sub>"]

        W0 -.- W1
        W0 -.- W2

        W1 -.- W3
        W1 -.- W4

        W2 -.- W5
        W2 -.- W6
    end
```

</div>

<TUMLogo variant="white" />
