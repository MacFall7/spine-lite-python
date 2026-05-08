# Design Rationale

Decisions made during the port that the migration brief did not specify. One entry per decision. The blueprint is silent on these; the choices below are the conservative defaults.

## `StrEnum` over `str, Enum`

`StrEnum` (Python 3.11+) is the canonical form. The repo requires 3.11, so the older `str, Enum` recipe adds nothing.

## Hatchling as the build backend

Default for new uv projects, full PEP 621 support, integrates cleanly with `uv build` and the GitHub Actions release flow.

## License declaration: SPDX string + `license-files`

PEP 639 superseded the legacy table form. `license = "MIT"` plus `license-files = ["LICENSE"]` is the current standard.

## `uv.lock` not committed

Spine-lite is a library. Downstream consumers resolve their own dependency tree. CI installs from `pyproject.toml` directly. If reproducibility on CI ever becomes a concern, the lockfile can be added later — committing it is a one-way door, omitting it is not.

## CI matrix: 3.11 / 3.12 / 3.13 × Linux / macOS / Windows

Nine cells, matching the migration brief. Drops Python 3.10 because `requires-python = ">=3.11"` lets us use `StrEnum`, PEP 695 generics, and the modern `typing` form.

## Coverage threshold: 95% repo-wide, 100% at phase exit

The repo-wide gate is 95% so early commits with stub modules don't fail. Each phase exit gate ratchets up to 100% on the modules that phase implements.

## Pre-commit hooks not adopted

Verification runs through `nox`. A pre-commit framework adds a second source of truth; the existing verification gates already cover the surface.

## CLI framework: Typer

Matches the migration brief and integrates with Pydantic v2. `argparse` would be lighter but the manifest validation surface in Phase 2 benefits from Typer's pydantic-aware command parameters. The single-command app uses an explicit `@app.callback()` so the multi-command structure stays stable as Phase 2 and 3 add subcommands.

## Logging: `NullHandler` at package init

Library code never configures logging. `cli.py` is the only place that adds handlers. The migration brief mandates this; this entry just records the choice for searchability.

## Exception strategy

A single base (`SpineLiteError`) with one subclass per major failure mode (`ManifestError`, `ClassificationError`, `PostureError`, `HookError`). Closed in spirit — adding new classes is permitted, but every new class descends from the base. Callers can `except SpineLiteError` for blanket handling or pick a subclass for finer control.

## CI triggers vs. docs deploy triggers

`ci.yml` runs on every push to `main` and to feature branches; the docs build is included in `ci.yml` (so we know docs build clean on every push). `docs.yml` deploys to GitHub Pages from `main` and on `workflow_dispatch`. Splitting build (always) from deploy (gated) means the dev branch can verify docs without requiring Pages to be enabled before the first push.

## RECEIPTS.md at repo root

The migration brief points at a canonical run-registry on the operator's local machine. This sandbox can't reach that file. Receipts are written to `RECEIPTS.md` at the repo root (not inside `docs/` so they don't show up in the published site) and mirrored to the canonical registry by the operator.
