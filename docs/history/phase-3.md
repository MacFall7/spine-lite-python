# Phase 3

The build log for the third ship. Posture transitions, Disposition, Receipt, hook adapter, full CLI, and E2E coverage. Mirrors `RECEIPTS.md` with day-of-build context.

## Headline

**Shipped:** `v0.3.0a0`, 2026-05-09. Six commits on `claude/setup-project-structure-3YeiT` ahead of `main` after the operator's Phase 2 ff-merge to `main` at `e5e37bf`. CI green across all 9 matrix cells.

**Scope:** Pure posture state machine (`transition`, `evaluate`), the closed `Disposition` enum, the content-addressable `Receipt`, the I/O hook adapter (`run_hook`, `main`), the full `spine-lite` CLI surface (`validate-manifest`, `classify`, `hook`), and an end-to-end test suite that exercises the same path Claude Code invokes when wiring the PreToolUse hook.

**What's stable:** Everything in `spine_lite.__all__` after this phase. Phase 3 adds `Disposition`, `Receipt`, `transition`, `evaluate` to the surface. The full public API:

```python
from spine_lite import (
    PRECEDENCE, Effect, most_restrictive,
    Manifest, ToolDefinition, parse_manifest,
    ToolCall, Decision, classify,
    Posture, Disposition, transition, evaluate,
    Receipt,
    SpineLiteError, ManifestError, ClassificationError,
    PostureError, HookError,
    __version__,
)
```

`spine_lite.hook.run_hook` and `spine_lite.hook.main` remain accessible via the submodule import for programmatic users; the canonical operator entry point is the `spine-lite hook` console script.

**What's not in scope:** Real-host integration (smoke against an actual Claude Code session) — the E2E tests run via subprocess against the installed `spine-lite` console script, which is the closest faithful test the build sandbox supports. PyPI publish remains a project-level decision.

## Commit timeline

| # | SHA prefix | Subject |
|---|---|---|
| 1 | `6cdcde5` | `chore: enable attr_list mkdocs extension` |
| 2 | `29bfb63` | `feat: posture state machine with Disposition and evaluate` |
| 3 | `7cd329b` | `feat: Receipt dataclass with deterministic serialization` |
| 4 | `0d92074` | `feat: PreToolUse hook adapter` |
| 5 | `d3e6cb6` | `feat: full CLI surface with integration and E2E tests` |
| 6 | (this commit) | `release: bump to v0.3.0a0 + phase 3 exit receipt` |

Each commit independently passed the local verification gate before being staged.

## Design choices recorded

- **Disposition is closed at three members.** `ALLOW`, `DENY`, `ESCALATE`. Adding a fourth (e.g. `LOG_ONLY`) would require updating every consumer that exhaustively matches and the exit-code contract; same closed-taxonomy logic applies as for `Effect`.
- **`evaluate` is layered explicitly.** The order of checks matters: posture allow-list first (one tool, many postures), `LOCKED`/`DRY_RUN` posture-specific rules next, `require_confirmation` last. Reordering the posture-specific checks against the allow-list would let a deny-listed tool slip through under `LOCKED`.
- **Exit codes use a wide range.** `0` ALLOW / `1` DENY / `2` ESCALATE / `64` HOOK_ERROR / `65` MANIFEST_ERROR. `64+` is sysexits.h territory for "internal failure" — keeps policy outcomes distinguishable from protocol errors at the host's exit-code layer.
- **Receipt fields are content-addressable.** `to_canonical_json` uses `sort_keys=True`, `ensure_ascii=False`, and compact separators. The hash is `sha256(canonical_json.encode("utf-8"))`. No timestamps, no UUIDs, no per-run metadata — anything that varies between runs lives in the hook's external metadata, not the receipt itself.
- **Hook contract is intentionally minimal.** Top-level JSON object with `tool` (required, non-empty string) and `arguments` (optional, object). Other fields are ignored. This lets the same hook adapt to multiple host hook formats; spine-lite doesn't need to be re-released when a host's payload schema evolves.
- **Stdin ↔ stdout is the boundary, not a config file.** The CLI's `--manifest` flag is the configuration; payload comes via stdin; decision goes to stdout. No log files written by default. Whether to capture receipts to disk is the operator's choice (a `--receipt-dir` flag is reserved for a future minor release).
- **CLI uses `Annotated`-style typer parameters.** Avoids `B008` cleanly and matches typer's modern recommended idiom. The one carve-out: `Path` stays at the top of `cli.py` (TC003 ignored for this file only) because typer introspects the runtime annotation to do `exists=True` validation.
- **E2E tests run via `python -m spine_lite.cli` subprocess.** True fresh-venv install is out of scope for the build sandbox, but invoking the installed entry point captures everything except the console-script shim.

## Verification on the green run

- `ruff check`: clean
- `ruff format --check`: clean
- `mypy --strict src tests`: clean across 19 source files
- `pytest`: 209 / 209 passing
- Coverage: 100% on every runtime module
- `mkdocs build --strict`: clean
- Hypothesis: 9 properties × 1,000 examples each (six classifier + three receipt)
- E2E subprocess tests: 7 cases (5 posture × tool combinations + byte-stability + version)

## Phase 3 exit gate

| # | Item | State |
|---|------|-------|
| 1 | `posture.py` (transitions + evaluate) 100% coverage | ✓ (34 stmts, 14 branches, 0 miss) |
| 2 | `receipt.py` 100% coverage | ✓ (22 stmts, 0 miss) |
| 3 | `hook.py` 100% coverage | ✓ (54 stmts, 6 branches, 0 miss) |
| 4 | `cli.py` 100% coverage | ✓ (49 stmts, 0 miss) |
| 5 | Integration tests for every subcommand | ✓ |
| 6 | E2E smoke via installed entry point | ✓ (7 subprocess cases) |
| 7 | mypy `--strict` clean | ✓ |
| 8 | CI green on all 9 matrix cells | (pending push verification) |
| 9 | CHANGELOG entry for `v0.3.0a0` | ✓ |
| 10 | All commits in Conventional Commits format | ✓ |
| 11 | Receipt appended to `RECEIPTS.md` | ✓ (this commit) |

## Lessons for after Phase 3

- **Closed enums fold neatly into ordered transition tables.** Once `Posture` was closed at four members, encoding the transition rules as `dict[Posture, frozenset[Posture]]` produced a fully-typed structure with zero special-cased code paths.
- **Hypothesis on dataclasses with `st.builds(...)` is cheap.** The `Receipt` strategy at 1,000 examples per property is ~3 seconds. Tightening the strategy bounds (max sizes for arguments, text fields) keeps it that way.
- **Annotated-style typer is worth the upgrade.** `B008` ignore is an anti-pattern; the Annotated form is cleaner and the typer docs now lead with it.

## See also

- [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md) — canonical phase-day receipts.
- [`CHANGELOG.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CHANGELOG.md) — what shipped in each version.
- [Phase 2 history](phase-2.md) — what shipped immediately before.
- [Wire into Claude Code](../how-to/wire-claude-code.md) — operator runbook now backed by a working hook.
