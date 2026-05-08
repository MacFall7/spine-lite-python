"""Posture state machine.

Phase 2 ships the closed :class:`Posture` enum used by manifest validation.
Phase 3 will add the transition functions (pure value-in-value-out).

Pure module: deterministic, no I/O.
"""

from __future__ import annotations

from enum import StrEnum


class Posture(StrEnum):
    """Operational posture of the runtime.

    Drives how the runtime treats ambiguous calls. Closed enum: extending
    requires a project-level decision. The members and their string values
    are pinned by ``docs/concepts/posture-and-hooks.md``.

    Members:
        INTERACTIVE: Operator at the keyboard; ambiguous calls escalate.
        AUTONOMOUS: No operator in the loop; ambiguous calls fail closed.
        DRY_RUN: Classification only; non-``READ`` effects don't fire.
        LOCKED: Refuse everything except explicit allow-listed read-only calls.
    """

    INTERACTIVE = "interactive"
    AUTONOMOUS = "autonomous"
    DRY_RUN = "dry_run"
    LOCKED = "locked"
