---
layout: two-cols-header
---

# Manager x Worker: Jobs

- Manager and Workers inherit Node Class
- Nodes own jobs, mapped via a dictionary of threads
- `exec_job(j:Job)`: 
    - Runs `j.command` in separate thread
    - stores thread handler in dict
    - thread ultimately modifies the overloaded Job

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

            +recv_message()
            +send_message(m:Message)
            +exec_job(j:Job)
            +find_job(j:Job)
            +check_jobs()
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
            +list: dependencies

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
    class="absolute bottom-7% right-10%"
>

```mermaid
block-beta
    N("Node"):1
    space
    J("<font color=white>Jobs"):1
    block:jobs
        columns 1
        A["T1 => J1"] 
        B["T2 => J2"] 
        C["T3 => J3"] 
    end

    N --> J

    style J fill:#000000
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
