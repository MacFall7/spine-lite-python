"""Posture state machine (Phase 3).

A pure transition function over a closed ``Posture`` enum. No hidden state.
Every transition is a value-in-value-out function. See
``docs/architecture.md`` for the state diagram.

Pure module: deterministic, no I/O.
"""

from __future__ import annotations
