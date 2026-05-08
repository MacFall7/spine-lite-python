"""Tool-manifest schema.

Pydantic v2 models for tool definitions, declared effects, and posture
constraints. Pure module: validation only, no I/O.

Manifests round-trip authored fixtures byte-for-byte. The two
order-sensitive fields — :attr:`ToolDefinition.effects` and
:attr:`ToolDefinition.permitted_postures` — are canonicalised on
construction (deduplicated and sorted by enum-declaration order) so JSON
serialisation is stable across runs and platforms regardless of the
order the author wrote them in.
"""

from __future__ import annotations

from typing import Any, ClassVar, Final

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from spine_lite.effects import PRECEDENCE, Effect
from spine_lite.exceptions import ManifestError
from spine_lite.posture import Posture

_EFFECT_ORDER: Final[dict[Effect, int]] = {e: i for i, e in enumerate(PRECEDENCE)}
_POSTURE_ORDER: Final[dict[Posture, int]] = {p: i for i, p in enumerate(Posture)}


def _canonical_effects(effects: tuple[Effect, ...]) -> tuple[Effect, ...]:
    """Deduplicate and sort effects by ``PRECEDENCE`` order."""
    seen: set[Effect] = set()
    canonical: list[Effect] = []
    for effect in sorted(effects, key=_EFFECT_ORDER.__getitem__):
        if effect not in seen:
            seen.add(effect)
            canonical.append(effect)
    return tuple(canonical)


def _canonical_postures(postures: tuple[Posture, ...]) -> tuple[Posture, ...]:
    """Deduplicate and sort postures by enum declaration order."""
    seen: set[Posture] = set()
    canonical: list[Posture] = []
    for posture in sorted(postures, key=_POSTURE_ORDER.__getitem__):
        if posture not in seen:
            seen.add(posture)
            canonical.append(posture)
    return tuple(canonical)


class ToolDefinition(BaseModel):
    """Declares a single tool's effects and posture constraints.

    Attributes:
        name: Tool identifier as the LLM sees it. Must match the key under
            which this definition is registered in a :class:`Manifest`.
        description: Optional human-readable description.
        effects: Effect classes this tool's invocations can produce. Must
            be non-empty. Stored canonically: deduplicated and sorted by
            ``PRECEDENCE`` order.
        permitted_postures: Postures under which this tool may be invoked.
            ``None`` means no posture constraint (the tool runs under any
            posture). When set, must be non-empty. Stored canonically:
            deduplicated and sorted by :class:`Posture` declaration order.
        require_confirmation: If true, even an otherwise-allowed call must
            be confirmed by the operator before execution. Phase 3
            classifier honours this; Phase 2 just stores it.
        metadata: Free-form additional metadata. Manifest authors may
            carry arbitrary keys here; spine-lite ignores them but
            preserves them for round-trip serialisation.

    Examples:
        >>> definition = ToolDefinition(
        ...     name="read_file",
        ...     effects=(Effect.READ,),
        ... )
        >>> definition.effects
        (<Effect.READ: 'read'>,)
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
        str_strip_whitespace=True,
    )

    name: str = Field(min_length=1)
    description: str | None = None
    effects: tuple[Effect, ...] = Field(min_length=1)
    permitted_postures: tuple[Posture, ...] | None = None
    require_confirmation: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("effects", mode="after")
    @classmethod
    def _canonicalise_effects(
        cls,
        value: tuple[Effect, ...],
    ) -> tuple[Effect, ...]:
        return _canonical_effects(value)

    @field_validator("permitted_postures", mode="after")
    @classmethod
    def _canonicalise_postures(
        cls,
        value: tuple[Posture, ...] | None,
    ) -> tuple[Posture, ...] | None:
        if value is None:
            return None
        canonical = _canonical_postures(value)
        if not canonical:
            raise ValueError(
                "permitted_postures must be non-empty when set; "
                "use null/None to indicate no constraint",
            )
        return canonical


class Manifest(BaseModel):
    """A collection of tool definitions keyed by tool name.

    A manifest is the policy document for a runtime configuration. Every
    tool the LLM can call must appear here; calls to undeclared tools
    fail closed in the classifier.

    Attributes:
        tools: Mapping from tool name to its :class:`ToolDefinition`.
            Each definition's ``name`` field must match its key in this
            mapping. Empty manifests are permitted (zero tools declared).

    Examples:
        >>> manifest = Manifest(tools={
        ...     "read_file": ToolDefinition(name="read_file", effects=(Effect.READ,)),
        ... })
        >>> manifest.get("read_file").effects
        (<Effect.READ: 'read'>,)
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_default=True,
    )

    tools: dict[str, ToolDefinition] = Field(default_factory=dict)

    @field_validator("tools", mode="after")
    @classmethod
    def _names_match_keys(
        cls,
        tools: dict[str, ToolDefinition],
    ) -> dict[str, ToolDefinition]:
        for key, tool in tools.items():
            if tool.name != key:
                raise ValueError(
                    f"tool name mismatch: key {key!r} does not match definition name {tool.name!r}",
                )
        return tools

    def get(self, name: str) -> ToolDefinition:
        """Return the definition for ``name``.

        Args:
            name: Tool name to look up.

        Returns:
            The matching :class:`ToolDefinition`.

        Raises:
            ManifestError: If no tool with that name is declared.
        """
        try:
            return self.tools[name]
        except KeyError as exc:
            raise ManifestError(
                f"tool {name!r} not declared in manifest",
            ) from exc


def parse_manifest(data: Any) -> Manifest:
    """Validate ``data`` as a :class:`Manifest`.

    Wraps pydantic's :class:`pydantic.ValidationError` as
    :class:`ManifestError` so callers can catch a single typed exception
    rooted at :class:`SpineLiteError`.

    Args:
        data: A Python mapping (dict), a JSON string, or JSON bytes.
            Strings and bytes are parsed via
            :meth:`pydantic.BaseModel.model_validate_json`; everything
            else through :meth:`pydantic.BaseModel.model_validate`.

    Returns:
        A validated, immutable :class:`Manifest`.

    Raises:
        ManifestError: If validation fails for any reason. The original
            :class:`pydantic.ValidationError` is attached as ``__cause__``.

    Examples:
        >>> parse_manifest({
        ...     "tools": {
        ...         "read_file": {"name": "read_file", "effects": ["read"]},
        ...     },
        ... }).get("read_file").effects
        (<Effect.READ: 'read'>,)
    """
    try:
        if isinstance(data, (str, bytes)):
            return Manifest.model_validate_json(data)
        return Manifest.model_validate(data)
    except ValidationError as exc:
        raise ManifestError(f"manifest validation failed: {exc}") from exc
