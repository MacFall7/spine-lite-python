# Phase 1

The build log for the first ship. What landed, in what order, and what verified it. Mirrors [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md) with day-of-build context.

## Headline

**Shipped:** `v0.1.0a0`, 2026-05-08. Branch `claude/setup-project-structure-3YeiT` merged to `main` via PR #1. CI green across all 9 matrix cells. Repo public, GitHub Pages live.

**Scope:** Project scaffold, the closed six-class effects taxonomy with precedence and `most_restrictive`, the public exception hierarchy rooted at `SpineLiteError`, scaffolds for the Phase 2 / Phase 3 modules, a working `spine-lite version` CLI subcommand, and the full documentation site you're reading now.

**What's stable:** `Effect`, `PRECEDENCE`, `most_restrictive`, the exception hierarchy, the public `__all__` surface, the `spine-lite version` console script.

**What's not yet built:** `manifest`, `classifier`, `posture`, `receipt`, `hook`. Stubs are in place with phase-pinning docstrings; they'll fill in during Phases 2 and 3.

## Commit timeline

| # | SHA | Subject |
|---|---|---|
| 1 | `ccfce54` | `chore: initial project scaffold (pyproject, uv, nox)` |
| 2 | `b17aa10` | `feat: effects taxonomy with closed 6-class enum and precedence` |
| 3 | `4a80062` | `feat: exception hierarchy and public API surface` |
| 4 | `6cfefa0` | `feat: classifier, posture, manifest, receipt, hook scaffolds + cli` |
| 5 | `0e58bef` | `docs: README, CONTRIBUTING, CHANGELOG, CLAUDE governance, mkdocs, architecture` |
| 6 | `2500f61` | `ci: GitHub Actions matrix and docs workflows` |
| 7 | `3359239` | `docs: phase 1 day 1 receipt` |
| 8 | `444cc5b` | `chore: track uv.lock for CI cache reproducibility` |
| 9 | `9e65986` | `chore: add uv.lock for CI determinism` |

Each commit independently passed the local verification gate (lint + format + mypy + test) before being staged. The two `chore: ...uv.lock...` commits resolved the only CI failure in the phase: the initial scaffold ran with `uv.lock` gitignored, and `astral-sh/setup-uv@v3` with `enable-cache: true` keys against that file's default glob, so every job died at the setup step. Tracking the lockfile fixed it.

## Day 1 — scaffold and first push

- Authored the scaffold from blueprint spec. The pre-staged scaffold referenced in the migration brief did not exist in the build environment; everything came from the architectural invariants and phase plan in `CLAUDE.md`.
- Six logical commits, each green at the local gate. Pushed to `claude/setup-project-structure-3YeiT`.
- First CI run: 12/12 jobs failed in setup step. Local gate had been clean, so the failure was environment-specific. Halted for a log paste rather than guessing.

## Day 1 — root cause and fix

- Operator identified: `setup-uv@v3` cache key requires `uv.lock`. Lockfile was gitignored.
- Two-commit fix: untrack from `.gitignore` (with `design-rationale.md` inverted), then commit the actual lockfile (1,396 lines, 68 packages).
- CI re-run: green across all 9 matrix cells (`lint`, `typecheck`, `test py3.11/3.12/3.13 × ubuntu/macos/windows`, `docs-build`).
- Operator merged via PR #1 to `main`, flipped repo to public, enabled GitHub Pages.

## Verification on the green run

- `ruff check`: clean
- `ruff format --check`: clean
- `mypy --strict src tests`: clean across 13 source files
- `pytest`: 35 / 35 passing
- Coverage: 100% (45 statements, 4 branches, 0 misses)
- `mkdocs build --strict`: clean

## Phase 1 exit gate (final state)

| # | Item | State |
|---|------|-------|
| 1 | Repo public on GitHub | ✓ |
| 2 | CI green on all 9 matrix cells | ✓ |
| 3 | Docs deployed to GitHub Pages | ✓ |
| 4 | `pip install -e .` works in fresh venv | ✓ |
| 5 | `spine_lite.__version__ == "0.1.0a0"` | ✓ |
| 6 | `tests/unit/test_effects.py` passes | ✓ (20/20 incl. hypothesis) |
| 7 | CHANGELOG entry for `v0.1.0a0` | ✓ |
| 8 | CLAUDE.md ≤ 150 lines | ✓ (91 lines) |
| 9 | All commits in Conventional Commits format | ✓ |
| 10 | Receipt appended to `RECEIPTS.md` | ✓ |

All 10 items clear. Phase 1 closed.

## Lessons for Phase 2

- **Lockfile-as-cache-key matters.** When CI uses `setup-uv` with caching, the lockfile is part of the contract, not an optional reproducibility nicety. Track it from the start.
- **Local gate ≠ CI gate.** The local invocation (`uv run pytest`) passes without a lockfile because `uv` resolves on the fly. CI's setup steps may rely on the lockfile being present even before they install deps. Plan for that.
- **Halt before guessing.** When 12 jobs fail in seconds with the same root cause, asking for one log beat applying three speculative fixes. The first three hypotheses (setup-uv version, `uv sync` semantics, hatchling PEP 639) all missed the actual cause; an extra round-trip with the operator was cheaper than three speculative pushes.

## See also

- [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md) — the canonical phase-day receipts.
- [`CHANGELOG.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CHANGELOG.md) — what shipped in each version.
- [Architecture](../explanation/architecture.md) — the shape Phase 1 established.
- [Design Rationale](../explanation/design-rationale.md) — decisions made during the build.
