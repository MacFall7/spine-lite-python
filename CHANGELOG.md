# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
