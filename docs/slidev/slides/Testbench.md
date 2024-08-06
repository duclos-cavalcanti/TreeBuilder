---
layout: two-cols-header
---

# Tree-Finder: Testbench and Heuristic


1. Allocate __N__ VMs.
2. Apply Proposed Heuristic 
3. Apply Lemon-Drop
4. Evaluate Multicast Performances: 
    - Vanilla x Heuristic x LemonDrop

<div
    alt="Pool"
    style="transform: scale(0.8)"
    class="absolute top-13% left-40% right-0 bottom-0"
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
        W8["W<sub>8</sub>"]
        W9["W<sub>9</sub>"]
        W10["W<sub>10</sub>"]
        W11["W<sub>11</sub>"]

        style W2 fill:#FF0000,color:#fff

        style W8 fill:#000000,color:#fff
        style W9 fill:#000000,color:#fff
        style W10 fill:#000000,color:#fff
        style W11 fill:#000000,color:#fff
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
    class="absolute bottom-10% right-5%"
>

```mermaid
graph TB
    subgraph Tree [Tree D=2, F=2]
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

        style W0 fill:#FF0000,color:#fff
    end
```

</div>

<img 
    alt="Heuristic"
    style="transform: scale(0.5)"
    src="/images/MethodHeuristicNew.png"
    class="absolute top-25% right-10%"
/>

<TUMLogo variant="white" />
