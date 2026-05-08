"""Tests for the posture state machine, Disposition enum, and evaluate."""

from __future__ import annotations

import pytest

from spine_lite import (
    Decision,
    Disposition,
    Effect,
    Posture,
    PostureError,
    ToolDefinition,
    evaluate,
    transition,
)

# ---------- Posture (closed enum) ----------


def test_posture_has_exactly_four_members() -> None:
    assert len(Posture) == 4


def test_posture_member_names() -> None:
    assert {p.name for p in Posture} == {
        "INTERACTIVE",
        "AUTONOMOUS",
        "DRY_RUN",
        "LOCKED",
    }


@pytest.mark.parametrize(
    ("member", "value"),
    [
        (Posture.INTERACTIVE, "interactive"),
        (Posture.AUTONOMOUS, "autonomous"),
        (Posture.DRY_RUN, "dry_run"),
        (Posture.LOCKED, "locked"),
    ],
)
def test_posture_string_values_are_pinned(member: Posture, value: str) -> None:
    assert member.value == value
    assert member == value


def test_posture_unknown_value_raises() -> None:
    with pytest.raises(ValueError, match="not a valid Posture"):
        Posture("escalated")


def test_posture_round_trip_through_value() -> None:
    for member in Posture:
        assert Posture(member.value) is member


def test_posture_is_in_public_api() -> None:
    import spine_lite

    assert "Posture" in spine_lite.__all__
    assert spine_lite.Posture is Posture


# ---------- Disposition (closed enum) ----------


def test_disposition_has_exactly_three_members() -> None:
    assert len(Disposition) == 3


def test_disposition_member_names() -> None:
    assert {d.name for d in Disposition} == {"ALLOW", "DENY", "ESCALATE"}


@pytest.mark.parametrize(
    ("member", "value"),
    [
        (Disposition.ALLOW, "allow"),
        (Disposition.DENY, "deny"),
        (Disposition.ESCALATE, "escalate"),
    ],
)
def test_disposition_values_pinned(member: Disposition, value: str) -> None:
    assert member.value == value


def test_disposition_in_public_api() -> None:
    import spine_lite

    assert "Disposition" in spine_lite.__all__
    assert spine_lite.Disposition is Disposition


# ---------- transition ----------


@pytest.mark.parametrize("posture", list(Posture))
def test_transition_identity_is_always_allowed(posture: Posture) -> None:
    assert transition(posture, posture) is posture


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (Posture.INTERACTIVE, Posture.AUTONOMOUS),
        (Posture.INTERACTIVE, Posture.DRY_RUN),
        (Posture.INTERACTIVE, Posture.LOCKED),
        (Posture.AUTONOMOUS, Posture.INTERACTIVE),
        (Posture.AUTONOMOUS, Posture.LOCKED),
        (Posture.DRY_RUN, Posture.INTERACTIVE),
        (Posture.DRY_RUN, Posture.LOCKED),
        (Posture.LOCKED, Posture.INTERACTIVE),
    ],
)
def test_transition_allowed(source: Posture, target: Posture) -> None:
    assert transition(source, target) is target


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (Posture.AUTONOMOUS, Posture.DRY_RUN),
        (Posture.DRY_RUN, Posture.AUTONOMOUS),
        (Posture.LOCKED, Posture.AUTONOMOUS),
        (Posture.LOCKED, Posture.DRY_RUN),
    ],
)
def test_transition_illegal_raises(source: Posture, target: Posture) -> None:
    with pytest.raises(PostureError, match="illegal posture transition"):
        transition(source, target)


def test_transition_error_message_carries_both_postures() -> None:
    with pytest.raises(PostureError) as exc_info:
        transition(Posture.LOCKED, Posture.AUTONOMOUS)
    assert "locked" in str(exc_info.value)
    assert "autonomous" in str(exc_info.value)


def test_transition_table_covers_every_posture_as_source() -> None:
    """Every Posture member must have an explicit allow-set."""
    from spine_lite.posture import _ALLOWED_TRANSITIONS

    assert set(_ALLOWED_TRANSITIONS) == set(Posture)


# ---------- evaluate ----------


def _decision(*effects: Effect, tool: str = "t") -> Decision:
    """Construct a Decision with the given effects (canonically ordered)."""
    from spine_lite.effects import most_restrictive

    sorted_effects = tuple(sorted(set(effects), key=lambda e: list(Effect).index(e)))
    return Decision(
        tool=tool,
        effects=sorted_effects,
        most_restrictive=most_restrictive(effects),
        rationale="test",
    )


def _definition(
    *effects: Effect,
    name: str = "t",
    permitted: tuple[Posture, ...] | None = None,
    require_confirmation: bool = False,
) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        effects=effects,
        permitted_postures=permitted,
        require_confirmation=require_confirmation,
    )


def test_evaluate_interactive_read_allows() -> None:
    defn = _definition(Effect.READ)
    decision = _decision(Effect.READ)
    assert evaluate(Posture.INTERACTIVE, defn, decision) is Disposition.ALLOW


def test_evaluate_interactive_destructive_allows_when_no_confirmation() -> None:
    defn = _definition(Effect.DESTRUCTIVE, require_confirmation=False)
    decision = _decision(Effect.DESTRUCTIVE)
    assert evaluate(Posture.INTERACTIVE, defn, decision) is Disposition.ALLOW


def test_evaluate_interactive_with_confirmation_escalates() -> None:
    defn = _definition(Effect.DESTRUCTIVE, require_confirmation=True)
    decision = _decision(Effect.DESTRUCTIVE)
    assert evaluate(Posture.INTERACTIVE, defn, decision) is Disposition.ESCALATE


def test_evaluate_autonomous_with_confirmation_denies() -> None:
    defn = _definition(Effect.DESTRUCTIVE, require_confirmation=True)
    decision = _decision(Effect.DESTRUCTIVE)
    assert evaluate(Posture.AUTONOMOUS, defn, decision) is Disposition.DENY


def test_evaluate_autonomous_without_confirmation_allows() -> None:
    defn = _definition(Effect.WRITE, require_confirmation=False)
    decision = _decision(Effect.WRITE)
    assert evaluate(Posture.AUTONOMOUS, defn, decision) is Disposition.ALLOW


@pytest.mark.parametrize(
    "effect",
    [Effect.WRITE, Effect.NETWORK, Effect.EXECUTE, Effect.SPAWN, Effect.DESTRUCTIVE],
)
def test_evaluate_dry_run_denies_non_read(effect: Effect) -> None:
    defn = _definition(effect)
    decision = _decision(effect)
    assert evaluate(Posture.DRY_RUN, defn, decision) is Disposition.DENY


def test_evaluate_dry_run_allows_read() -> None:
    defn = _definition(Effect.READ)
    decision = _decision(Effect.READ)
    assert evaluate(Posture.DRY_RUN, defn, decision) is Disposition.ALLOW


@pytest.mark.parametrize(
    "effect",
    [Effect.WRITE, Effect.NETWORK, Effect.EXECUTE, Effect.SPAWN, Effect.DESTRUCTIVE],
)
def test_evaluate_locked_denies_non_read(effect: Effect) -> None:
    defn = _definition(effect)
    decision = _decision(effect)
    assert evaluate(Posture.LOCKED, defn, decision) is Disposition.DENY


def test_evaluate_locked_allows_read() -> None:
    defn = _definition(Effect.READ)
    decision = _decision(Effect.READ)
    assert evaluate(Posture.LOCKED, defn, decision) is Disposition.ALLOW


def test_evaluate_permitted_postures_excludes() -> None:
    defn = _definition(Effect.READ, permitted=(Posture.INTERACTIVE,))
    decision = _decision(Effect.READ)
    assert evaluate(Posture.AUTONOMOUS, defn, decision) is Disposition.DENY


def test_evaluate_permitted_postures_includes() -> None:
    defn = _definition(
        Effect.READ,
        permitted=(Posture.INTERACTIVE, Posture.AUTONOMOUS),
    )
    decision = _decision(Effect.READ)
    assert evaluate(Posture.AUTONOMOUS, defn, decision) is Disposition.ALLOW


def test_evaluate_permitted_postures_none_means_all_allowed() -> None:
    defn = _definition(Effect.READ, permitted=None)
    decision = _decision(Effect.READ)
    for posture in Posture:
        result = evaluate(posture, defn, decision)
        # READ is always allowed under every posture if no allow-list excludes it
        assert result is Disposition.ALLOW


def test_evaluate_collapses_to_dominant_effect_for_decision() -> None:
    """Mixed-effect tools evaluate against most_restrictive, not individual effects."""
    defn = _definition(Effect.READ, Effect.NETWORK)
    decision = _decision(Effect.READ, Effect.NETWORK)
    # most_restrictive is NETWORK, so DRY_RUN denies
    assert evaluate(Posture.DRY_RUN, defn, decision) is Disposition.DENY
    # but INTERACTIVE allows
    assert evaluate(Posture.INTERACTIVE, defn, decision) is Disposition.ALLOW


def test_evaluate_locked_overrides_confirmation_logic() -> None:
    """Even with require_confirmation, LOCKED denies non-READ."""
    defn = _definition(Effect.WRITE, require_confirmation=True)
    decision = _decision(Effect.WRITE)
    assert evaluate(Posture.LOCKED, defn, decision) is Disposition.DENY


def test_evaluate_is_pure_and_deterministic() -> None:
    """Same inputs produce identical results across calls."""
    defn = _definition(Effect.NETWORK, Effect.READ)
    decision = _decision(Effect.NETWORK, Effect.READ)
    a = evaluate(Posture.INTERACTIVE, defn, decision)
    b = evaluate(Posture.INTERACTIVE, defn, decision)
    assert a is b


def test_evaluate_in_public_api() -> None:
    import spine_lite

    assert "evaluate" in spine_lite.__all__
    assert "transition" in spine_lite.__all__
