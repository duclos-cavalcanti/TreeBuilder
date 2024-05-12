---
layout: two-cols-header
---

# Worker State Machine

- Workers are reply sockets
- Bind and block on `recv()`
- Process message based on type

::left::

```python
while(True):
    m = self.recv_message()
    match m.type:
        case CONNECT: self.connectACK(m)
        case COMMAND: self.commandACK(m)
        case REPORT:  self.reportACK(m)
        case _:       raise RuntimeError()

```

::right::

<img 
    alt="WorkerSM"
    width=200px
    class="absolute top-35% left-60% right-0 bottom-0"
    src="/images/WorkerSM.png"
/>

<TUMLogo variant="white" />
