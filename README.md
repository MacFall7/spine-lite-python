# spine-lite

[![CI](https://github.com/MacFall7/spine-lite-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MacFall7/spine-lite-python/actions/workflows/ci.yml)
[![docs](https://img.shields.io/badge/docs-mkdocs--material-blue)](https://macfall7.github.io/spine-lite-python/)
[![python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/MacFall7/spine-lite-python)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Deterministic policy and effects runtime for LLM tool calls.

Six-class effects taxonomy on state × boundary × reversibility axes. Ordinal precedence. Content-addressable receipts. Wires into Claude Code as a PreToolUse hook (Phase 3); usable anywhere you can shell out to a subprocess. Sibling project to [M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite) — see [Porting Notes](docs/explanation/porting-notes.md) for the relationship.

## What it does

You give it a tool call and a manifest of declared effects. It returns a deterministic decision: which effects fire, what the dominant class is, and a structured receipt you can replay by SHA. Built to wire into Claude Code as a PreToolUse hook; usable anywhere you can shell out to a subprocess.

The runtime is offline by design — no clocks, no randomness, no network, no LLM calls inside the runtime itself.

## Status

| Phase | Scope | Version | State |
|-------|-------|---------|-------|
| 1 | Scaffold, taxonomy, exceptions, CLI surface, CI matrix, docs | `v0.1.0a0` | Shipped 2026-05-08 |
| 2 | Manifest schema, classifier, Posture enum, parity + hypothesis tests | `v0.2.0a0` | Shipped 2026-05-08 |
| 3 | Posture transitions, Disposition, Receipt, hook adapter, full CLI, E2E | `v0.3.0a0` | Shipped 2026-05-09 |

See [`RECEIPTS.md`](RECEIPTS.md) for build progress and [docs/history/phase-1.md](https://macfall7.github.io/spine-lite-python/history/phase-1/) for the Phase 1 narrative.

## Install

Not yet published to PyPI (confirmed 2026-07-10). Install from source:

```bash
git clone https://github.com/MacFall7/spine-lite-python
cd spine-lite-python
uv venv
uv sync --all-extras --dev
```

Verify:

```bash
uv run spine-lite version
# 0.3.0a0
```

Need uv? `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS) or `winget install astral-sh.uv` (Windows).

## Quick example

```python
from spine_lite import Effect, most_restrictive, SpineLiteError

# Collapse any non-empty effect set to its dominant class
most_restrictive({Effect.READ, Effect.NETWORK, Effect.WRITE})
# <Effect.NETWORK: 'network'>

# Precedence is total: DESTRUCTIVE > SPAWN > EXECUTE > NETWORK > WRITE > READ
most_restrictive({Effect.READ, Effect.WRITE, Effect.DESTRUCTIVE})
# <Effect.DESTRUCTIVE: 'destructive'>

# Every error in the package descends from SpineLiteError
issubclass(SpineLiteError, Exception)  # True
```

The classifier and PreToolUse hook ship as of `v0.3.0a0` (Phases 2 and 3). The taxonomy is the contract; everything else builds on it without changing it.

## What this gives you

The closed six-class effects taxonomy:

| Effect | Meaning | Examples |
|--------|---------|----------|
| `READ` | observation only | reading a file, listing a dir, querying without writing |
| `WRITE` | persistent state change to caller-owned storage | writing a file, updating a row, appending a log |
| `NETWORK` | outbound network call | HTTP request, DNS lookup, Slack message |
| `EXECUTE` | subprocess invocation, no fork | `subprocess.run`, `os.system`, shell pipeline |
| `SPAWN` | subprocess that may fork-and-detach | `Popen` with no `wait`, daemon launch, `nohup` |
| `DESTRUCTIVE` | irreversible state change | `rm -rf`, `git push --force`, dropping a table |

Ordered by precedence: `DESTRUCTIVE > SPAWN > EXECUTE > NETWORK > WRITE > READ`. `most_restrictive()` collapses any non-empty set to the highest class.

Same input → same output, every time. No clocks, no randomness, no I/O in the core.

## What this isn't

- **Not a model.** No LLM calls happen inside the runtime.
- **Not a sandbox.** It classifies and decides; enforcement happens in the hook adapter.
- **Not extensible at runtime.** The taxonomy is closed by design — extending it is a project-level decision.
- **Not a network library.** There are zero network calls in the runtime, ever.

## Documentation

Full docs at <https://macfall7.github.io/spine-lite-python/>. Quick links:

- [**Getting Started**](https://macfall7.github.io/spine-lite-python/getting-started/) — five-minute install + first decision.
- [**Concepts / Overview**](https://macfall7.github.io/spine-lite-python/concepts/overview/) — mental model end to end.
- [**How-To / Use the API**](https://macfall7.github.io/spine-lite-python/how-to/use-the-api/) — practical patterns, today.
- [**How-To / Wire into Claude Code**](https://macfall7.github.io/spine-lite-python/how-to/wire-claude-code/) — operator runbook.
- [**Reference / API**](https://macfall7.github.io/spine-lite-python/reference/api/) — auto-generated from docstrings.
- [**Reference / Glossary**](https://macfall7.github.io/spine-lite-python/reference/glossary/) — vocabulary.
- [**Explanation / Architecture**](https://macfall7.github.io/spine-lite-python/explanation/architecture/) — why it's shaped this way.
- [**Explanation / Invariants**](https://macfall7.github.io/spine-lite-python/explanation/invariants/) — the rules nothing in this repo gets to break.
- [**Explanation / FAQ**](https://macfall7.github.io/spine-lite-python/explanation/faq/) — common questions about the design.

## Repository layout

```
spine-lite-python/
├── src/spine_lite/         # the runtime (5 pure modules + hook + cli + exceptions)
├── tests/                  # unit + smoke tests, all offline
├── docs/                   # mkdocs source — Diátaxis-structured
├── .github/workflows/      # CI matrix + Pages deploy
├── CLAUDE.md               # repo governance for Claude Code sessions (≤ 150 lines)
├── CONTRIBUTING.md         # contributor quick-start
├── CHANGELOG.md            # what shipped in each version
├── RECEIPTS.md             # append-only phase-day completion log
├── SECURITY.md             # vulnerability reporting + trust model
├── pyproject.toml          # hatchling build, deps pinned via uv.lock
└── uv.lock                 # tracked; CI cache keys against it
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the quick-start and [docs/how-to/contribute.md](https://macfall7.github.io/spine-lite-python/how-to/contribute/) for the long form. The closed effects taxonomy and the public API are non-negotiable; proposals to change either need a written rationale on an issue first.

## Security

See [SECURITY.md](SECURITY.md). The runtime is deterministic and offline; trust questions live in your manifest.

## Governance

This repo runs under M87 Studio with explicit phase boundaries. Authority split, halt conditions, and verification gates are in [`CLAUDE.md`](CLAUDE.md). Phase exit gates and receipts are in [`RECEIPTS.md`](RECEIPTS.md).

## License

[MIT](LICENSE). Maintained by Mac McFall.
