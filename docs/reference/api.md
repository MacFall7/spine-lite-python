# API Reference

The public surface is exactly what is exported from `spine_lite.__all__`. Everything else is private and subject to change without notice.

## Top-level

The package root re-exports the surface so callers don't have to navigate submodules:

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
    __version__,
)
```

## Effects

::: spine_lite.effects
    options:
      members:
        - Effect
        - PRECEDENCE
        - most_restrictive

## Exceptions

::: spine_lite.exceptions
    options:
      members:
        - SpineLiteError
        - ManifestError
        - ClassificationError
        - PostureError
        - HookError

## Posture

::: spine_lite.posture
    options:
      members:
        - Posture

## Phase 2 / Phase 3 modules

Stubs and partials with phase-pinning docstrings. The reference expands as implementations land.

::: spine_lite.manifest

::: spine_lite.classifier

::: spine_lite.receipt

::: spine_lite.hook

## CLI module

::: spine_lite.cli
    options:
      members:
        - app
        - version

## See also

- [How-To / Use the API](../how-to/use-the-api.md) — practical patterns.
- [Reference / CLI](cli.md) — subcommand reference.
- [Reference / Exceptions](exceptions.md) — error catalog.
- [Reference / Glossary](glossary.md) — vocabulary.
