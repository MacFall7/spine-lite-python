# spine-lite

Deterministic policy and effects runtime for LLM tool calls.

A Python port of [M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite). Same closed effects taxonomy, same precedence rules, same posture state machine — typed, tested, and shipped as a `pip`-installable package.

## Status

Alpha. Phase 1 ships the scaffold, the closed effects taxonomy, and the public exception hierarchy. The classifier, posture state machine, hook adapter, and the rest of the CLI land in Phases 2 and 3.

## Install

PyPI release lands at the end of Phase 3. Until then, install from source:

```bash
git clone https://github.com/MacFall7/spine-lite-python
cd spine-lite-python
uv venv
uv sync --all-extras --dev
```

## Use

```python
from spine_lite import Effect, most_restrictive

most_restrictive({Effect.READ, Effect.NETWORK, Effect.WRITE})
# <Effect.NETWORK: 'network'>
```

Read [Architecture](architecture.md) for the design and [API Reference](api.md) for the full surface.
