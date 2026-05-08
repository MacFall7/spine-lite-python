# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `SECURITY.md` with vulnerability-reporting process, supported-version policy, and the runtime trust model.
- Documentation site restructured into Diátaxis quadrants (Tutorial / How-To / Reference / Explanation) plus a History section. New pages: getting-started, concepts/{overview,effects-taxonomy,posture-and-hooks}, how-to/{use-the-api,wire-claude-code,contribute,release}, reference/{cli,exceptions,glossary}, explanation/{invariants,faq}, history/phase-1.
- Iron-clad README with status grid, repository layout, and links into the docs site.

### Changed

- `docs/architecture.md`, `docs/design-rationale.md`, `docs/porting-notes.md`, `docs/integration-claude-code.md`, and `docs/api.md` moved under `docs/explanation/`, `docs/how-to/`, and `docs/reference/`.
- `CONTRIBUTING.md` reduced to a quick-start that points at the long form in the docs site.

## [0.1.0a0] — 2026-05-08

### Added

- Closed six-class effects taxonomy: `READ`, `WRITE`, `NETWORK`, `EXECUTE`, `SPAWN`, `DESTRUCTIVE`. Canonical precedence ordering and `most_restrictive()` collapse function.
- Public exception hierarchy rooted at `SpineLiteError` with `ManifestError`, `ClassificationError`, `PostureError`, and `HookError` subclasses.
- Scaffolds for `classifier`, `manifest`, `posture`, `receipt`, and `hook` modules — implementations land in Phases 2 and 3.
- `spine-lite` console script with a `version` subcommand.
- CI matrix across Python 3.11/3.12/3.13 on Linux, macOS, and Windows.
- MkDocs documentation with `mkdocstrings`, deployable to GitHub Pages.
- Repo governance file (`CLAUDE.md`) and build-progress receipt log (`RECEIPTS.md`).

[Unreleased]: https://github.com/MacFall7/spine-lite-python/compare/v0.1.0a0...HEAD
[0.1.0a0]: https://github.com/MacFall7/spine-lite-python/releases/tag/v0.1.0a0
