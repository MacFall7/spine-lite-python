# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0a0] — 2026-05-09

### Added

- **Posture state machine.** `transition(current, target)` enforces an explicit transition table (`INTERACTIVE` is the hub; `LOCKED` only unlocks to `INTERACTIVE`; identity transitions are always allowed). `evaluate(posture, definition, decision)` is a pure function that maps a classified call under a posture to a `Disposition`.
- **`Disposition` closed enum.** Members: `ALLOW`, `DENY`, `ESCALATE`. `ESCALATE` is only returned under `INTERACTIVE`; `AUTONOMOUS` fails closed (denies) on any tool flagged `require_confirmation=True`.
- **`Receipt` dataclass** (frozen, slotted, kw-only). Carries the tool, arguments, canonical effects, dominant effect, rationale, posture, disposition, and the echoed `require_confirmation` flag. Three methods make it content-addressable: `to_canonical_dict()`, `to_canonical_json()` (sort_keys, ensure_ascii=False, compact separators), and `content_hash()` (SHA-256 of the canonical JSON). Same input → same hash, byte-stable across runs and platforms.
- **PreToolUse hook adapter** (`spine_lite.hook`). `run_hook(manifest, payload, *, posture)` is the testable core: accepts `str` or `bytes` payloads, returns `(Receipt, exit_code)`. `main(manifest, *, stdin, stdout, stderr, posture)` is the I/O wrapper: reads stdin, writes the receipt's canonical JSON to stdout (or a structured error JSON on failure), returns the exit code per the documented contract (`0`/`1`/`2`/`64`/`65`).
- **Full CLI surface.** `validate-manifest`, `classify`, and `hook` subcommands ship alongside the existing `version`. `Annotated`-style typer params throughout. Console-script invocation via `python -m spine_lite.cli` is the supported entry for Claude Code's PreToolUse hook.
- **Integration and E2E tests.** Typer's `CliRunner` exercises every subcommand × posture × disposition combination; subprocess-based E2E tests run `python -m spine_lite.cli` against the authored fixtures, the closest equivalent in the build sandbox to the blueprint's "fresh-venv install + Claude Code wiring" smoke.
- `Receipt`, `Disposition`, `transition`, `evaluate` added to `spine_lite.__all__`.
- `attr_list` mkdocs extension enabled — required by the badge buttons on the docs landing page.

### Changed

- `mypy` per-file ignore: `src/spine_lite/cli.py` ignores `TC003` because typer introspects `Path` annotations at runtime to do path validation. `tests/**` ignores `S603` (subprocess calls constructed in-process from fixtures, not user input).

## [0.2.0a0] — 2026-05-08

### Added

- **`Posture` closed enum** (`spine_lite.posture`) with members `INTERACTIVE`, `AUTONOMOUS`, `DRY_RUN`, `LOCKED`. `Posture` added to `spine_lite.__all__`. Phase 3 will add the transition functions; Phase 2 ships only the enum so the manifest schema can validate posture constraints against a closed set.
- **Pydantic v2 manifest schema** (`spine_lite.manifest`) with `ToolDefinition` and `Manifest` (frozen, `extra="forbid"`). Effects and postures are canonicalised on construction (deduplicated and sorted by enum-declaration order) so JSON round-trip is byte-stable across runs and platforms. `parse_manifest()` accepts dicts, JSON strings, and JSON bytes, wrapping `pydantic.ValidationError` as `ManifestError` with the original error attached as `__cause__`. `Manifest`, `ToolDefinition`, and `parse_manifest` added to `__all__`.
- **Classifier** (`spine_lite.classifier`) with `ToolCall`, `Decision`, and `classify(tool_call, manifest) -> Decision`. Pure function, deterministic, no I/O. `Decision` carries a canonical effects tuple, the dominant effect under `PRECEDENCE`, and a byte-stable rationale string. `ToolCall`, `Decision`, and `classify` added to `__all__`.
- **Authored test fixtures** in `tests/fixtures/`: `manifest_minimal.json`, `manifest_basic.json`, `manifest_full.json`, `decisions_basic.json`. Parametrized parity tests confirm round-trip JSON byte-stability per fixture and decision parity per case.
- **Hypothesis property tests** for the classifier — 1,000 examples each across determinism, dominance, manifest-fidelity, byte-stable rationale, manifest round-trip stability, and argument independence.
- `SECURITY.md` with vulnerability-reporting process, supported-version policy, and the runtime trust model.
- Documentation site restructured into Diátaxis quadrants (Tutorial / How-To / Reference / Explanation) plus a History section. New pages: getting-started, concepts/{overview,effects-taxonomy,posture-and-hooks}, how-to/{use-the-api,wire-claude-code,contribute,release}, reference/{cli,exceptions,glossary}, explanation/{invariants,faq}, history/phase-1.
- Iron-clad README with status grid, repository layout, and links into the docs site.

### Changed

- **Mission reframed.** `MacFall7/M87-Spine-lite` is now documented as a **sibling project** rather than a parity target. The blueprint's stale "TS reference" framing is dropped from `CLAUDE.md`, `README.md`, `docs/index.md`, `docs/explanation/architecture.md`, `docs/explanation/porting-notes.md`, and seven other doc pages. The §9 halt and operator resolution that produced this change are recorded verbatim in `RECEIPTS.md` as the Phase 2 Day 1 opening entry.
- `docs/architecture.md`, `docs/design-rationale.md`, `docs/porting-notes.md`, `docs/integration-claude-code.md`, and `docs/api.md` moved under `docs/explanation/`, `docs/how-to/`, and `docs/reference/`.
- `CONTRIBUTING.md` reduced to a quick-start that points at the long form in the docs site.
- `mypy` config: `disallow_untyped_decorators = false` for `tests.*` so hypothesis decorators don't require local `# type: ignore` carve-outs. Runtime modules stay strict; zero `Any` carve-outs in `src/`.

## [0.1.0a0] — 2026-05-08

### Added

- Closed six-class effects taxonomy: `READ`, `WRITE`, `NETWORK`, `EXECUTE`, `SPAWN`, `DESTRUCTIVE`. Canonical precedence ordering and `most_restrictive()` collapse function.
- Public exception hierarchy rooted at `SpineLiteError` with `ManifestError`, `ClassificationError`, `PostureError`, and `HookError` subclasses.
- Scaffolds for `classifier`, `manifest`, `posture`, `receipt`, and `hook` modules — implementations land in Phases 2 and 3.
- `spine-lite` console script with a `version` subcommand.
- CI matrix across Python 3.11/3.12/3.13 on Linux, macOS, and Windows.
- MkDocs documentation with `mkdocstrings`, deployable to GitHub Pages.
- Repo governance file (`CLAUDE.md`) and build-progress receipt log (`RECEIPTS.md`).

[Unreleased]: https://github.com/MacFall7/spine-lite-python/compare/v0.3.0a0...HEAD
[0.3.0a0]: https://github.com/MacFall7/spine-lite-python/releases/tag/v0.3.0a0
[0.2.0a0]: https://github.com/MacFall7/spine-lite-python/releases/tag/v0.2.0a0
[0.1.0a0]: https://github.com/MacFall7/spine-lite-python/releases/tag/v0.1.0a0
