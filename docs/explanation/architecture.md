# Architecture

## Mission

Classify and decide on every LLM tool call before it runs. Pure, deterministic, byte-for-byte reproducible. Wire into Claude Code as a PreToolUse hook; carry the same semantics anywhere else a hook contract exists.

## The runtime in one diagram

```
                     ┌──────────────────────────────────────────────┐
                     │               pure pipeline                  │
                     │                                              │
   stdin payload ──► │  manifest ──► classifier ──► posture machine │ ──► stdout decision
                     │     │              │              │          │
                     │     ▼              ▼              ▼          │
                     │  ManifestError  Classification-  Posture-    │
                     │                 Error            Error       │
                     │                                              │
                     │              receipt (deterministic bytes)   │
                     └──────────────────────────────────────────────┘
   exit 0 = allow                       │
   exit n = deny                        ▼
                                  receipt directory (optional)
```

The hook is a thin I/O wrapper. Everything inside is pure: no clocks, no randomness, no network, no filesystem. Same input → same output, every time.

## Module map

| Module | Responsibility | Pure | Phase |
| --- | --- | --- | --- |
| `effects` | Closed six-class taxonomy + precedence + `most_restrictive` | yes | 1 ✓ |
| `exceptions` | Hierarchy rooted at `SpineLiteError` | yes | 1 ✓ |
| `manifest` | Tool-definition schema (Pydantic v2) | yes | 2 |
| `classifier` | Tool call → effect set → `Decision` | yes | 2 |
| `posture` | Posture state machine | yes | 3 |
| `receipt` | Structured, deterministic decision records | yes | 3 |
| `hook` | Claude Code PreToolUse stdin/stdout adapter | I/O | 3 |
| `cli` | Operator interface (Typer) | I/O | 1 (`version`) → 3 (full) |

The five pure modules contain no clocks, no randomness, no network, no filesystem. Determinism is the contract.

## Why the pure / I/O split

Determinism only holds if there's exactly one boundary where wall-clock entropy enters. Everything else has to be pure. The hook is that boundary; the CLI is that boundary; nothing else is.

This is what makes a receipt content-addressable. A receipt that hashed differently every time you ran it would be useless for replay; the only way to get byte-stability is to keep the hot path free of timestamps, UUIDs, and randomness. The cost is one extra layer of indirection (the hook); the benefit is replayability by SHA forever.

## Why a closed taxonomy

A taxonomy that grows at runtime is a taxonomy that drifts. The six classes were chosen to draw the lines that matter for safety review:

- `READ` vs. `WRITE`: did anything change?
- `WRITE` vs. `NETWORK`: did anything cross a trust boundary?
- `NETWORK` vs. `EXECUTE`: did we hand control to another process?
- `EXECUTE` vs. `SPAWN`: did the child outlive the call?
- `SPAWN` vs. `DESTRUCTIVE`: can we undo it?

Anything finer is a manifest concern, not a taxonomy concern. If something feels like a seventh class, it's almost always an existing class with manifest-level qualifiers — *which* file the WRITE touched, *which* host the NETWORK call hit.

Adding a class is permitted but expensive. The process is in [Effects Taxonomy / Why closed](../concepts/effects-taxonomy.md#why-closed) and triggers a HALT to the project lead.

## Phase plan

| Phase | Modules | Version | What you can do |
|---|---|---|---|
| 1 (shipped) | `effects`, `exceptions`, `cli` (`version`) | `v0.1.0a0` | Collapse effect sets, raise/catch typed errors, ship as a package. |
| 2 | `+ manifest`, `classifier` | `v0.2.0a0` | Classify a tool call against a manifest, get a `Decision`. |
| 3 | `+ posture`, `receipt`, `hook`, `cli` (full) | `v0.3.0a0` | End-to-end PreToolUse integration with Claude Code. |

The architecture stays the same across phases. Each phase fills in pure modules that adhere to the same purity contract.

## Reference implementation

The TypeScript reference lives at [MacFall7/M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite). Treat it as the spec for semantic behaviour. Where Python idiom diverges from TypeScript (typing, dataclass shape, exception names), prefer the Python form and document the call in [Porting Notes](porting-notes.md). Anything that changes observable behaviour is a divergence and needs project-level sign-off.

## See also

- [Invariants](invariants.md) — the rules nothing in this repo gets to break.
- [Design Rationale](design-rationale.md) — past decisions, with reasoning.
- [Porting Notes](porting-notes.md) — TypeScript-to-Python translation log.
- [FAQ](faq.md) — common questions about the design.
