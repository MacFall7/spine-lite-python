# Overview

The mental model in one page.

## The pipeline

```
tool call ──┐
            │
manifest ───┼──► classifier ──► effect set ──► most_restrictive ──► dominant effect
            │                        │                                    │
posture ────┘                        │                                    │
                                     ▼                                    ▼
                                  posture transition ─────────────► decision
                                                                     │
                                                                     ▼
                                                                   receipt
                                                                     │
                                                                     ▼
                                                                  hook ──► allow / deny
```

You give the runtime three inputs:

- A **tool call** — the LLM has decided to invoke a named tool with arguments.
- A **manifest** — the policy document for that tool, including its declared effects and any posture constraints.
- A **posture** — the current operational state (e.g., interactive vs. autonomous, dry-run vs. live).

The runtime returns a single output: a **decision** carrying the dominant effect, the full effect set, the new posture, and a receipt that hashes to the same value if you re-run with the same inputs.

The PreToolUse **hook** is just an I/O wrapper that maps stdin/stdout to and from the pure pipeline above.

## What's pure

`effects`, `manifest`, `classifier`, `posture`, and `receipt` are pure modules. No clocks, no randomness, no network, no filesystem. Same input → same output, every time. This is what makes a receipt replayable by SHA — there's no hidden state to drift.

`hook` and `cli` do I/O, because something has to. They're thin adapters around the pure core.

## What's closed

The effects taxonomy is closed at six classes. Adding a class is a project-level decision that requires updating the precedence ordering, the parity tests against the TypeScript reference, and the docstrings. It is not a runtime extension point.

This is a feature, not a limitation. A taxonomy that grows at runtime is a taxonomy that drifts. The six classes were chosen to cover every observable side effect a tool call can produce. If something looks like a seventh class, it's probably an existing class with new arguments.

## What's deterministic

Same tool call + same manifest + same posture → same decision + same receipt bytes. No "the timestamp differs" caveats; the receipt doesn't carry a timestamp. The hook layer is where wall-clock entropy enters, and only as input — it doesn't influence classification.

## What's offline

Zero network calls inside the runtime. Zero LLM calls inside the runtime. The runtime's job is to look at a tool call and decide; if you want to call a model to second-guess it, that's a separate concern that lives outside this package.

## Phase boundaries

| Phase | Modules complete | What you can do |
|---|---|---|
| 1 | `effects`, `exceptions`, `cli` (`version`) | Collapse effect sets, raise/catch typed errors, ship as a package. |
| 2 | `+ manifest`, `classifier` | Classify a tool call against a manifest, get a `Decision`. |
| 3 | `+ posture`, `receipt`, `hook`, `cli` (full) | End-to-end PreToolUse integration with Claude Code. |

The architecture stays the same across phases. Each phase fills in pure modules that adhere to the same purity contract.

## Where to go next

- [Effects Taxonomy](effects-taxonomy.md) — the six classes and their precedence.
- [Posture and Hooks](posture-and-hooks.md) — the Phase 2/3 components in outline.
- [Architecture](../explanation/architecture.md) — why the modules are split this way.
- [Invariants](../explanation/invariants.md) — the rules nothing in this repo gets to break.
