# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/MacFall7/spine-lite-python/compare/v0.2.0a0...HEAD
[0.2.0a0]: https://github.com/MacFall7/spine-lite-python/releases/tag/v0.2.0a0
[0.1.0a0]: https://github.com/MacFall7/spine-lite-python/releases/tag/v0.1.0a0
