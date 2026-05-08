# Architecture

## Mission

Classify and decide on every LLM tool call before it runs. Pure, deterministic, byte-for-byte reproducible. Wire into Claude Code as a PreToolUse hook; carry the same semantics anywhere else a hook contract exists.

## Effects taxonomy

A closed six-class set:

| Effect | Meaning |
| --- | --- |
| `READ` | observation only |
| `WRITE` | persistent state change to caller-owned storage |
| `NETWORK` | outbound network call |
| `EXECUTE` | subprocess invocation |
| `SPAWN` | fork-and-detach subprocess |
| `DESTRUCTIVE` | irreversible state change |

Ordered by precedence: `DESTRUCTIVE > SPAWN > EXECUTE > NETWORK > WRITE > READ`. `spine_lite.most_restrictive()` collapses any non-empty set to the highest class.

Why closed? Stable semantics. A taxonomy that grows at runtime is a taxonomy that drifts. Adding a class is a project-level decision that requires updating the precedence ordering and the parity tests against the TypeScript reference.

## Module map

| Module | Responsibility | Pure |
| --- | --- | --- |
| `effects` | Closed taxonomy + precedence + collapse | yes |
| `manifest` | Tool-definition schema (pydantic v2) | yes |
| `classifier` | Tool call → effect set → decision | yes |
| `posture` | Posture state machine (transitions) | yes |
| `receipt` | Structured decision records | yes |
| `hook` | Claude Code PreToolUse adapter | I/O |
| `cli` | Operator interface (Typer) | I/O |
| `exceptions` | Hierarchy rooted at `SpineLiteError` | yes |

The five pure modules contain no clocks, no randomness, no network, no filesystem. Determinism is the contract: same input, same output, every time.

## Phase plan

- **Phase 1** — scaffold, CI matrix, docs deploy. `v0.1.0a0`.
- **Phase 2** — `manifest` and `classifier` complete. Pydantic v2 models, parity tests against TypeScript reference fixtures, hypothesis invariants. `v0.2.0a0`.
- **Phase 3** — `posture`, `receipt`, `hook`, `cli` complete. End-to-end PreToolUse integration, fixture-driven smoke test against a mocked Claude Code session. `v0.3.0a0`.

## Reference implementation

The TypeScript reference lives at [MacFall7/M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite). Treat it as the spec for semantic behaviour. Where Python idiom diverges from TypeScript (typing, dataclass shape, exception names), prefer the Python form and document the call in [Porting Notes](porting-notes.md). Anything that changes observable behaviour is a divergence and needs project-level sign-off.
