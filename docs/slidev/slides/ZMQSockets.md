---
layout: two-cols-header
---

# ZMQ Sockets

- ZMQ_REQ/ZMQ_REP
    - Send/Receiver order has to be respected
    - Reply remembers only last received address
- Other Sockets:
    - Push/Pull 
    - Pub/Sub 
    - Pair/Pair
    - Router/Dealer

<div 
    alt="WorkerSM"
    class="absolute top-15% left-50% right-0 bottom-0"
>

```mermaid
sequenceDiagram
    participant A as REQ
    participant B as REP

    A->>B: Initiates
    B->>A: Replies
```
</div>

<TUMLogo variant="white" />
