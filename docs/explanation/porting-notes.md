# Porting Notes

A log of design decisions made in this repository and any intentional divergences from earlier-stated specs. Append-only. When two implementations of related ideas look different, the entry on this page explains why.

## Sibling project

The repository [MacFall7/M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite) is a Python governance framework that addresses a related but different problem: deterministic classification of Claude Code shell commands. Its taxonomy is six classes drawn on the shell-vs-file axis (`SAFE_READ`, `SHELL_SAFE`, `SHELL_MUTATING`, `SCOPED_WRITE`, `RESTRICTED_WRITE`, `SHELL_DANGEROUS`) with numeric risk-delta scores and a five-step ordered match pipeline (deny list → network egress → safe → mutating → fail-closed default).

`spine-lite-python` is a sibling implementation, not a port. Its taxonomy is six classes drawn on the **state × boundary × reversibility** axes (`READ`, `WRITE`, `NETWORK`, `EXECUTE`, `SPAWN`, `DESTRUCTIVE`) with **ordinal precedence** and a `most_restrictive` collapse function. It is designed to classify any LLM tool call, not only bash commands.

The two taxonomies are categorically different — neither maps cleanly onto the other:

- The sibling distinguishes `SAFE_READ` (file read) from `SHELL_SAFE` (read-only shell command); `spine-lite-python` collapses both into `READ`/`EXECUTE` based on whether a subprocess was invoked.
- `spine-lite-python` carves out `NETWORK` as its own class; the sibling rolls outbound network calls into `SHELL_DANGEROUS` via the deny-list step.
- The sibling encodes risk numerically (0.00 to 0.10); `spine-lite-python` encodes dominance ordinally and resolves through `PRECEDENCE`.
- `spine-lite-python`'s invariants in [`CLAUDE.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CLAUDE.md) are about implementation discipline (purity, type strictness, public API gates); the sibling's invariants are about governance philosophy (separation of proposal from execution, model interchangeability, narrative-vs-runtime separation).

Both designs are coherent for their respective scopes. `spine-lite-python`'s scope is broader (any tool call, not just bash) and its invariants are canonical for this repository.

## Phase 2 opening — 2026-05-08

This entry records the §9 halt that opened Phase 2 and its resolution.

### The halt

Probed the sibling repository for the manifest schema and classifier logic referenced as the "TS reference" by the original blueprint. Findings:

1. The sibling repository is publicly accessible and is implemented in **Python**, not TypeScript. The blueprint's "TS reference" framing is stale.
2. Its six-class taxonomy is **categorically different** from what shipped in Phase 1. The taxonomies are not relabelings of each other; they draw axes on different dimensions.
3. Phase 1 had already shipped `v0.1.0a0` under `spine-lite-python`'s action-centric taxonomy with operator sign-off. Re-aligning to the sibling's taxonomy would invalidate the public release and rewrite the docs site.

### The decision

Phase 2 proceeds with `spine-lite-python` as canonical:

- **Sibling project is informational.** Citable in this file but not a parity target. Parity tests in Phase 2 round-trip authored fixtures with byte-stability invariants; they do not cross-check against external fixtures.
- **Posture enum lands in Phase 2.** One-line `__all__` extension so the manifest schema can validate posture constraints against a closed enum. Members and string values are pinned by [`docs/concepts/posture-and-hooks.md`](../concepts/posture-and-hooks.md): `INTERACTIVE`, `AUTONOMOUS`, `DRY_RUN`, `LOCKED`.
- **Blueprint corrections.** `CLAUDE.md` rewords the mission to drop the "TS reference" framing. This page reframes from "translation log" to "design history."

### Recorded in the run-registry

The §9 halt and this resolution are mirrored in [`RECEIPTS.md`](https://github.com/MacFall7/spine-lite-python/blob/main/RECEIPTS.md) as the Phase 2 Day 1 opening entry.

## Phase 1 — 2026-05-08

The closed six-class effects taxonomy and precedence ordering were authored from the architectural invariants in `CLAUDE.md`. The local pre-staged scaffold referenced in the original migration brief did not exist, so the entire Phase 1 scaffold was authored from spec.

The taxonomy `READ / WRITE / NETWORK / EXECUTE / SPAWN / DESTRUCTIVE` and the precedence ordering `DESTRUCTIVE > SPAWN > EXECUTE > NETWORK > WRITE > READ` are `spine-lite-python`'s spec, not derived from any external repository.

### Idiomatic translations recorded for the archive

Even though this isn't a port, the language and library choices are worth pinning:

- **`from __future__ import annotations`** at the top of every module. PEP 563 stringified annotations + `if TYPE_CHECKING:` guards for cycle-prone imports.
- **Frozen, slotted, kw-only dataclasses** for value types. `@dataclass(frozen=True, slots=True, kw_only=True)`.
- **`StrEnum`** for closed enumerations. `Effect(StrEnum)` and (Phase 2) `Posture(StrEnum)`.
- **Pydantic v2** for the manifest schema. Fast Rust-backed validation, JSON round-trip, `model_config = ConfigDict(frozen=True, extra="forbid")` for immutability and strictness.

## Records

Once a design decision or divergence is settled, it stays in this file forever. Don't delete entries when implementations evolve — annotate them with the convergence date instead. The archive is the value.

## See also

- [Architecture](architecture.md) — the design this repository follows.
- [Invariants](invariants.md) — the rules nothing in this repo gets to break.
- Sibling project: [MacFall7/M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite).
