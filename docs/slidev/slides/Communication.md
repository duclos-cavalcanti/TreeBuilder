---
layout: two-cols-header
---

# Manager x Worker: Communication

- ZMQ Sockets
- Pairwise send and reply initiated by Manager
- Manager: ZMQ_REQ 
- Worker:  ZMQ_REP

::left::

```mermaid
classDiagram
    class MessageFlag{
        NONE = 0 
        PARENT = 1 
        CHILD = 2 
    }

    class MessageType{
        ACK = 0 
        CONNECT = 1 
        COMMAND = 2 
        REPORT = 3
    }

    class Message{
            +int32_t id
            +int64_t ts
            +MessageType type
            +MessageFlag flag
            +char[] data
    }
    %% style Message fill:#0070C0,color:#fff
```

::right::

```mermaid
sequenceDiagram
    participant M as Manager
    participant W1 as Worker_1
    participant W2 as Worker_2

    M->>W1: SEND
    W1->>M: REPLY/ACK

    W1->>W2: SEND
    W2->>W1: REPLY/ACK
```

<TUMLogo variant="white" />
