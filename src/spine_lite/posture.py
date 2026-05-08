"""Posture state machine.

Closed :class:`Posture` enum, the closed :class:`Disposition` enum, the
explicit :func:`transition` rule table, and :func:`evaluate` — the pure
policy function that maps ``(posture, definition, decision)`` to a
disposition.

Pure module: deterministic, no I/O. Same input produces the same output,
every time. The transition table and the evaluation rules are encoded
inline; both are sensitive to changes and warrant project-level sign-off
on extension.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Final

from spine_lite.effects import Effect
from spine_lite.exceptions import PostureError

if TYPE_CHECKING:
    from spine_lite.classifier import Decision
    from spine_lite.manifest import ToolDefinition


class Posture(StrEnum):
    """Operational posture of the runtime.

    Drives how the runtime treats tool calls. Closed enum: extending
    requires a project-level decision. The members and their string
    values are pinned by ``docs/concepts/posture-and-hooks.md``.

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


class Disposition(StrEnum):
    """The outcome of evaluating a classified decision under a posture.

    Members:
        ALLOW: Permitted; the tool may run as classified.
        DENY: Refused; the tool must not run.
        ESCALATE: Permitted only after operator confirmation. Only
            returned under :attr:`Posture.INTERACTIVE`; autonomous
            postures fail closed instead of escalating.
    """

    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"


_ALLOWED_TRANSITIONS: Final[dict[Posture, frozenset[Posture]]] = {
    Posture.INTERACTIVE: frozenset(
        {Posture.AUTONOMOUS, Posture.DRY_RUN, Posture.LOCKED},
    ),
    Posture.AUTONOMOUS: frozenset({Posture.INTERACTIVE, Posture.LOCKED}),
    Posture.DRY_RUN: frozenset({Posture.INTERACTIVE, Posture.LOCKED}),
    Posture.LOCKED: frozenset({Posture.INTERACTIVE}),
}


def transition(current: Posture, target: Posture) -> Posture:
    """Transition from ``current`` to ``target``.

    Identity transitions (``target is current``) are always permitted and
    return ``current`` unchanged. Cross-posture transitions must appear
    in the allow-set for the source posture.

    Args:
        current: The posture being left.
        target: The posture being entered.

    Returns:
        The new posture (always equal to ``target`` on success).

    Raises:
        PostureError: If the transition is not in the allow-set.

    Examples:
        >>> transition(Posture.INTERACTIVE, Posture.AUTONOMOUS)
        <Posture.AUTONOMOUS: 'autonomous'>
        >>> transition(Posture.LOCKED, Posture.INTERACTIVE)
        <Posture.INTERACTIVE: 'interactive'>
    """
    if target is current:
        return current
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise PostureError(
            f"illegal posture transition: {current.value} → {target.value}",
        )
    return target


def evaluate(
    posture: Posture,
    definition: ToolDefinition,
    decision: Decision,
) -> Disposition:
    """Map a classified call under a posture to a :class:`Disposition`.

    Pure function. Encodes the policy rules:

    1. **Posture allow-list.** If the tool's
       :attr:`~spine_lite.manifest.ToolDefinition.permitted_postures` is
       set and the current posture isn't in it, the tool is denied
       regardless of the rest.
    2. **LOCKED.** Only ``READ`` calls are permitted. Anything else is
       denied.
    3. **DRY_RUN.** Only ``READ`` calls fire. Anything else is denied
       (the tool would be classified, but DRY_RUN's contract is that no
       state-changing effect actually executes).
    4. **`require_confirmation`.** A tool flagged as requiring
       confirmation escalates under ``INTERACTIVE`` and fails closed
       (denies) under ``AUTONOMOUS``.
    5. Otherwise: ``ALLOW``.

    Args:
        posture: Current operational posture.
        definition: The tool's manifest definition.
        decision: The classifier's output for the tool call.

    Returns:
        ``ALLOW``, ``DENY``, or ``ESCALATE``.

    Examples:
        >>> from spine_lite import Effect, ToolDefinition, Decision
        >>> defn = ToolDefinition(name="t", effects=(Effect.WRITE,))
        >>> dec = Decision(
        ...     tool="t", effects=(Effect.WRITE,),
        ...     most_restrictive=Effect.WRITE, rationale="",
        ... )
        >>> evaluate(Posture.LOCKED, defn, dec)
        <Disposition.DENY: 'deny'>
        >>> evaluate(Posture.INTERACTIVE, defn, dec)
        <Disposition.ALLOW: 'allow'>
    """
    if definition.permitted_postures is not None and posture not in definition.permitted_postures:
        return Disposition.DENY

    if posture is Posture.LOCKED:
        return Disposition.ALLOW if decision.most_restrictive is Effect.READ else Disposition.DENY

    if posture is Posture.DRY_RUN:
        return Disposition.ALLOW if decision.most_restrictive is Effect.READ else Disposition.DENY

    if definition.require_confirmation:
        if posture is Posture.AUTONOMOUS:
            return Disposition.DENY
        return Disposition.ESCALATE

    return Disposition.ALLOW


__all__ = [
    "Disposition",
    "Posture",
    "evaluate",
    "transition",
]
