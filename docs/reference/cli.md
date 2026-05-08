# CLI Reference

Every subcommand of the `spine-lite` console script. Phase 1 ships only `version`; subsequent phases extend the table without changing what's already there.

## Synopsis

```text
spine-lite [OPTIONS] COMMAND [ARGS]...
```

Help is printed when invoked with no arguments. Run `spine-lite --help` to see the full list of subcommands available in your installed version.

## Subcommands

| Subcommand | Phase | Purpose |
|---|---|---|
| [`version`](#version) | 1 — shipped | Print the installed version. |
| [`validate-manifest`](#validate-manifest-phase-2) | 2 | Validate a manifest file against the schema. |
| [`classify`](#classify-phase-2) | 2 | One-shot classification of a tool call. |
| [`hook`](#hook-phase-3) | 3 | stdin/stdout PreToolUse adapter for Claude Code. |

## `version`

```text
spine-lite version
```

Prints the installed version of `spine-lite` and exits 0.

```bash
$ spine-lite version
0.1.0a0
```

This is the integration-test surface for the Phase 1 exit gate. If the console script is registered correctly and the package imports cleanly, this command works.

## `validate-manifest` (Phase 2)

```text
spine-lite validate-manifest [OPTIONS] MANIFEST_PATH
```

Validates a TOML or JSON manifest against the Pydantic v2 schema. Exits 0 on success, non-zero on validation error. Prints structured diagnostics on stderr.

Planned options:

- `--format {toml,json,auto}` — input format. Default: `auto` (inferred from file extension).
- `--strict` — treat warnings (e.g. unused fields) as errors.

## `classify` (Phase 2)

```text
spine-lite classify [OPTIONS] --manifest PATH < tool_call.json
```

Reads a tool call from stdin, classifies it against `--manifest`, and writes a `Decision` to stdout as JSON. Exits 0 if classification succeeds (regardless of allow/deny); exits non-zero if the input fails to parse.

This is a debugging surface — the production path is `spine-lite hook`, which adds the posture state machine and receipt emission.

## `hook` (Phase 3)

```text
spine-lite hook --manifest PATH [--posture POSTURE] [--receipt-dir DIR] < payload.json
```

The Claude Code PreToolUse adapter. Reads a hook payload from stdin, runs the full pipeline (manifest validation → classification → posture transition → decision → receipt), writes the decision to stdout, and exits 0 (allow) or non-zero (deny).

Planned options:

- `--manifest PATH` — required; path to the manifest file.
- `--posture POSTURE` — current operational posture. Default: `interactive`.
- `--receipt-dir DIR` — write receipts to this directory. Default: no receipts written.
- `--debug` — emit verbose diagnostics on stderr.

See [How-To / Wire into Claude Code](../how-to/wire-claude-code.md) for the full operator runbook.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success (allow, for `hook`) |
| 1 | Decision was deny (`hook` only) or generic spine-lite error |
| 2 | Usage error: bad arguments, missing file, malformed input |
| 64+ | Reserved for future structured failure codes |

## See also

- [Reference / API](api.md) — programmatic surface.
- [Reference / Exceptions](exceptions.md) — error catalog.
- [How-To / Wire into Claude Code](../how-to/wire-claude-code.md) — operator runbook.
