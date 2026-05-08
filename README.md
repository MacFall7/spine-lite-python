# spine-lite

Deterministic policy and effects runtime for LLM tool calls.

A Python port of [M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite). Same closed effects taxonomy, same precedence rules, same posture state machine — typed, tested, and shipped as a `pip`-installable package.

## Status

Alpha. Phase 1 ships the scaffold, the closed effects taxonomy, and the public exception hierarchy. The classifier, posture state machine, hook adapter, and the rest of the CLI land in Phases 2 and 3. See `RECEIPTS.md` for build progress and `docs/architecture.md` for the plan.

> PyPI release lands at the end of Phase 3. Until then, install from source.

## Install

```bash
git clone https://github.com/MacFall7/spine-lite-python
cd spine-lite-python
uv venv
uv sync --all-extras --dev
```

Verify:

```bash
uv run spine-lite version
# 0.1.0a0
```

## Quickstart

```python
from spine_lite import Effect, most_restrictive

most_restrictive({Effect.READ, Effect.NETWORK, Effect.WRITE})
# <Effect.NETWORK: 'network'>
```

The classifier and PreToolUse hook arrive in later phases. The taxonomy is the contract; everything else builds on top of it.

## What this is

A six-class taxonomy of side effects every tool call falls into:

| Effect | Meaning |
| --- | --- |
| `READ` | observation only |
| `WRITE` | persistent state change to caller-owned storage |
| `NETWORK` | outbound network call |
| `EXECUTE` | subprocess invocation |
| `SPAWN` | fork-and-detach subprocess |
| `DESTRUCTIVE` | irreversible change |

Ordered by precedence: `DESTRUCTIVE > SPAWN > EXECUTE > NETWORK > WRITE > READ`. `most_restrictive()` collapses any non-empty set to the highest class. Same input produces the same output every time. No clocks, no randomness, no I/O in the core.

## What this is not

- Not a model. No LLM calls happen inside spine-lite.
- Not a sandbox. It classifies and decides; enforcement happens in the hook.
- Not extensible at runtime. The taxonomy is closed by design — extending it is a project-level decision.

## Documentation

Full docs publish to GitHub Pages once Phase 1 is signed off.

## Contributing

See `CONTRIBUTING.md`. The closed effects taxonomy and the public API are non-negotiable; proposals to change either need a written rationale on an issue first.

## License

MIT. See `LICENSE`.
