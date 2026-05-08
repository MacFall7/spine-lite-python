# Getting Started

Five minutes from clone to a deterministic decision in your REPL.

## Prerequisites

- **Python 3.11 or newer.** The runtime uses `StrEnum`, PEP 695 generics, and modern typing forms. 3.10 is unsupported and will not be added.
- **[uv](https://docs.astral.sh/uv/)** for environment management. Install with `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS) or `winget install astral-sh.uv` (Windows).
- **git** for cloning.

## Install

PyPI publish lands at the end of Phase 3. Until then:

```bash
git clone https://github.com/MacFall7/spine-lite-python
cd spine-lite-python
uv venv
uv sync --all-extras --dev
```

`uv sync` resolves the lockfile, builds the project in editable mode, and installs the docs and dev dependency groups. The first sync also fetches Python 3.11 if you don't have a matching interpreter.

## Verify

```bash
uv run spine-lite version
# 0.1.0a0
```

```bash
uv run python -c "import spine_lite; print(spine_lite.__version__)"
# 0.1.0a0
```

If both print `0.1.0a0`, you're set.

## First decision

The Phase 1 surface is the closed six-class effects taxonomy and the collapse function. Open a REPL:

```python
from spine_lite import Effect, most_restrictive

# Single class — passes through
most_restrictive({Effect.READ})
# <Effect.READ: 'read'>

# Mixed set — collapses to the highest-precedence class
most_restrictive({Effect.READ, Effect.NETWORK, Effect.WRITE})
# <Effect.NETWORK: 'network'>

# DESTRUCTIVE wins over everything
most_restrictive({Effect.READ, Effect.WRITE, Effect.DESTRUCTIVE})
# <Effect.DESTRUCTIVE: 'destructive'>
```

The full precedence ordering lives in [`spine_lite.PRECEDENCE`](reference/api.md):

```python
from spine_lite import PRECEDENCE
PRECEDENCE
# (<Effect.DESTRUCTIVE>, <Effect.SPAWN>, <Effect.EXECUTE>,
#  <Effect.NETWORK>, <Effect.WRITE>, <Effect.READ>)
```

## Errors

Every error from this package descends from `SpineLiteError`:

```python
from spine_lite import SpineLiteError, ManifestError

try:
    raise ManifestError("invalid schema")
except SpineLiteError as exc:
    print(type(exc).__name__, "-", exc)
# ManifestError - invalid schema
```

## What you can do today vs. later

| Capability | Phase | Notes |
|---|---|---|
| Classify a `tool_call` against a manifest | 2 | `spine_lite.classifier.classify` |
| Validate a manifest schema | 2 | `spine_lite.manifest` (pydantic v2) |
| Run the posture state machine | 3 | `spine_lite.posture` |
| Emit a receipt for a decision | 3 | `spine_lite.receipt` |
| Wire as a Claude Code PreToolUse hook | 3 | `spine_lite.hook`, plus `spine-lite hook` CLI |

The full surface lands at `v0.3.0a0`. Until then, the taxonomy and exception hierarchy are the contract — everything else builds on them without changing them.

## Where to go next

- [Concepts / Overview](concepts/overview.md) — the mental model end to end.
- [How-To / Use the API](how-to/use-the-api.md) — practical patterns for the Phase 1 surface.
- [How-To / Wire into Claude Code](how-to/wire-claude-code.md) — the operator runbook (Phase 3 deliverable; the wiring shape is already specified).
- [Reference / API](reference/api.md) — auto-generated from docstrings.
