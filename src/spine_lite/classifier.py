"""Effect classifier.

The :func:`classify` function maps a :class:`ToolCall` and a validated
:class:`spine_lite.manifest.Manifest` to a :class:`Decision`.

Pure module: deterministic, no I/O, no clocks, no randomness. Identical
inputs produce identical decisions every time. The decision's
``rationale`` is the only string-formatted field, and it is built from
fields in canonical order so two calls with the same inputs produce the
same byte-for-byte rationale.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from spine_lite.effects import Effect, most_restrictive

if TYPE_CHECKING:
    from spine_lite.manifest import Manifest


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolCall:
    """A planned tool invocation to classify.

    Attributes:
        tool: Tool name as declared in the manifest.
        arguments: Free-form key/value arguments. Currently informational
            only; future phases may use them to refine classification
            beyond the manifest's declared effects.
    """

    tool: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True, kw_only=True)
class Decision:
    """The result of classifying a :class:`ToolCall`.

    Attributes:
        tool: Echoed from the input call.
        effects: The full set of effect classes the call can produce, as a
            canonically-ordered tuple (sorted by ``PRECEDENCE``). Tuple
            rather than frozenset so equality and serialisation are
            byte-stable.
        most_restrictive: The dominant effect under
            :data:`spine_lite.PRECEDENCE`. Always a member of ``effects``.
        rationale: Human-readable explanation of why this effect set was
            chosen. Format is canonical so byte-stable across runs.
    """

    tool: str
    effects: tuple[Effect, ...]
    most_restrictive: Effect
    rationale: str


def classify(tool_call: ToolCall, manifest: Manifest) -> Decision:
    """Classify ``tool_call`` against ``manifest``.

    Args:
        tool_call: The planned invocation.
        manifest: A validated :class:`Manifest` declaring the tool.

    Returns:
        A :class:`Decision` carrying the effect set, the dominant effect,
        and a deterministic rationale.

    Raises:
        ManifestError: If the tool isn't declared in the manifest.

    Examples:
        >>> from spine_lite import Effect, Manifest, ToolDefinition
        >>> manifest = Manifest(tools={
        ...     "fetch": ToolDefinition(
        ...         name="fetch",
        ...         effects=(Effect.NETWORK, Effect.READ),
        ...     ),
        ... })
        >>> decision = classify(ToolCall(tool="fetch"), manifest)
        >>> decision.most_restrictive
        <Effect.NETWORK: 'network'>
        >>> decision.effects
        (<Effect.NETWORK: 'network'>, <Effect.READ: 'read'>)
    """
    definition = manifest.get(tool_call.tool)

    dominant = most_restrictive(definition.effects)
    return Decision(
        tool=tool_call.tool,
        effects=definition.effects,
        most_restrictive=dominant,
        rationale=_rationale(tool_call.tool, definition.effects, dominant),
    )


def _rationale(
    tool: str,
    effects: tuple[Effect, ...],
    dominant: Effect,
) -> str:
    """Format a deterministic rationale string."""
    classes = ", ".join(sorted(e.value for e in effects))
    return (
        f"tool {tool!r} declares effects [{classes}]; "
        f"dominant under PRECEDENCE is {dominant.value!r}"
    )


__all__ = ["Decision", "ToolCall", "classify"]
