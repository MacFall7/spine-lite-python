# Contributing

This repo is governed under M87 Studio. External PRs are welcome, but the closed six-class effects taxonomy and the public API surface are non-negotiable — proposals to change either need a written rationale on an issue before code lands.

## Local setup

```bash
git clone https://github.com/MacFall7/spine-lite-python
cd spine-lite-python
uv venv
uv sync --all-extras --dev
```

## Verification

Before every commit:

```bash
nox -s lint typecheck test
```

Before every push, also:

```bash
nox -s coverage docs
```

Coverage must stay at or above 95% on every commit and at 100% on the modules a phase implements at its exit gate. Docs build with `--strict`.

## Style

- Python 3.11+. `from __future__ import annotations` at the top of every module.
- `mypy --strict` clean. No `Any` without a comment explaining why.
- Google-style docstrings on every public symbol.
- Frozen, slotted, kw-only dataclasses by default. Mutable only with explicit justification.
- Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`, `ci:`. Subject ≤ 72 chars, imperative mood, no trailing period.
- Direct prose. No marketing copy, no LLM boilerplate, no performative empathy.

## Architecture rules

The closed six-class effects taxonomy and the precedence ordering are the spec. The five core modules — `effects.py`, `classifier.py`, `posture.py`, `manifest.py`, `receipt.py` — are pure: no I/O, no timestamps, no randomness. I/O lives in `hook.py`, `cli.py`, and tests.

## Tests

`pytest` for everything. `hypothesis` for invariants and determinism. The TypeScript reference fixtures (added in Phase 2) are used as-is — no mocking. No network calls in tests; the runtime is offline by design.

## Reviewing

The build operates under explicit phase gates documented in `CLAUDE.md`. Reviews should focus on:

1. Public API stability (anything in `__all__`).
2. Determinism in the pure modules.
3. Parity with the TypeScript reference where applicable.
4. Test coverage on the modules touched.

## Releases

Versioning is SemVer with explicit phase tags: `0.1.0a0` (Phase 1), `0.2.0a0` (Phase 2), `0.3.0a0` (Phase 3). PyPI publishing is gated on a project-level sign-off, not on CI alone.
