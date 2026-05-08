# Wire into Claude Code

Operator runbook for using spine-lite as a Claude Code PreToolUse hook. The hook itself ships in Phase 3 (`v0.3.0a0`); this page documents the wiring shape so you can prepare your settings ahead of time.

> **Status:** Phase 3 deliverable. The CLI subcommand `spine-lite hook` lands at `v0.3.0a0`. Until then, this is a contract document, not an executable runbook. Sections marked **(Phase 3)** activate when the hook ships.

## What the hook does

Claude Code calls a configured PreToolUse hook before every tool invocation. The hook reads a JSON payload from stdin describing the planned call, returns a JSON decision on stdout, and signals allow/deny via exit code.

spine-lite's hook adapter:

1. Parses the stdin payload.
2. Validates it against the configured manifest (Phase 2: `spine_lite.manifest`).
3. Classifies the tool call to produce an effect set (Phase 2: `spine_lite.classifier`).
4. Applies the posture state machine to produce a decision (Phase 3: `spine_lite.posture`).
5. Emits a deterministic receipt (Phase 3: `spine_lite.receipt`).
6. Writes the decision to stdout and exits 0 (allow) or non-zero (deny).

The hook is the only place in the package that touches stdin/stdout/wall-clock time. Everything inside the pipeline is pure.

## Settings (Phase 3)

Once `v0.3.0a0` ships, register the hook in your Claude Code settings:

```json
{
  "hooks": {
    "PreToolUse": {
      "command": "spine-lite hook",
      "args": ["--manifest", "/path/to/manifest.toml"],
      "timeout_ms": 5000
    }
  }
}
```

The `--manifest` flag is required; without it the hook fails closed (deny).

## Manifest shape (Phase 2)

A manifest is a TOML or JSON document declaring the policy for every tool the LLM can invoke. The exact schema lands with the manifest module; the shape will be:

```toml
[tools.read_file]
effects = ["read"]
postures = ["interactive", "autonomous", "dry_run"]

[tools.write_file]
effects = ["write"]
postures = ["interactive", "autonomous"]

[tools.shell_run]
effects = ["execute", "spawn"]
postures = ["interactive"]

[tools.git_force_push]
effects = ["destructive", "network"]
postures = ["interactive"]
require_confirmation = true
```

Every tool the LLM can call must appear in the manifest. Calls to undeclared tools fail closed with `ManifestError`.

## Test the hook locally (Phase 3)

```bash
cat > /tmp/payload.json <<'EOF'
{
  "tool": "shell_run",
  "args": {"command": "ls -la"}
}
EOF

spine-lite hook --manifest manifest.toml < /tmp/payload.json
echo "exit=$?"
```

Expect exit 0 with a JSON decision on stdout, or non-zero with a structured error.

## Posture management (Phase 3)

The posture is configured per-session. Set it explicitly so the hook fails closed when ambiguous:

```bash
export SPINE_LITE_POSTURE=interactive  # or autonomous, dry_run, locked
spine-lite hook --manifest manifest.toml < payload.json
```

Switching posture mid-session requires re-invoking the hook with the new value; postures don't auto-transition.

## Receipts (Phase 3)

Every decision produces a deterministic receipt. Capture them for audit:

```bash
spine-lite hook --manifest manifest.toml --receipt-dir ./receipts < payload.json
```

Each receipt is content-addressable — same inputs produce identical bytes. Two operators replaying the same session will see byte-identical receipts.

## Failure modes

| Symptom | Likely cause | Resolution |
|---|---|---|
| Hook exits 1, stderr says `ManifestError` | Tool not declared in manifest | Add the tool to the manifest, or remove it from the LLM's available tools. |
| Hook exits 1, stderr says `PostureError` | Tool not allowed under current posture | Change posture, or adjust `tools.<name>.postures` in the manifest. |
| Hook exits 1, stderr says `HookError` | Malformed stdin payload | Check the JSON structure against the Claude Code hook spec. |
| Hook hangs | Manifest validation cycle | Re-run with `--debug`; check for circular references in posture constraints. |

## Roll back

If a hook deployment causes a regression, remove the `PreToolUse` block from your Claude Code settings. spine-lite has no ambient state — there is nothing to clean up beyond the receipts directory if you configured one.

## See also

- [Concepts / Posture and Hooks](../concepts/posture-and-hooks.md) — what the components do.
- [Reference / CLI](../reference/cli.md) — every subcommand.
- [Reference / Glossary](../reference/glossary.md) — vocabulary.
- [Phase 1 History](../history/phase-1.md) — what shipped first.
