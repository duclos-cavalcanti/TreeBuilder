---
layout: two-cols-header
---

# Manager State Machine

- Manager actively sends requests to workers
- Fetches steps from `step_queue`
- Process steps based on action type

::left::

```python
while(True):
    step = self.pop_step()
    if not step: break
        match step["action"]:
            case "CONNECT": self.establish()
            case "ROOT":    self.root()
            case "REPORT":  self.report()
            case _:         raise RuntimeError()
```

::right::

<img 
    alt="StepQ"
    width=320px
    class="absolute top-17% left-60% right-0 bottom-0"
    src="/images/StepQ.png"
/>

<img 
    alt="ManagerSM"
    width=320px
    class="absolute top-37% left-60% right-0 bottom-0"
    src="/images/ManagerStateMachine.png"
/>

<TUMLogo variant="white" />
