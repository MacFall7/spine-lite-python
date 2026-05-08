# Porting Notes

Translation log between the TypeScript reference and this Python port. One entry per intentional divergence. When the two implementations look different, the entry on this page explains why.

## Conventions

- **Spec form.** The TypeScript reference defines semantics. The Python form must produce equivalent observable behaviour given equivalent input.
- **Idiomatic translation.** Wherever Python idiom (enums, dataclasses, exceptions, typing) reads better, prefer the Python form. Document the choice here.
- **Divergence.** Anything that changes observable behaviour is a divergence and requires project-level sign-off before merge.

## Phase 1 (shipped at `v0.1.0a0`, 2026-05-08)

No semantic divergences. The closed effects taxonomy and precedence ordering mirror the TypeScript reference exactly. `most_restrictive` matches `mostRestrictive` byte-for-byte on equivalent inputs.

### Mechanical naming differences

| TypeScript | Python | Reason |
| --- | --- | --- |
| `mostRestrictive` | `most_restrictive` | snake_case is canonical Python. |
| `Effect` (string union) | `Effect(StrEnum)` | Python doesn't have string-literal unions. `StrEnum` (3.11+) gives the same observable behaviour with a typed handle. |
| `PRECEDENCE` (readonly array) | `PRECEDENCE` (`tuple[Effect, ...]`) | Tuples are immutable by construction. `tuple[Effect, ...]` is the typed-Python equivalent. |
| `SpineLiteError` (TS class) | `SpineLiteError` (Python class) | Same name, both ecosystems. |
| `ManifestError`, `ClassificationError`, `PostureError`, `HookError` | identical | Closed-in-spirit hierarchy in both ports. |

### Idiomatic translations

- **`from __future__ import annotations`** at the top of every module. The TypeScript reference uses ESM imports with explicit type-only imports; the Python equivalent is PEP 563 stringified annotations + `if TYPE_CHECKING:` guards.
- **Frozen, slotted, kw-only dataclasses** for value types. The TypeScript reference uses `readonly` fields on classes with explicit getters. The Python form is `@dataclass(frozen=True, slots=True, kw_only=True)`.
- **Pydantic v2** for the manifest schema (Phase 2). The TypeScript reference uses Zod. Both produce JSON-validating types with runtime checks.

## Phase 2 (planned)

Manifest and classifier. Expected sources of divergence:

- **JSON schema serialisation.** The TypeScript reference uses Zod's `safeParse` semantics. Pydantic v2 has different error message shapes and a different "additional fields" default. The parity test is round-trip on byte-equal JSON given identical inputs; error messages are not part of the parity contract.
- **Enum string handling.** TypeScript string unions accept arbitrary strings at runtime if narrowing is bypassed (e.g., via `as`). Python `StrEnum` raises `ValueError` on construction from an unknown string. The Python port treats this as a feature; the parity test covers it explicitly.
- **Schema field ordering.** TypeScript object-literal field order is insertion-order preserved; Pydantic v2 model_dump field order follows the model definition. Match the model definition order to the TS reference's struct order exactly.

## Phase 3 (planned)

Posture machine, receipts, hook. Expected sources of divergence:

- **Posture transition rejections.** TypeScript throws untyped `Error`; Python raises `PostureError`. Observable behaviour (rejection) is the same; the exception type is different. Document this as an idiomatic translation, not a divergence.
- **Receipt byte-stability.** Both ports must produce byte-identical receipts for byte-identical inputs. Field ordering, key sorting, and JSON encoding (especially Unicode) must match. The parity test is `sha256(ts_receipt) == sha256(py_receipt)` against fixture inputs.
- **Hook stdin/stdout protocol.** The Claude Code PreToolUse contract is the spec; both ports implement the same wire format.

## Records

Once a divergence is settled, it stays in this file forever. Don't delete entries when implementations converge — annotate them with the convergence date instead. The archive is the value.

## See also

- [Architecture](architecture.md) — the design both ports share.
- [Invariants](invariants.md) — the rules both ports must preserve.
- TypeScript reference: [MacFall7/M87-Spine-lite](https://github.com/MacFall7/M87-Spine-lite).
