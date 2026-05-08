# CLAUDE.md

Operating manual for Claude Code sessions in this repo.

## Mission

Deterministic policy and effects runtime for LLM tool calls. Public API and observable semantics are defined by the architectural invariants below; the sibling project at [MacFall7/M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite) is informational and not a parity target. See `docs/explanation/porting-notes.md` for the relationship.

## Authority

You decide:

- File contents, signatures, types, tests, commit messages.
- Refactors that don't change the public API.
- Lint, format, and typecheck rule application.

Mac decides — halt and ask:

- Anything in `src/spine_lite/__init__.py`'s `__all__`.
- New dependencies beyond `pyproject.toml`.
- Phase boundary transitions (1→2, 2→3).
- PyPI publish, repo visibility, GitHub Pages enablement.

## Architectural invariants

1. Closed effects taxonomy. Six members: `READ`, `WRITE`, `NETWORK`, `EXECUTE`, `SPAWN`, `DESTRUCTIVE`. No additions without project sign-off.
2. Precedence: `DESTRUCTIVE > SPAWN > EXECUTE > NETWORK > WRITE > READ`. `most_restrictive()` returns the highest.
3. Determinism. No timestamps, UUIDs, or randomness in `effects.py`, `classifier.py`, `posture.py`, `manifest.py`, `receipt.py`. Inject entropy where you need it.
4. No I/O in those five modules. I/O lives in `hook.py`, `cli.py`, and tests.
5. `mypy --strict` clean on every commit. No `Any` without a comment justifying it.
6. Public API gate. Anything not in `__all__` is private. Private names start with `_`.
7. This file ≤ 150 lines. Refactor before letting it sprawl.

## Style

- Python 3.11+. `from __future__ import annotations` at the top of every module.
- Frozen, slotted, kw-only dataclasses by default.
- Google-style docstrings on every public symbol.
- `logging.getLogger(__name__)` with a `NullHandler` at package init. Library never configures logging.
- Conventional Commits. Subject ≤ 72 chars, imperative mood, no trailing period.
- Direct prose. No marketing tone, no LLM boilerplate, no performative empathy.

## Verification gates

Before any commit:

```
nox -s lint typecheck test
```

All three green or no commit. Before any push, also `coverage` and `docs`. Coverage ≥ 95% on touched files. Docs build with `--strict`.

## Stop conditions

Halt and report when:

- A phase exit gate item is unclear.
- The architectural invariants above conflict with new code or new decisions.
- A test fails you can't explain in 15 minutes.
- You're about to add a dependency.
- You're about to modify `__all__`.
- Two consecutive CI runs fail on the same root cause.

Halt format:

```
HALT: <one-line reason>
Context: <what surfaced>
Options: <2-3 with tradeoffs>
Recommendation: <pick + reasoning>
Awaiting: <decision needed>
```

## Phase plan

- **Phase 1** — scaffold + CI + docs deploy. Tags `v0.1.0a0`.
- **Phase 2** — `manifest`, `classifier`, and the closed `Posture` enum complete. Pydantic v2 models, round-trip parity tests against authored fixtures, `hypothesis` for invariants. Tags `v0.2.0a0`.
- **Phase 3** — `posture`, `receipt`, `hook`, `cli` complete. End-to-end PreToolUse integration with Claude Code. Tags `v0.3.0a0`.

Phase exit gates and receipts live in `RECEIPTS.md`.

## Scope

- In-repo only. Don't touch the sibling project at MacFall7/M87-Spine-lite (informational, not a parity target).
- Don't invoke Patronus, Braintrust, or Arize SDKs (operator-decision pending).
- No network calls in tests. No LLM calls anywhere in the runtime.

## Run registry

Append to `RECEIPTS.md` after every phase day or major milestone. Never edit prior entries. Mac mirrors entries to the canonical run-registry on his side.
