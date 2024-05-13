---
layout: two-cols-header
---

# Manager x Worker: Data Structures

- Manager and Workers inherit Node Class
- Nodes own jobs, mapped via a dictionary of threads
- `exec(j:Job)`: 
    - Runs `j.command` in separate thread and returns handler
    - Thread ultimately modifies overloaded Job

<div 
    alt="Node"
    style="transform: scale(1.0)"
    class="absolute top-15% right-10%"
>

```mermaid
classDiagram
    class Node{
            +string ip
            +int port
            +dict jobs: thread -> Job

            +exec(j:Job, callback, args) -> Thread
            +find(j:Job, d:dict)

            _run(j:Job)
            _guard(j:Job)
    }

    class Manager{
    }

    class Worker{
    }

    class Job{
            +string: id
            +string: addr

            +string command
            +int: ret
            +bool: end
            +string: output

            +list: deps[]

            +to_arr() -> char[]
            +from_arr(char[])
    }


    Node --|> Manager
    Node --|> Worker

    style Job fill:#000000,color:#fff
```

</div>

<div 
    alt="Node"
    style="transform: scale(1.0)"
    class="absolute bottom-8% right-12%"
>

```mermaid
block-beta
    N("Node"):1
    space
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

    N --> G

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
            +data = [ Job ]
    }
    %% style Message fill:#0070C0,color:#fff
```

</div>

<TUMLogo variant="white" />
