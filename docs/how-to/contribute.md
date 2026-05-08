# Contribute

The full contributor guide. The root [`CONTRIBUTING.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CONTRIBUTING.md) is a quick-start summary; this page is the long form.

## Before you write code

Read these in order:

1. The [Mission and Architecture](../explanation/architecture.md).
2. The [Invariants](../explanation/invariants.md) — the rules nothing in this repo gets to break.
3. The [Design Rationale](../explanation/design-rationale.md) — past decisions, in case the question has been settled already.
4. [`CLAUDE.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CLAUDE.md) — repo governance, including the authority split between contributors and the project lead.

## Before you propose an API change

The closed effects taxonomy and the public API are non-negotiable without project sign-off. If your change touches either:

- Open an issue first with a written rationale.
- Wait for a HALT-format response from the project lead before sending a PR.
- Expect to update the parity tests against the TypeScript reference and add a Porting Notes entry.

Without prior agreement, PRs that modify `__all__` or extend the `Effect` enum will be closed with a request to convert to an issue.

## Local setup

```bash
git clone https://github.com/MacFall7/spine-lite-python
cd spine-lite-python
uv venv
uv sync --all-extras --dev
```

The first sync also fetches Python 3.11 if needed and resolves the lockfile (~70 packages).

## Verification gates

Before every commit:

```bash
nox -s lint typecheck test
```

Or, if you don't have nox installed and want to invoke the underlying tools directly:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

Before every push, also:

```bash
nox -s coverage docs
```

Or:

```bash
uv run pytest --cov=spine_lite --cov-fail-under=95
uv run mkdocs build --strict
```

Coverage must be at or above 95% on every commit, and at 100% on the modules a phase implements at its exit gate. Docs build with `--strict` (treats warnings as errors).

## Coding standards

- **Python 3.11+.** `from __future__ import annotations` at the top of every module.
- **`mypy --strict` clean.** No `Any` without a comment justifying the carve-out. The repo has zero `Any` today; keep it that way.
- **Google-style docstrings** on every public symbol. Include `Examples:` for non-trivial functions.
- **Frozen, slotted, kw-only dataclasses by default.** Mutable only with explicit justification in a comment.
- **Imports** sorted by ruff/isort: stdlib → third-party → first-party. No wildcard imports. Use `if TYPE_CHECKING:` for cycle-prone or annotation-only imports.
- **Pure modules** (`effects`, `manifest`, `classifier`, `posture`, `receipt`) contain no I/O, no clocks, no randomness. I/O lives in `hook` and `cli`.
- **Conventional Commits.** Subject ≤ 72 chars, imperative mood, no trailing period. Types in use: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `ci`, `perf`.
- **Voice.** Direct prose. No marketing tone, no LLM boilerplate, no performative empathy. See [`docs/explanation/design-rationale.md`](../explanation/design-rationale.md) and the existing READMEs for the baseline.

## Tests

`pytest` for everything. `hypothesis` for invariants and determinism properties. Parametrize aggressively; one parametrized test beats six near-duplicates.

The TypeScript reference fixtures arrive with Phase 2 — use them as-is. Don't mock them. Parity is the spec.

```python
import pytest
from hypothesis import given, strategies as st

from spine_lite.effects import Effect, most_restrictive, PRECEDENCE


@pytest.mark.parametrize(
    ("effects", "expected"),
    [
        ({Effect.READ}, Effect.READ),
        ({Effect.READ, Effect.WRITE}, Effect.WRITE),
    ],
)
def test_dominance_table(effects: set[Effect], expected: Effect) -> None:
    assert most_restrictive(effects) is expected


@given(effects=st.sets(st.sampled_from(list(Effect)), min_size=1))
def test_result_is_member_of_input(effects: set[Effect]) -> None:
    assert most_restrictive(effects) in effects
```

No network calls in tests. Determinism is the runtime contract — the test suite enforces it.

## Pull requests

- One logical change per PR.
- Reference an issue if one exists.
- Include the verification gate output in the PR description if any cell took unusual time.
- Keep the diff focused — drive-by refactors slow review.
- The project lead reviews every PR; expect a HALT-format message if anything is unclear, and respond in kind.

## Architecture rules (recap)

The closed effects taxonomy and its precedence ordering are the spec. The five core modules (`effects.py`, `classifier.py`, `posture.py`, `manifest.py`, `receipt.py`) are pure — no I/O, no timestamps, no randomness. I/O belongs in `hook.py`, `cli.py`, and tests.

If your change cannot be made within those rules, that's a project-level discussion, not a PR.

## See also

- [How-To / Release](release.md) — the release process.
- [Explanation / Invariants](../explanation/invariants.md) — the hard-line rules.
- [Explanation / FAQ](../explanation/faq.md) — common questions about the design.
