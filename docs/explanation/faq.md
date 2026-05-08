# FAQ

## Why six effect classes?

Six lines that matter for safety review. `READ` vs. `WRITE` (did anything change?), `WRITE` vs. `NETWORK` (did anything cross a trust boundary?), `NETWORK` vs. `EXECUTE` (did we hand control to another process?), `EXECUTE` vs. `SPAWN` (did the child outlive the call?), `SPAWN` vs. `DESTRUCTIVE` (can we undo it?). Anything finer is manifest territory.

## Why is the taxonomy closed?

A taxonomy that grows at runtime is a taxonomy that drifts. Adding a class would require updating the precedence ordering, the parity tests against the TypeScript reference, every consumer that exhaustively matches on `Effect`, and every receipt that hashed under the old ordering. The cost is real; the benefit (better fit for one new use case) is local. So: closed by default, with an explicit project-level process for extension.

## Why no LLM calls inside the runtime?

The runtime's job is to classify and decide. Calling a model to second-guess that decision turns the hook into a non-deterministic component, which breaks receipt replayability, which breaks the audit story. If you want a model in the loop, run it outside the hook and feed its decision in as part of the manifest or posture configuration.

## Why deterministic?

Receipts are content-addressable. Two operators replaying the same session see byte-identical receipts. That property only holds if the runtime is deterministic — same input → same output, every time. The cost is that wall-clock time can only enter at the I/O boundary (the hook); the benefit is that "what happened?" has a SHA-stable answer.

## Why Python after TypeScript?

The TypeScript reference is the spec. The Python port is what you install in environments where Python is already the language of choice — Claude Code agents written in Python, internal CLIs, CI pipelines, Jupyter sessions. Both implementations target the same observable behaviour.

## Why Pydantic v2 for the manifest?

Pydantic v2 is the de facto standard for typed Python schemas, has fast Rust-backed validation, and round-trips JSON cleanly. The TypeScript reference uses Zod; Pydantic v2 is the closest match in the Python ecosystem.

## What happens when a tool call has no declared effects?

`ManifestError`. Tools without declared effects can't be classified, and an unclassified call is a refused call. The manifest is the contract; declare the effects explicitly.

## What happens when a manifest declares an effect outside the closed taxonomy?

`ManifestError` at validation time. Unknown effect strings fail Pydantic validation; the call doesn't reach the classifier.

## Will it work without Claude Code?

Yes. The `hook` adapter implements the Claude Code PreToolUse contract specifically, but the underlying pipeline is just a function from inputs to a `Decision`. Wire it into any process that can invoke a subprocess and parse JSON.

## Can I extend the posture state machine?

Posture members live in the closed `Posture` enum (Phase 3). Adding a member is an additive change that needs project-level sign-off, similar to `Effect`. The transition function itself is pure — defining new transitions for existing postures is a code change in `posture.py` and a parity test update.

## How do I report a security issue?

See [SECURITY.md](https://github.com/MacFall7/spine-lite-python/blob/main/SECURITY.md). Don't open a public issue for a vulnerability.

## Why is there no `dataclass(frozen=True, slots=True, kw_only=True)` in Phase 1?

Phase 1 ships only the taxonomy, the exception hierarchy, and a CLI. None of those need a dataclass. Phase 2 introduces the manifest and decision types where the dataclass discipline applies.

## Why isn't the lockfile auto-generated in CI?

The lockfile (`uv.lock`) is committed to the repo. CI uses it directly. See [Design Rationale / `uv.lock` is committed](design-rationale.md). Refresh with `uv lock --upgrade` and commit the result.

## Why no `Any` anywhere?

Strict typing catches more bugs than it costs. The codebase has zero `Any` today; the constraint forces you to model the data clearly rather than waving at it. If a third-party stub forces an `Any`, justify it with an inline comment.

## Why a 150-line CLAUDE.md cap?

Repo-level governance files want to be read in one sitting. A 150-line cap forces priorities; everything else lives in `docs/`.

## Where do I propose a change to the public API?

Open an issue with a written rationale. Wait for a HALT-format response from the project lead. PRs that modify `__all__` without prior agreement will be closed back to the issue.

## Where do receipts go?

Phase 3 will add `--receipt-dir` to `spine-lite hook`. Each receipt is a content-addressable file; same inputs produce identical bytes. Capture them somewhere durable for audit.

## See also

- [Architecture](architecture.md) — the overall shape.
- [Invariants](invariants.md) — the rules.
- [Design Rationale](design-rationale.md) — past decisions.
- [Glossary](../reference/glossary.md) — vocabulary.
