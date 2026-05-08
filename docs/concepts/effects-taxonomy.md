# Effects Taxonomy

The six classes, the precedence ordering, and the rules that make them stable.

## The six classes

| Class | Meaning | Examples |
|---|---|---|
| `READ` | Pure observation. No state change anywhere the caller can see. | reading a file, listing a directory, querying without writing |
| `WRITE` | Persistent state change to caller-owned storage. Reversible by the caller. | writing a file, updating a row, appending a log entry |
| `NETWORK` | Outbound network call. Crosses a trust boundary; result is observable to a third party. | HTTP request, DNS lookup, Slack message, webhook fire |
| `EXECUTE` | Subprocess invocation, no fork-and-detach. Caller waits for completion. | `subprocess.run`, `os.system`, shell pipeline |
| `SPAWN` | Subprocess invocation that may fork-and-detach. Caller does not necessarily wait. | `Popen` with no `wait`, daemon launch, `nohup`, container `run -d` |
| `DESTRUCTIVE` | Irreversible state change. Recovery requires backups or external intervention. | `rm -rf`, `git push --force`, dropping a table, deleting a branch |

## Precedence

Most restrictive at the top:

```
DESTRUCTIVE  ← highest
SPAWN
EXECUTE
NETWORK
WRITE
READ         ← lowest
```

`spine_lite.most_restrictive(effects)` walks this ordering top-down and returns the first match. The function is total over any non-empty subset of `Effect`; it raises `ValueError` on an empty input.

```python
from spine_lite import Effect, most_restrictive

most_restrictive({Effect.READ, Effect.NETWORK, Effect.WRITE})
# <Effect.NETWORK: 'network'>

most_restrictive({Effect.DESTRUCTIVE, Effect.READ})
# <Effect.DESTRUCTIVE: 'destructive'>
```

The ordering is encoded once in [`spine_lite.PRECEDENCE`](../reference/api.md). Every comparison in the runtime resolves through that constant; reordering is a one-line change with project-level sign-off.

## Why these six

Each class draws a line that matters for safety review:

- `READ` vs. `WRITE`: did anything change?
- `WRITE` vs. `NETWORK`: did anything cross a trust boundary?
- `NETWORK` vs. `EXECUTE`: did we hand control to another process?
- `EXECUTE` vs. `SPAWN`: did the child outlive the call?
- `SPAWN` vs. `DESTRUCTIVE`: can we undo it?

Anything finer is a manifest concern (the *which* file, the *which* host), not a taxonomy concern (the *what kind of effect*).

## Why closed

A taxonomy that grows at runtime is a taxonomy that drifts. Adding a seventh class would require:

1. Updating `Effect` and `PRECEDENCE` in `effects.py`.
2. Updating the parity tests and the porting-notes log.
3. Updating every consumer that exhaustively matches on `Effect`.
4. A migration note in `CHANGELOG.md` and `docs/explanation/porting-notes.md`.
5. Project-level sign-off — recorded as a HALT against [`CLAUDE.md`](https://github.com/MacFall7/spine-lite-python/blob/main/CLAUDE.md).

If you find yourself wanting a new class, first try modelling the new behaviour as an existing class with manifest-level qualifiers. The seventh class is almost always an existing class wearing a different hat.

## Determinism

`most_restrictive` is a pure function. Same input set → same output, every time. No hidden state, no clocks, no randomness. The runtime depends on this property — receipts hash by SHA exactly because the inputs uniquely determine the outputs.

The `effects` module contains zero I/O, zero clocks, zero randomness. This is enforced by the [Invariants](../explanation/invariants.md) and verified by the test suite.

## See also

- [Concepts / Overview](overview.md) — where the taxonomy fits in the pipeline.
- [Reference / API](../reference/api.md#effects) — the auto-generated `Effect`, `PRECEDENCE`, `most_restrictive` reference.
- [Reference / Glossary](../reference/glossary.md) — term-by-term definitions.
- [Explanation / Porting Notes](../explanation/porting-notes.md) — design history and the relationship to the sibling project.
