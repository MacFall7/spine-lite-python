# Invariants

The hard-line rules. Nothing in this repo gets to break them. Listed here for reference; enforcement lives in the test suite, the type checker, and the CI gate.

## 1. Closed effects taxonomy

`spine_lite.Effect` has exactly six members: `READ`, `WRITE`, `NETWORK`, `EXECUTE`, `SPAWN`, `DESTRUCTIVE`. Adding a class is a project-level decision that requires a HALT to the project lead. The taxonomy is closed by design.

**Enforced by:** `tests/unit/test_effects.py::test_taxonomy_has_exactly_six_members`, `test_taxonomy_member_names`.

## 2. Precedence ordering is fixed

`spine_lite.PRECEDENCE` is exactly:

```python
(Effect.DESTRUCTIVE, Effect.SPAWN, Effect.EXECUTE,
 Effect.NETWORK, Effect.WRITE, Effect.READ)
```

Reordering is a project-level decision. Every dominance comparison in the runtime resolves through this constant.

**Enforced by:** `test_effects.py::test_precedence_is_canonical_order`, `test_precedence_covers_every_effect`.

## 3. Determinism

The five pure modules — `effects`, `manifest`, `classifier`, `posture`, `receipt` — contain no clocks, no UUIDs, no randomness, no network, no filesystem. Same input → same output, every time.

**Enforced by:** code review + hypothesis property tests (`test_most_restrictive_is_deterministic`). Future phases will add receipt-byte-stability tests against fixture inputs.

## 4. I/O boundary is `hook` and `cli` only

Only `spine_lite.hook` and `spine_lite.cli` may touch stdin, stdout, the filesystem, or wall-clock time. The pure modules don't import `os`, `sys`, `time`, `random`, `uuid`, or `requests`/`httpx`/`urllib`.

**Enforced by:** code review. A future grep-based test in CI is on the table if drift becomes a concern.

## 5. `mypy --strict` clean

Every commit passes `mypy --strict` with zero `Any` carve-outs. If a third-party stub forces an `Any`, justify it with an inline comment.

**Enforced by:** `nox -s typecheck`, run on every commit and every CI build.

## 6. Public API gate

Anything not in `spine_lite.__all__` is private and may change without notice. Private symbols start with an underscore. Modifying `__all__` is a project-level decision.

**Enforced by:** code review + the convention that private names start with `_`.

## 7. Coverage at or above 95%

Every commit keeps line coverage at 95% or higher across the package. Each phase's exit gate ratchets up to 100% on the modules that phase implements.

**Enforced by:** `pytest --cov-fail-under=95` in CI; phase exit gates verified by hand against the test report.

## 8. Conventional Commits

Every commit subject is in Conventional Commits form (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`, `ci:`, `perf:`). Subject ≤ 72 chars, imperative mood, no trailing period.

**Enforced by:** code review. A pre-commit hook is not adopted (see [Design Rationale / Pre-commit hooks not adopted](design-rationale.md)).

## 9. CLAUDE.md ≤ 150 lines

The repo-level governance file at [`CLAUDE.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CLAUDE.md) does not exceed 150 lines. If it grows past, refactor — don't let it sprawl.

**Enforced by:** code review.

## 10. No LLM calls inside the runtime

Zero LLM API calls, zero model invocations, zero "let me just check with the AI" indirection inside `src/spine_lite/`. The runtime classifies and decides; if you want a model in the loop, that's a separate concern that lives outside this package.

**Enforced by:** code review + the dependency list (no `anthropic`, `openai`, `cohere`, etc. in `pyproject.toml`).

## 11. No network calls in tests

Every test runs offline. The full suite passes with no internet connection.

**Enforced by:** code review + (Phase 2+) an explicit pytest fixture that fails on outbound socket connections.

## 12. RECEIPTS.md is append-only

Phase exit receipts and phase-day completion receipts live in [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md). Never edit prior entries. Append only.

**Enforced by:** code review + the CHANGELOG / RECEIPTS distinction (CHANGELOG documents what shipped; RECEIPTS documents what verifies the ship).

## See also

- [Architecture](architecture.md) — why the invariants exist.
- [Design Rationale](design-rationale.md) — decisions that produced them.
- [`CLAUDE.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CLAUDE.md) — the governance front-matter for repo sessions.
