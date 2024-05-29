---
layout: two-cols-header
---

# Manager x Worker: Data Structures

- Manager and Workers inherit Node Class
- Nodes: 
    - own jobs, mapped via a dictionary of threads
    - are able of runnig jobs in separate threads 
    - are able of guarding against job dependencies

<div 
    alt="Node"
    style="transform: scale(0.6)"
    class="absolute top-0% right-14%"
>

```mermaid
classDiagram
    class Node{
            ...
            +dict jobs: thread -> Job

            +exec(callback, args) -> Thread
            +find(j:Job) -> Thread

            _run(j:Job)
            _guard(j:Job)
            _launch(t:Thread, args=(,))
    }

    class Manager{
    }

    class Worker{
    }

    Node --|> Manager
    Node --|> Worker

    style Job fill:#000000,color:#fff
```

</div>

<div 
    alt="Node"
    style="transform: scale(0.9)"
    class="absolute bottom-10% right-12%"
>

```mermaid
block-beta
    N("Node"):1
    block:G
        columns 2
        J("<font color=white>Jobs"):1
        block:jobs
            columns 1
            A["T1 => J1"] 
            B["T2 => J2"] 
        end
        Guard("<font color=white>Guards"):1
        block:guards
            columns 1
            C["T1 => J0"] 
            D["--------"] 
        end
    end

    G --> N

    style J fill:#000000
    style Guard fill:#000000
```

</div>

<div 
    alt="Message"
    style="transform: scale(0.8)"
    class="absolute left-15% bottom-5%"
>

```mermaid
classDiagram
    class Message{
            +id   = 4
            +ts   = 1715280981565948
            +type = REPORT/ACK
            +flag = NONE
            +data = Report
    }
    %% style Message fill:#0070C0,color:#fff
```

</div>

<TUMLogo variant="white" />
