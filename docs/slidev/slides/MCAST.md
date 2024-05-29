---
layout: two-cols-header
---

# MCAST Tree Performance

- Root: 
    - Sends messages to children
- Proxies: 
    - Forwards messages from parent to children
- Leaves: 
    - Stores latency difference
    - prints to `stdout` 90% percentile latency

<div 
    alt="WorkerSM"
    style="transform: scale(1.9)"
    class="absolute bottom-10% left-20%"
>

```mermaid
sequenceDiagram
    participant P as PARENT
    participant C1 as CHILD_1
    participant C2 as CHILD_2

    P->>C1: M0
    P->>C2: M0

    C1->>L1: M0
    C1->>L2: M0

    C2->>L3: M0
    C2->>L4: M0
```
</div>

::left::

<div 
    alt="cpp"
    style="transform: scale(0.8)"
    class="absolute top-15% right-5%"
>

```cpp
typedef struct MsgUDP {
    uint32_t id;
    uint64_t ts;
} MsgUDP_t;

double get_percentile(const std::vector<int64_t>& data, 
                      double percentile) {
    // stuff 
}

```

</div>

<TUMLogo variant="white" />
