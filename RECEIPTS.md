# Receipts

Append-only build log for spine-lite-python. Mirrored to the canonical M87 run-registry by the operator. Never edit prior entries.

---

### Phase 1 Day 1 Completion Receipt — 2026-05-08

**Repo:** spine-lite-python @ `2500f61` (branch `claude/setup-project-structure-3YeiT`, 6 commits ahead of `main`)
**Duration:** ~1 hour (Claude Code on Web sandbox session)

**Tasks completed:**

- Authored Phase 1 scaffold from blueprint §4–6 (the local pre-stage referenced in the migration brief did not exist; built from spec).
- Build substrate: `pyproject.toml` (hatchling, pydantic v2, typer, ruff, mypy strict, pytest, hypothesis, nox, mkdocs+mkdocstrings), `noxfile.py`, `.gitignore`, `.gitattributes`, `src/spine_lite/py.typed`.
- Closed six-class effects taxonomy (`READ`, `WRITE`, `NETWORK`, `EXECUTE`, `SPAWN`, `DESTRUCTIVE`) with `PRECEDENCE` tuple and `most_restrictive()` collapse function. Twenty unit tests including parametrized cases and hypothesis invariants for determinism, dominance, and idempotency.
- Public exception hierarchy rooted at `SpineLiteError` with `ManifestError`, `ClassificationError`, `PostureError`, `HookError` subclasses.
- Phase 2/3 module scaffolds (`manifest`, `classifier`, `posture`, `receipt`, `hook`) with phase-pinning docstrings.
- Working `spine-lite` console script with a `version` subcommand. Multi-command structure forced via `@app.callback()` so Phase 2/3 subcommands stay namespaced.
- Mac-voice prose: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `CLAUDE.md` (91 lines, well under the 150-line invariant), `mkdocs.yml`, and six docs pages (`index`, `architecture`, `porting-notes`, `design-rationale`, `integration-claude-code`, `api`).
- CI: 5-job workflow (`lint`, `typecheck`, 9-cell matrix `test py3.11/3.12/3.13 × ubuntu/macos/windows`, `docs-build`). Docs deploy split into a separate workflow gated on `main` + `workflow_dispatch` so first dev-branch push isn't blocked on Pages enablement.
- Six commits in Conventional Commits format, each independently passing the local lint/format/typecheck/test gate before being staged.

**Verification (local, in sandbox):**

- `ruff check`: pass
- `ruff format --check`: pass
- `mypy --strict src tests`: pass, 13 source files clean
- `pytest`: 35 / 35 passed
- `pytest --cov=spine_lite --cov-fail-under=95`: 100% coverage (45 statements, 4 branches, 0 misses)
- `mkdocs build --strict`: pass
- `uv run spine-lite version`: prints `0.1.0a0`
- `python -c "import spine_lite; print(spine_lite.__version__)"`: prints `0.1.0a0`
- CI run on `claude/setup-project-structure-3YeiT`: **NOT VERIFIED** — sandbox has no GitHub Actions API access via the available MCP tools, and `gh` / direct API access is restricted. Operator must confirm at https://github.com/MacFall7/spine-lite-python/actions.

**Phase 1 exit gate status (per blueprint §5):**

| # | Item | Status |
|---|------|--------|
| 1 | Repo public on GitHub | **Mac's call** — sandbox cannot flip visibility |
| 2 | CI green on all 9 matrix cells | **Pending Mac's verification** — sandbox cannot read workflow runs |
| 3 | Docs deployed to GitHub Pages | **Mac's call** — Pages enablement deliberately not triggered |
| 4 | `pip install -e .` works in fresh venv | ✓ verified via `uv sync --all-extras --dev` |
| 5 | `python -c "import spine_lite; print(spine_lite.__version__)"` returns `0.1.0a0` | ✓ verified |
| 6 | `pytest tests/unit/test_effects.py` passes (taxonomy + precedence) | ✓ 20/20 incl. hypothesis |
| 7 | CHANGELOG entry for v0.1.0a0 | ✓ present |
| 8 | CLAUDE.md ≤ 150 lines | ✓ 91 lines |
| 9 | All commits Conventional Commits format | ✓ |
| 10 | Receipt appended to run-registry | ✓ this entry; operator mirrors to canonical registry |

**Open items / halts:**

- The sandbox-vs-spec environment delta (no `~/m87-career-ops/`, no pre-staged scaffold). Authored from blueprint spec under Option 1; reconcile against any private pre-staged variants on the operator's local box before tagging `v0.1.0a0`.
- Three exit-gate items (1, 2, 3) require operator action: confirm CI green on the 9-cell matrix, flip repo visibility to public, enable GitHub Pages.

**Next:** Halt for Mac at the Phase 1 exit gate. Phase 2 (manifest + classifier, ~5 working days) does not start without an explicit go.

---

### Phase 1 Day 2 Receipt — 2026-05-08

**Repo:** spine-lite-python branch `claude/setup-project-structure-3YeiT`, ahead of `main` by the docs-expansion commits below.
**Duration:** ~1.5 hours (continuation of the same Claude Code Web session).

**Tasks completed:**

- **CI fix.** Two commits resolving the `setup-uv@v3` cache-key failure: untrack `uv.lock` from `.gitignore` (with the `design-rationale.md` entry inverted), then commit the lockfile (1,396 lines, 68 packages). Operator confirmed all 9 matrix cells green and merged via PR #1 (`d90e72c`). Repo now public; GitHub Pages live at <https://macfall7.github.io/spine-lite-python/>.
- **Documentation expansion to archivist grade.** Restructured `docs/` into Diátaxis quadrants (Tutorial / How-To / Reference / Explanation) plus a History section. Twelve new pages, three substantial rewrites of moved pages, mkdocs nav updated, mkdocs --strict clean.
- **Top-level prose rewritten.** Iron-clad README (status grid, repository layout, copy-paste install, today-vs-later capability matrix, deep links into the docs site), SECURITY.md added (vulnerability reporting, supported versions, trust model, threat model, dependency policy), CONTRIBUTING.md reduced to a quick-start that points at the long-form guide in `docs/how-to/contribute.md`.

**New documentation surface (counts):**

- 1 landing page (`docs/index.md`, rewritten).
- 1 tutorial (`docs/getting-started.md`).
- 3 concept pages (overview, effects-taxonomy, posture-and-hooks).
- 4 how-to pages (use-the-api, wire-claude-code, contribute, release).
- 4 reference pages (api refined, cli, exceptions, glossary).
- 5 explanation pages (architecture refined, design-rationale moved, porting-notes expanded, invariants new, faq new).
- 1 history page (phase-1).
- 1 SECURITY.md.
- README + CONTRIBUTING + CHANGELOG updated.

**Verification (local, in sandbox):**

- `ruff check`: pass
- `ruff format --check`: pass
- `mypy --strict src tests`: pass, 13 source files clean
- `pytest`: 35 / 35 passed
- Coverage: 100% (45 statements, 4 branches, 0 misses)
- `mkdocs build --strict`: pass
- CI on the previous push (commits up to `9e65986`): all 9 matrix cells + lint + typecheck + docs-build green; confirmed by operator.

**Phase 1 exit gate (final):**

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
| 10 | Receipt appended | ✓ |

All 10 items clear. **Phase 1 closed.**

**Open items / halts:**

- None. Phase 2 (manifest + classifier, ~5 working days, target `v0.2.0a0`) is gated on operator go per `CLAUDE.md`.

**Next:** Halt for Mac at the Phase 1 → Phase 2 transition. Per blueprint §11, completion of Phase 1 unblocks the Braintrust application thread on the operator's side.
