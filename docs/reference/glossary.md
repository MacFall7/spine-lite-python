# Glossary

Vocabulary used throughout this project. Define a term once; link from everywhere.

## Classifier

The pure function that maps a tool call and a manifest to a `Decision`. Phase 2 module: [`spine_lite.classifier`](api.md). No I/O, no clocks, no randomness — same input produces the same output every time.

## Closed taxonomy

A set whose membership cannot be extended at runtime. The six-class effects taxonomy is closed: adding a seventh class is a project-level decision that requires updating the precedence ordering, the parity tests, and consumers that exhaustively match. Compare with capability bits or OAuth scopes, which are open at runtime.

## Decision

The output of the classifier (Phase 2) or the full pipeline (Phase 3). Carries the effect set, the dominant effect under [precedence](#precedence), the rationale, and (Phase 3) the resulting [posture transition](#posture). Encoded as a frozen, slotted, kw-only dataclass.

## Determinism

Same input → same output, every time. The runtime contract. The five pure modules (`effects`, `manifest`, `classifier`, `posture`, `receipt`) preserve it; `hook` and `cli` are the only places where wall-clock entropy enters, and only as input.

## Effect

A side-effect class produced by a tool call. One of six members of the closed taxonomy: `READ`, `WRITE`, `NETWORK`, `EXECUTE`, `SPAWN`, `DESTRUCTIVE`. See [Effects Taxonomy](../concepts/effects-taxonomy.md).

## Hook

A thin I/O wrapper around the pipeline. Reads a hook payload from stdin, runs the pure modules, writes a decision to stdout, exits 0 (allow) or non-zero (deny). Phase 3 module: [`spine_lite.hook`](api.md). The only place in the package that touches stdin/stdout.

## Manifest

The policy document for a tool. Declares the tool's name, signature, declared effects, and posture constraints. Validated as Pydantic v2 models. Phase 2 module: [`spine_lite.manifest`](api.md). Round-trips authored fixtures byte-for-byte after JSON normalisation.

## `most_restrictive`

The function that collapses any non-empty set of effects to the highest-precedence class under [`PRECEDENCE`](#precedence). Pure, total over non-empty inputs; raises `ValueError` on empty input. Phase 1 — shipped.

## Phase

A planned milestone delineated by an exit gate. spine-lite ships in three phases:

- **Phase 1** — scaffold + taxonomy + exceptions (shipped at `v0.1.0a0`).
- **Phase 2** — manifest + classifier (target `v0.2.0a0`).
- **Phase 3** — posture + receipt + hook + full CLI (target `v0.3.0a0`).

A phase exits only when every item on its exit gate is verified. Gates and exit receipts live in [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md).

## Posture

The current operational mode. Drives how the runtime treats ambiguous calls. Phase 3 enum (planned members):

- `INTERACTIVE` — operator at the keyboard; ambiguous calls escalate.
- `AUTONOMOUS` — no operator; ambiguous calls fail closed.
- `DRY_RUN` — classification only; non-`READ` effects don't fire.
- `LOCKED` — refuse everything except explicit allow-listed read-only calls.

Transitions are pure value-in-value-out functions.

## Precedence

The fixed ordering over [Effect](#effect) members, from most restrictive to least:

```
DESTRUCTIVE > SPAWN > EXECUTE > NETWORK > WRITE > READ
```

Encoded once in [`spine_lite.PRECEDENCE`](api.md). Every dominance comparison resolves through it. Reordering is a project-level decision.

## PreToolUse hook

The Claude Code hook contract. A subprocess registered in the user's settings, invoked before every LLM tool call. Reads a JSON payload on stdin, returns a JSON decision on stdout, signals allow/deny by exit code. spine-lite's adapter is `spine-lite hook` (Phase 3).

## Pure module

A module containing no I/O, no clocks, no randomness, and no other source of hidden state. The five pure modules of spine-lite are `effects`, `manifest`, `classifier`, `posture`, `receipt`. Same input → same output, every time.

## Receipt

A structured record of a single decision. Field ordering is deterministic; receipts are content-addressable. Phase 3 module: [`spine_lite.receipt`](api.md). Two operators replaying the same session see byte-identical receipts.

## Run-registry

The append-only log of phase-day completion receipts. A repo-local copy lives at [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md); the operator mirrors entries to a canonical M87 run-registry on their side. Never edit prior entries.

## Tool call

A single invocation of a named tool with arguments, as the LLM has decided to make it. The input to the classifier. Distinct from a "tool definition" (which lives in the manifest) and a "tool invocation" (which is the actual execution that happens after the hook decides allow).

## See also

- [Concepts / Overview](../concepts/overview.md) — how the terms fit together.
- [Concepts / Effects Taxonomy](../concepts/effects-taxonomy.md) — the six classes in detail.
- [Reference / API](api.md) — programmatic surface.
