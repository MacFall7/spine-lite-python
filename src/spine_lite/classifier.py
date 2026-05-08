"""Effect classifier (Phase 2).

``classify(tool_call, manifest) -> Decision`` is a pure function that lands
in Phase 2. It returns the set of effects implied by a tool call against a
validated manifest, plus the dominating effect under
:data:`spine_lite.effects.PRECEDENCE`.

Pure module: deterministic, no I/O, no clocks, no randomness.
"""

from __future__ import annotations
