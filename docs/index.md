# spine-lite

Deterministic policy and effects runtime for LLM tool calls.

Six-class effects taxonomy on state × boundary × reversibility axes. Ordinal precedence. Content-addressable receipts. Designed for any LLM tool call, not just bash. Sibling project to [M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite) — see [Porting Notes](explanation/porting-notes.md) for the relationship.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](reference/api.md){ .md-button }

## What it does

You hand it a tool call and a manifest of declared effects. It hands back a deterministic decision: which effects fire, what the dominant class is, and a structured receipt you can replay by SHA. Wire it in front of Claude Code's tool-use as a PreToolUse hook, or call the library directly from any Python process.

The runtime is offline by design — no clocks, no randomness, no network, no LLM calls inside the runtime itself.

## Status

| Phase | Scope | Version | State |
|-------|-------|---------|-------|
| 1 | Scaffold, taxonomy, exceptions, CLI surface, CI matrix, docs | `v0.1.0a0` | Shipped |
| 2 | Manifest schema, classifier with parity tests | `v0.2.0a0` | Pending |
| 3 | Posture state machine, receipts, hook adapter, end-to-end | `v0.3.0a0` | Pending |

PyPI publish lands at the end of Phase 3. Until then, install from source — see [Getting Started](getting-started.md).

## Where to go

- New here? → [Getting Started](getting-started.md)
- Mental model → [Concepts / Overview](concepts/overview.md)
- The six effect classes → [Effects Taxonomy](concepts/effects-taxonomy.md)
- Use the API today → [How-To / Use the API](how-to/use-the-api.md)
- Wire into Claude Code → [How-To / Wire into Claude Code](how-to/wire-claude-code.md)
- Public surface → [Reference / API](reference/api.md), [Reference / CLI](reference/cli.md), [Reference / Glossary](reference/glossary.md)
- Why it's shaped this way → [Explanation / Architecture](explanation/architecture.md), [Invariants](explanation/invariants.md), [Design Rationale](explanation/design-rationale.md), [FAQ](explanation/faq.md)
- What shipped when → [History / Phase 1](history/phase-1.md)

## License

MIT. Maintained by Mac McFall under M87 Studio.
