"""Closed effects taxonomy.

Six-class enumeration of side-effect categories that a tool call can produce.
The ordering encoded in :data:`PRECEDENCE` is the spec — ``DESTRUCTIVE``
dominates, ``READ`` yields. :func:`most_restrictive` collapses any non-empty
set of effects to the single highest-precedence class.

This module is pure: no I/O, no clocks, no randomness. The taxonomy is closed
by design and mirrors the TypeScript reference at
https://github.com/MacFall7/M87-Spine-lite. Extensions require explicit
project sign-off.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Iterable


class Effect(StrEnum):
    """Side-effect class produced by a tool call.

    Members:
        READ: pure observation; no state change.
        WRITE: persistent state change to caller-owned storage.
        NETWORK: outbound network call.
        EXECUTE: subprocess invocation, no fork-and-detach.
        SPAWN: subprocess invocation that may fork-and-detach.
        DESTRUCTIVE: irreversible state change (delete, drop, force-push).
    """

    READ = "read"
    WRITE = "write"
    NETWORK = "network"
    EXECUTE = "execute"
    SPAWN = "spawn"
    DESTRUCTIVE = "destructive"


PRECEDENCE: Final[tuple[Effect, ...]] = (
    Effect.DESTRUCTIVE,
    Effect.SPAWN,
    Effect.EXECUTE,
    Effect.NETWORK,
    Effect.WRITE,
    Effect.READ,
)
"""Effect classes ordered from most restrictive to least restrictive."""


def most_restrictive(effects: Iterable[Effect]) -> Effect:
    """Return the highest-precedence effect from ``effects``.

    Args:
        effects: Non-empty iterable of effects. Order is irrelevant.

    Returns:
        The single effect that dominates all others under :data:`PRECEDENCE`.

    Raises:
        ValueError: If ``effects`` is empty.

    Examples:
        >>> most_restrictive({Effect.READ, Effect.NETWORK})
        <Effect.NETWORK: 'network'>
        >>> most_restrictive([Effect.DESTRUCTIVE, Effect.READ])
        <Effect.DESTRUCTIVE: 'destructive'>
    """
    materialised = frozenset(effects)
    if not materialised:
        raise ValueError("effects must be non-empty")
    for candidate in PRECEDENCE:
        if candidate in materialised:
            return candidate
    # Unreachable while the taxonomy and PRECEDENCE stay in sync; if a new
    # member is added without updating PRECEDENCE this hard-fails on the spot.
    raise AssertionError("effect outside PRECEDENCE")  # pragma: no cover
