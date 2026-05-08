# Use the API

Practical patterns for the Phase 1 surface. Every snippet runs as-is against `v0.1.0a0`.

## Import what you need

The public surface lives at the package root. Anything not listed in `spine_lite.__all__` is private and may change without notice.

```python
from spine_lite import (
    Effect,
    PRECEDENCE,
    most_restrictive,
    SpineLiteError,
    ManifestError,
    ClassificationError,
    PostureError,
    HookError,
)
```

## Collapse an effect set

The most common operation: take a set of effects a tool can produce and reduce it to the single class that dominates.

```python
from spine_lite import Effect, most_restrictive

# Simple collapse
most_restrictive({Effect.READ, Effect.WRITE})
# <Effect.WRITE: 'write'>

# Across the whole taxonomy
most_restrictive(set(Effect))
# <Effect.DESTRUCTIVE: 'destructive'>
```

`most_restrictive` accepts any iterable: `set`, `frozenset`, `list`, generator. Duplicates and ordering are irrelevant.

```python
most_restrictive([Effect.NETWORK, Effect.NETWORK, Effect.READ])
# <Effect.NETWORK: 'network'>

most_restrictive(e for e in [Effect.WRITE, Effect.EXECUTE])
# <Effect.EXECUTE: 'execute'>
```

Empty input raises `ValueError` — the function is total over non-empty subsets only.

```python
try:
    most_restrictive(set())
except ValueError as exc:
    print(exc)
# effects must be non-empty
```

## Compare effect dominance

When you need the position rather than the result:

```python
from spine_lite import Effect, PRECEDENCE

def dominates(a: Effect, b: Effect) -> bool:
    """Return True if `a` is at least as restrictive as `b`."""
    return PRECEDENCE.index(a) <= PRECEDENCE.index(b)

dominates(Effect.NETWORK, Effect.READ)
# True

dominates(Effect.READ, Effect.NETWORK)
# False

dominates(Effect.WRITE, Effect.WRITE)
# True
```

## Catch errors

Every error from this package descends from `SpineLiteError`. Use the base for blanket handling, or pick a subclass when you need to react differently per failure mode.

```python
from spine_lite import SpineLiteError, ManifestError, ClassificationError

def process(payload: dict) -> str:
    try:
        return validate_and_classify(payload)
    except ManifestError as exc:
        return f"manifest invalid: {exc}"
    except ClassificationError as exc:
        return f"could not classify: {exc}"
    except SpineLiteError as exc:
        # Catch-all for anything else from this package
        return f"spine-lite error: {exc}"
```

The hierarchy is closed in spirit — adding new exception classes is permitted, but every new class descends from `SpineLiteError`. Catching the base is always safe.

## String coercion

`Effect` is a `StrEnum`, so members compare equal to their lowercase string values:

```python
Effect.READ == "read"       # True
Effect.NETWORK == "network" # True
str(Effect.WRITE)           # "write"
```

This is useful when serialising to JSON or logging; you don't need a custom encoder.

```python
import json

decision_summary = {
    "dominant": Effect.NETWORK,
    "all_effects": [Effect.READ, Effect.NETWORK],
}
json.dumps(decision_summary, default=str)
# '{"dominant": "network", "all_effects": ["read", "network"]}'
```

## Anti-patterns

- **Don't** define your own ordering of `Effect`. Use `PRECEDENCE`. There is one canonical ordering and every comparison should resolve through it.
- **Don't** add a seventh `Effect` member at runtime. The taxonomy is closed; subclassing or monkey-patching `Effect` will break the closed-taxonomy invariant tests.
- **Don't** catch bare `Exception`. Use `SpineLiteError` if you mean "any error from this package" and a specific subclass otherwise.
- **Don't** rely on stringly-typed effect names from outside the runtime. Convert to `Effect` at the boundary so a typo fails on import, not on first use.

## See also

- [Effects Taxonomy](../concepts/effects-taxonomy.md) — what each class means.
- [Reference / API](../reference/api.md) — auto-generated reference.
- [Reference / Exceptions](../reference/exceptions.md) — full error catalog.
- [Reference / Glossary](../reference/glossary.md) — vocabulary.
