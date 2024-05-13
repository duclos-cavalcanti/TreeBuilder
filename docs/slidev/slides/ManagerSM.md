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

<div
    alt="StepQ"
    style="transform: scale(0.6)"
    class="absolute top--5 left-50% right-0 bottom-0"
>
```mermaid
block-beta
    Q("<font color=white>StepQ")
    space
    block:items
        columns 1
        A["____"] 
        B["____"]
        C["____"]
    end

    Q --> items

    style Q fill:#FF0000
```
</div>

<div
    alt="StepClass"
    style="transform: scale(0.6)"
    class="absolute top--5 left-70% right-0 bottom-0"
>
```mermaid
classDiagram
    class Step{
            +string: action = "CONNECT"
            +string: description
    }

    %% style Step fill:#0065BD,color:#fff
```

</div>

<img 
    alt="ManagerSM"
    width=320px
    class="absolute top-37% left-60% right-0 bottom-0"
    src="/images/ManagerStateMachine.png"
/>

<TUMLogo variant="white" />
