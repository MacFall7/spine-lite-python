# Porting Notes

Translation log between the TypeScript reference and this port. One entry per intentional divergence. When the two implementations look different, the entry on this page explains why.

## Conventions

- **Spec form:** the TypeScript reference defines semantics. The Python form should produce equivalent observable behaviour given equivalent input.
- **Idiomatic translation:** wherever Python idiom (enums, dataclasses, exceptions, typing) reads better, prefer the Python form. Document the choice here.
- **Divergence:** anything that changes observable behaviour is a divergence and requires project-level sign-off before merge.

## Phase 1

No semantic divergences. The closed effects taxonomy and precedence ordering are mirrored exactly. `most_restrictive` matches the TypeScript reference's `mostRestrictive` byte-for-byte on equivalent inputs.

Mechanical naming differences:

| TypeScript | Python |
| --- | --- |
| `mostRestrictive` | `most_restrictive` |
| `Effect` (string union) | `Effect(StrEnum)` |
| `PRECEDENCE` (readonly array) | `PRECEDENCE` (`tuple[Effect, ...]`) |
| `SpineLiteError` (TS class) | `SpineLiteError` (Python class) |

## Phase 2 and beyond

Entries land here as they surface. Expected sources of divergence:

- **JSON schema serialisation.** The TypeScript reference uses Zod; this port uses Pydantic v2. Field ordering, error messages, and edge-case validation may differ. Round-trip parity (TS-emitted JSON → Python validation → re-serialise → byte-equality) is the test.
- **Enum string handling.** TypeScript string unions accept arbitrary string values at runtime if narrowing is bypassed; Python `StrEnum` raises `ValueError`. The Python port treats this as a feature.
- **Posture transition rejections.** TypeScript throws untyped `Error`; Python raises `PostureError`. Observable behaviour (rejection) is the same; the type is different.
