# Security

## Reporting a vulnerability

Email `security@m87.studio` with details. Don't open a public issue for a vulnerability; security issues stay private until a fix is shipped and disclosed.

Include in the report:

- A description of the vulnerability and its impact.
- Steps to reproduce, ideally with a minimal example.
- The version(s) affected (commit SHA is fine).
- Your preferred disclosure timeline (the default is 90 days).

Expect an acknowledgement within 5 business days. We'll coordinate disclosure and CVE assignment if applicable.

## Supported versions

Alpha. Phase 1 is the only shipped version.

| Version | Status | Security fixes |
|---------|--------|----------------|
| `0.1.0aN` (Phase 1) | Current | Yes |
| `0.2.0aN` (Phase 2) | Pending | Will be supported when shipped |
| `0.3.0aN` (Phase 3) | Pending | Will be supported when shipped |

Once `v1.0.0` ships, we support the latest two minor lines (`v1.N` and `v1.N-1`) for security fixes.

## Trust model

The runtime is deterministic and offline. It contains:

- No LLM calls.
- No network calls.
- No filesystem access in the pure modules.
- No subprocess invocation in the pure modules.

Trust questions live entirely in your **manifest**. The manifest declares which tools the LLM can invoke, what effects each tool produces, and which postures permit which calls. If your manifest is wrong, the runtime will faithfully classify a wrong call as a wrong call — the runtime is not the safety net for a bad manifest.

### What the hook does and doesn't do

When `v0.3.0a0` ships:

- `spine-lite hook` reads stdin, classifies, decides, writes stdout. It does not execute the tool itself; that's Claude Code's job.
- An exit code of 0 from the hook is a permission, not an action. Whether the tool actually runs is the host's decision.
- A non-zero exit deny is final on the host's side. spine-lite has no way to override its own deny.

### What you trust the runtime for

- Correctly classifying a tool call against a manifest.
- Producing a deterministic, content-addressable receipt.
- Never silently widening permissions (e.g. classifying a `WRITE` as a `READ`).

### What you don't trust the runtime for

- Validating that the tool itself behaves as the manifest claims. The manifest is a contract, not a proof.
- Sandboxing the tool's execution. The hook decides; the host enforces.
- Detecting model jailbreaks or prompt injection. That's a separate layer.

### Threat model

In scope:

- A misconfigured manifest that leaks more permission than intended.
- A tool call that classifies differently in TypeScript and Python (parity bug).
- A receipt that doesn't reproduce on replay (determinism bug).
- A path-handling bug on Windows that doesn't surface on Linux.

Out of scope:

- Adversarial LLM output that the manifest does not constrain.
- Compromise of the operator's machine (the hook reads files; if those files are tampered with, classification follows the tampered input).
- Side-channel attacks via posture transitions in shared environments.

## Dependencies

We run `pip-audit` (manually for now, automated in CI for Phase 2+) against the `uv.lock` and respond to CVEs in dependencies within 30 days. The dependency surface is intentionally small: `pydantic`, `typer`, and the dev/docs tooling.

## Cryptographic guarantees

Receipts are content-addressable via `hashlib.sha256` (Phase 3). Two receipts with the same SHA-256 represent the same decision over the same inputs. We rely on the standard-library implementation; no custom crypto.

## Disclosure history

None yet.

## See also

- [Explanation / Invariants](docs/explanation/invariants.md) — what the runtime guarantees.
- [Explanation / FAQ](docs/explanation/faq.md) — common questions about the design.
- [How-To / Wire into Claude Code](docs/how-to/wire-claude-code.md) — the hook contract.
