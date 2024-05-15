---
layout: two-cols-header
---

# Manager x Worker: Workflow [Step_i = 0]

- Manager reads in YAML _script_
- Populates step queue
- Fetches first step

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
        A["CONN"] 
        B["ROOT"]
        C["____"]
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
        W2["W<sub>2</sub>"]
        W3["W<sub>3</sub>"]
        W4["W<sub>4</sub>"]
        W5["W<sub>5</sub>"]
        W6["W<sub>6</sub>"]
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
        A["____"] 
        B["____"] 
    end

    J --> items

    style J fill:#000000
```
</div>

::left::

<div
    alt="YAML"
    style="transform: scale(1.0)"
    class="absolute top-35% left-5%"
>
```yaml
name: DEFAULT
hyperparameter: 0.5
rate: 10 
duration: 10
addrs:
  - "localhost:9091"
  - "localhost:9092"
  - "localhost:9093"
  - "localhost:9094"
  - "localhost:9095"
  - "localhost:9096"
steps:
  - action: "CONNECT"
    description: "Establish connection workers."
    data: 0
  - action: "ROOT"
    description: "Choose root among worker nodes."
    data: 0
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
        W0["<font color=black>W<sub>0</sub>"]
        W1["<font color=black>W<sub>1</sub>"]
        W2["<font color=black>W<sub>2</sub>"]
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

        style W0 fill:#000000
        style W1 fill:#000000
        style W2 fill:#000000
        style W3 fill:#000000
        style W4 fill:#000000
        style W5 fill:#000000
        style W6 fill:#000000
    end
    M --> Tree
```

</diV>

<TUMLogo variant="white" />