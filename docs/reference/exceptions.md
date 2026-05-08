# Exceptions

Every error this package raises descends from `SpineLiteError`. The hierarchy is closed in spirit — adding new classes is permitted, but every new class descends from the base.

## Hierarchy

```
Exception
└── SpineLiteError
    ├── ManifestError
    ├── ClassificationError
    ├── PostureError
    └── HookError
```

## Catalog

### `SpineLiteError`

Base class for every error raised by the package. Catch this for blanket handling:

```python
from spine_lite import SpineLiteError

try:
    do_spine_lite_things()
except SpineLiteError as exc:
    log.error("spine-lite failure: %s", exc)
```

`SpineLiteError` is never raised directly by the runtime — only its subclasses.

### `ManifestError`

Raised when a tool manifest is malformed or fails validation. Sources:

- Manifest file is not parseable (TOML/JSON syntax error).
- Manifest schema validation fails (unknown fields with `--strict`, type mismatch, missing required field).
- Tool referenced in a call is not declared in the manifest.
- Manifest declares an effect outside the closed taxonomy.

```python
from spine_lite import ManifestError

raise ManifestError("tool 'shell_run' not declared in manifest")
```

### `ClassificationError`

Raised when a tool call cannot be classified against an otherwise-valid manifest. Sources:

- Tool call references arguments the manifest doesn't know about and cannot infer.
- Manifest's posture constraints conflict with the call's declared metadata.
- Internal classifier invariant violation (rare; indicates a bug).

```python
from spine_lite import ClassificationError

raise ClassificationError("ambiguous effect set for shell_run with no command")
```

### `PostureError`

Raised on illegal posture transitions or invalid posture state. Sources:

- Tool call attempts a transition not defined in the posture state machine.
- Configured posture is not a member of the `Posture` enum.
- Posture-required confirmation was not provided.

```python
from spine_lite import PostureError

raise PostureError("DESTRUCTIVE call refused under posture LOCKED")
```

### `HookError`

Raised when the PreToolUse hook protocol is violated. Sources:

- Stdin payload is not valid JSON.
- Stdin payload is missing required fields.
- Hook output cannot be serialised (should be impossible; indicates a bug).
- Hook timeout exceeded.

```python
from spine_lite import HookError

raise HookError("stdin payload missing 'tool' field")
```

## Anti-patterns

- **Don't catch bare `Exception`** when you mean "any error from this package." Use `SpineLiteError`.
- **Don't catch `SpineLiteError`** when you mean a specific failure mode. Use the subclass; let unexpected errors propagate.
- **Don't raise `SpineLiteError` directly.** Pick the subclass that matches the failure mode, or add a new subclass if none fits.
- **Don't catch and re-raise without context.** If you wrap an exception, use `raise ManifestError("...") from original_exc` so the chain is preserved.

## Adding a new exception class

Adding a new subclass of `SpineLiteError` does not require project-level sign-off — it's an additive change. But:

1. Every new class descends from `SpineLiteError`. No exceptions.
2. Add a docstring on the new class explaining when it's raised.
3. Add the class to `src/spine_lite/exceptions.py`.
4. Add the class to `__all__` in `src/spine_lite/__init__.py` if you want it in the public surface.
5. Add a test that the class is catchable via the base.
6. Document the class on this page.

## See also

- [Reference / API](api.md) — auto-generated reference for `spine_lite.exceptions`.
- [How-To / Use the API](../how-to/use-the-api.md#catch-errors) — catching patterns.
- [Concepts / Overview](../concepts/overview.md) — where each error type fits in the pipeline.
