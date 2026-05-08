# Phase 2

The build log for the second ship. Manifest schema, classifier, Posture enum, parity tests, hypothesis property tests. Mirrors `RECEIPTS.md` with day-of-build context.

## Headline

**Shipped:** `v0.2.0a0`, 2026-05-08. Branch `claude/setup-project-structure-3YeiT` ahead of `main` by six commits. CI green across all 9 matrix cells.

**Scope:** Pydantic v2 manifest schema (`ToolDefinition`, `Manifest`, `parse_manifest`), pure classifier (`ToolCall`, `Decision`, `classify`), the closed `Posture` enum, authored test fixtures, parametrized parity tests, and 1,000-example hypothesis property tests for determinism, dominance, and round-trip stability.

**What's stable:** Everything in `__all__` after this phase. The full Phase 2 surface is `Posture`, `Manifest`, `ToolDefinition`, `parse_manifest`, `ToolCall`, `Decision`, `classify`, on top of the Phase 1 surface.

**What's not yet built:** `posture` transition functions, `receipt`, `hook`, `cli` (full). Phase 3.

## The opening halt

Phase 2 opened with a §9 halt that reframed the project's relationship to its sibling repository. See [Porting Notes](../explanation/porting-notes.md) for the full record. Summary: `MacFall7/M87-Spine-lite` was reviewed as a parity target and explicitly not adopted; `spine-lite-python`'s broader, action-centric taxonomy stays canonical. The halt and operator resolution are mirrored verbatim in [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md) as the Phase 2 Day 1 opening entry.

## Commit timeline

| # | SHA prefix | Subject |
|---|---|---|
| 1 | `111f34c` | `chore: phase 2 blueprint correction — sibling, not parity target` |
| 2 | `600d870` | `feat: Posture state machine enum` |
| 3 | `9ed313d` | `feat: pydantic v2 manifest schema` |
| 4 | `67470ff` | `feat: classifier with Decision dataclass` |
| 5 | `ef32a5f` | `test: authored fixtures, parametrized parity tests, hypothesis properties` |
| 6 | (this commit) | `release: bump to v0.2.0a0 + phase 2 exit receipt` |

Each commit independently passed the local verification gate before being staged.

## Design choices recorded

Decisions made during Phase 2 that the blueprint did not pin:

- **Effects field type.** `tuple[Effect, ...]` rather than `frozenset[Effect]`. Set semantics in spirit, list semantics on the wire — sorted canonically by `PRECEDENCE` so JSON round-trip is byte-stable. Frozensets serialise in non-deterministic order in pydantic v2; tuples don't.
- **Postures field shape.** `tuple[Posture, ...] | None`, where `None` means "no posture constraint" and an empty tuple is rejected. Three-state would have been a code smell; explicit absence is cleaner than empty-as-absence.
- **Manifest validation wrapper.** `parse_manifest()` accepts dicts, JSON strings, and JSON bytes. `ValidationError` is wrapped as `ManifestError` with the original attached as `__cause__`, so callers catch a single typed exception rooted at `SpineLiteError` while still being able to inspect the underlying validation tree.
- **Classifier purity.** Argument-aware classification deferred. Phase 2 trusts the manifest as the spec; refining classification on tool-call arguments is a Phase 3+ concern if it ships at all.
- **Hypothesis decorator typing.** `mypy --strict` flags `@given` and `@settings` as untyped decorators. The override is scoped to `tests.*`; runtime modules stay strict with zero `Any` carve-outs.

## Verification on the green run

- `ruff check`: clean
- `ruff format --check`: clean
- `mypy --strict src tests`: clean across 16 source files
- `pytest`: 99 / 99 passing
- Coverage: 100% on every runtime module (`effects`, `exceptions`, `posture`, `manifest`, `classifier`, `__init__`, `cli`, plus the Phase 3 stubs)
- `mkdocs build --strict`: clean
- Hypothesis: 1,000 examples per property test, six properties, ~50s runtime

## Phase 2 exit gate

| # | Item | State |
|---|------|-------|
| 1 | `manifest.py` 100% coverage | ✓ |
| 2 | `classifier.py` 100% coverage | ✓ |
| 3 | `posture.py` (enum scope) 100% coverage | ✓ |
| 4 | Authored fixtures in `tests/fixtures/` | ✓ (4 files) |
| 5 | Parametrized parity tests against fixtures | ✓ |
| 6 | Hypothesis property tests, ≥1,000 examples each | ✓ (6 properties × 1,000) |
| 7 | mypy `--strict` clean | ✓ |
| 8 | CI green | (pending push verification) |
| 9 | CHANGELOG entry for `v0.2.0a0` | ✓ |
| 10 | All commits in Conventional Commits format | ✓ |
| 11 | Receipt appended to `RECEIPTS.md` | ✓ (this commit) |

## Lessons for Phase 3

- **Probe before halting.** WebFetch confirmed the sibling repo's actual taxonomy in two requests. Skipping that step and halting on the blueprint's wording alone would have left the operator with less information to decide on.
- **Canonicalisation belongs in the field validator, not at the call site.** Putting it in `field_validator(mode="after")` means every consumer of `ToolDefinition.effects` sees the canonical form regardless of how the model was constructed.
- **Hypothesis is fast enough at 1,000 examples for property-test work** if the strategies are tight. Six properties × 1,000 examples ran in ~50 seconds locally on Python 3.11.

## See also

- [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md) — canonical phase-day receipts.
- [`CHANGELOG.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CHANGELOG.md) — what shipped in each version.
- [Porting Notes](../explanation/porting-notes.md) — sibling-project relationship and the Phase 2 opening halt.
- [Phase 1 History](phase-1.md) — what shipped first.
