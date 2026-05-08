# Release

The release process. Versioning, tagging, changelog management, and (eventually) PyPI publishing.

## Versioning

SemVer with explicit phase tags:

| Tag | Phase | What ships |
|---|---|---|
| `v0.1.0a0` | Phase 1 | Scaffold, taxonomy, exceptions, CLI surface, CI matrix, docs |
| `v0.2.0a0` | Phase 2 | Manifest schema, classifier with parity tests |
| `v0.3.0a0` | Phase 3 | Posture state machine, receipts, hook adapter, end-to-end |

Bug-fix releases within a phase use the `aN+1` suffix (`v0.1.0a1`, `v0.1.0a2`, ...). The phase number bumps on phase exit.

PyPI publish is gated on a project-level decision, not on CI alone. The package may stay source-only beyond `v0.3.0a0` if there's reason to.

## Phase exit gate

A phase ships only when every item on its exit gate is verified. The gates live in [`docs/history/phase-1.md`](../history/phase-1.md) (and equivalent files for later phases) and in [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md).

Phase 1 exit gate (recap):

1. Repo public on GitHub.
2. CI green on all 9 matrix cells (3.11/3.12/3.13 × Linux/macOS/Windows).
3. Docs deployed to GitHub Pages.
4. `pip install -e .` works in a fresh venv.
5. `python -c "import spine_lite; print(spine_lite.__version__)"` returns the target version.
6. The phase's headline test file passes (Phase 1: `tests/unit/test_effects.py`).
7. CHANGELOG entry for the new version.
8. CLAUDE.md ≤ 150 lines.
9. All commits in Conventional Commits format.
10. Receipt appended to `RECEIPTS.md` and mirrored to the operator's run-registry.

## Cut a release

```bash
# 1. Verify the gate (run from a clean checkout)
nox -s lint typecheck test coverage docs

# 2. Bump the version in pyproject.toml and __init__.py
# (One-line change in both files; keep them in sync.)

# 3. Update CHANGELOG.md — move [Unreleased] entries to [vX.Y.Za0]
# Add the date in YYYY-MM-DD form. Add the comparison link at the bottom.

# 4. Append the phase exit receipt to RECEIPTS.md

# 5. Commit and tag
git add pyproject.toml src/spine_lite/__init__.py CHANGELOG.md RECEIPTS.md
git commit -m "release: vX.Y.Za0"
git tag -a vX.Y.Za0 -m "Phase N exit"

# 6. Push tag and branch
git push origin main
git push origin vX.Y.Za0
```

CI re-runs on the tag push; verify all cells green before announcing.

## Build artifacts

```bash
uv build
ls dist/
# spine_lite-X.Y.ZaN-py3-none-any.whl
# spine_lite-X.Y.ZaN.tar.gz
```

Inspect the wheel's metadata and contents:

```bash
uv run python -m zipfile -l dist/spine_lite-X.Y.ZaN-py3-none-any.whl
uv run python -m wheel unpack dist/spine_lite-X.Y.ZaN-py3-none-any.whl -d /tmp/wheel-check
```

The wheel must contain `spine_lite/py.typed`. Without it, downstream type-checkers won't pick up annotations.

## PyPI publish (gated on project-level approval)

```bash
# Test PyPI first
uv publish --publish-url https://test.pypi.org/legacy/

# Then real PyPI, only after the test install verifies clean
uv publish
```

The `uv publish` command reads credentials from `UV_PUBLISH_TOKEN` or `~/.pypirc`. Don't put credentials in the repo or in CI secrets without project-level approval.

## Rollback

If a release goes out broken:

1. **Don't `pip install --force-reinstall`** to fix it for users — they'll keep the broken version cached.
2. **Yank the bad release on PyPI** (`uv publish --yank` or via the PyPI web UI). Yanked releases stay installable by exact-version pin but are excluded from new resolutions.
3. **Cut a fix release** with the next `aN+1` suffix.
4. **Add a CHANGELOG entry** for the yanked version explaining what was wrong.
5. **Append a `release: yank vX.Y.Za0`** receipt to `RECEIPTS.md`.

Yanking is a one-way door at the user-experience level — once a release is out, treat it as permanent in your changelog even if you yank it from PyPI.

## See also

- [Phase 1 History](../history/phase-1.md) — what shipped in the first release.
- [Explanation / Invariants](../explanation/invariants.md) — what every release must preserve.
