# Posture, Receipts, and Hooks

The Phase 2 and Phase 3 components in outline. Implementations land at `v0.2.0a0` and `v0.3.0a0` respectively; what's described here is the contract those phases fill in.

## Manifest (Phase 2)

A manifest is the policy document for a tool. It declares:

- The tool's name and signature.
- The set of effects each invocation can produce.
- Posture constraints — under which postures the tool may be invoked, and under which it must be refused.

Manifests are validated as Pydantic v2 models and round-trip the TypeScript reference fixtures byte-for-byte after JSON normalisation.

## Classifier (Phase 2)

```python
def classify(tool_call: ToolCall, manifest: Manifest) -> Decision: ...
```

Pure function. Given a tool call and a manifest, returns a `Decision` carrying:

- `effects: frozenset[Effect]` — every effect the call can produce.
- `most_restrictive: Effect` — the dominant class.
- `rationale: str` — human-readable explanation.
- `posture_transition: PostureTransition | None` — what the posture machine should do next.

No I/O. No clocks. Same input → same output, every time.

## Posture state machine (Phase 3)

A posture is the current operational mode. Transitions are pure value-in-value-out functions; no hidden state.

Postures (planned, subject to refinement against the TypeScript reference):

| Posture | Meaning |
|---|---|
| `INTERACTIVE` | Operator is at the keyboard; ambiguous calls escalate to a prompt. |
| `AUTONOMOUS` | No operator in the loop; ambiguous calls fail closed. |
| `DRY_RUN` | Classification only; no `WRITE`/`NETWORK`/`EXECUTE`/`SPAWN`/`DESTRUCTIVE` effects fire. |
| `LOCKED` | Refuse everything except explicitly allow-listed read-only calls. |

Transitions are total — every `(posture, decision)` pair has a defined next posture or a `PostureError`. There are no implicit transitions.

## Receipt (Phase 3)

A structured record of a single decision. Field ordering is deterministic; serialised receipts hash to identical bytes given identical inputs.

A receipt carries:

- The input tool call (as the manifest validated it).
- The classified effects and dominant class.
- The posture before and after.
- The decision (`allow`, `deny`, `escalate`).
- A content hash that uniquely identifies the receipt.

No timestamps. The hook layer attaches wall-clock time as out-of-band metadata; the receipt itself stays content-addressable.

## Hook (Phase 3)

A thin I/O wrapper. Reads a hook payload from stdin, runs the pipeline, writes a decision to stdout, exits 0 (allow) or non-zero (deny).

The hook is the only place in the package that touches `sys.stdin` or `sys.stdout`. Everything inside is pure.

```bash
# Phase 3 — wired into Claude Code as a PreToolUse hook
spine-lite hook < payload.json
echo $?  # 0 = allow, non-zero = deny
```

## CLI (Phase 3)

| Subcommand | Status | Purpose |
|---|---|---|
| `version` | Phase 1 — shipped | Print the installed version. |
| `validate-manifest` | Phase 2 | Validate a manifest file against the schema. |
| `classify` | Phase 2 | One-shot classification of a tool call. |
| `hook` | Phase 3 | stdin/stdout PreToolUse adapter for Claude Code. |

## See also

- [Concepts / Overview](overview.md) — pipeline shape.
- [How-To / Wire into Claude Code](../how-to/wire-claude-code.md) — operator runbook.
- [Explanation / Porting Notes](../explanation/porting-notes.md) — how this maps to the TypeScript reference.
