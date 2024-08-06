---
layout: two-cols-header
---

# Tree-Finder: Experiment

- Runs: encoded as `JSON` dictionaries
- Manager goes through runs:
    - builds tree (K/N)
    - evaluates performance
    - stores results { `csv`, `json` }
- Types:  `Best` x `Worst` x `Rand` x `LemonDrop`
- Strategies: 
    - p90 
    - p50 
    - heuristic: 0.7 * p90 + 0.3 x stddev

<div 
    alt="sequenceDiagram"
    style="transform: scale(1.0)"
    class="absolute top-12% right-30%"
>

```json 
Run:
{
    "name": "BEST",
    "strategy": {
        "key": "heuristic",
        "reverse": false
    },
    "parameters": {
        "hyperparameter": 4,
        "rate": 10000,
        "duration": 10,
        "evaluation": 30,
        ...
    },
    "tree": {
        "root": "",
        "nodes": []
        ...
    },
    "pool": [],
    "stages": [],
    "perf": [],
    "timers": {}
},

```

</div>

<div 
    alt="sequenceDiagram"
    style="transform: scale(1.0)"
    class="absolute top-12% right-9%"
>

```json 
Result:
{
    "id": "foobar",
    "root": "W1",
    "key": "p90",
    "select": 0, 
    "rate": rate,
    "duration": duration,
    "items": [],
    "selected": []
```

```json 
Item:
{
    "addr":     "W2",
    "p90":      0.0,
    "p75":      0.0,
    "p50":      0.0,
    "p25":      0.0,
    "stddev":   0.0,
    "mean":     0.0,
    "recv":     0,
}
```
</div>

<TUMLogo variant="white" />
