# Contributing

The quick-start. The full contributor guide lives at [docs/how-to/contribute.md](https://macfall7.github.io/spine-lite-python/how-to/contribute/).

This repo is governed under M87 Studio. External PRs are welcome, but the closed six-class effects taxonomy and the public API surface are non-negotiable — proposals to change either need a written rationale on an issue before code lands.

## Setup

```bash
git clone https://github.com/MacFall7/spine-lite-python
cd spine-lite-python
uv venv
uv sync --all-extras --dev
```

## Verify

Before every commit:

```bash
nox -s lint typecheck test
```

Before every push, also:

```bash
nox -s coverage docs
```

Coverage stays ≥ 95%; docs build with `--strict`.

If you don't have nox, the underlying tools work directly:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest --cov=spine_lite --cov-fail-under=95
uv run mkdocs build --strict
```

## Style at a glance

- Python 3.11+. `from __future__ import annotations` everywhere.
- `mypy --strict` clean. No `Any` without a justifying comment.
- Google-style docstrings on every public symbol.
- Conventional Commits, subject ≤ 72 chars, imperative mood, no trailing period.
- Direct prose. No marketing tone, no LLM boilerplate.

## Architecture rules

The closed six-class effects taxonomy and the precedence ordering are the spec. The five pure modules (`effects.py`, `manifest.py`, `classifier.py`, `posture.py`, `receipt.py`) contain no I/O, no clocks, no randomness. I/O lives in `hook.py`, `cli.py`, and tests.

If your change cannot be made within those rules, that's an issue for discussion — not a PR.

## Where to read more

- [Full contributor guide](https://macfall7.github.io/spine-lite-python/how-to/contribute/)
- [Architecture](https://macfall7.github.io/spine-lite-python/explanation/architecture/)
- [Invariants](https://macfall7.github.io/spine-lite-python/explanation/invariants/)
- [Design Rationale](https://macfall7.github.io/spine-lite-python/explanation/design-rationale/)
- [Release process](https://macfall7.github.io/spine-lite-python/how-to/release/)
- [`CLAUDE.md`](CLAUDE.md) — repo governance for Claude Code sessions.
