"""Tests for the classifier (basic / unit).

Property-based tests with hypothesis live in commit 5 alongside the
authored fixtures. This file covers the core behaviour and the error
paths.
"""

from __future__ import annotations

import pytest

from spine_lite import (
    Decision,
    Effect,
    Manifest,
    ManifestError,
    Posture,
    ToolCall,
    ToolDefinition,
    classify,
)


def _manifest(**tools: ToolDefinition) -> Manifest:
    return Manifest(tools=dict(tools))


# ---------- happy path ----------


def test_classify_returns_declared_effects() -> None:
    manifest = _manifest(
        read_file=ToolDefinition(name="read_file", effects=(Effect.READ,)),
    )
    decision = classify(ToolCall(tool="read_file"), manifest)

    assert decision.tool == "read_file"
    assert decision.effects == (Effect.READ,)
    assert decision.most_restrictive is Effect.READ


def test_classify_collapses_to_dominant_effect() -> None:
    manifest = _manifest(
        fetch=ToolDefinition(
            name="fetch",
            effects=(Effect.NETWORK, Effect.READ),
        ),
    )
    decision = classify(ToolCall(tool="fetch"), manifest)

    assert decision.most_restrictive is Effect.NETWORK
    assert set(decision.effects) == {Effect.NETWORK, Effect.READ}


def test_classify_destructive_dominates() -> None:
    manifest = _manifest(
        nuke=ToolDefinition(
            name="nuke",
            effects=(
                Effect.READ,
                Effect.WRITE,
                Effect.NETWORK,
                Effect.DESTRUCTIVE,
            ),
        ),
    )
    decision = classify(ToolCall(tool="nuke"), manifest)
    assert decision.most_restrictive is Effect.DESTRUCTIVE


def test_classify_returns_canonical_effect_order() -> None:
    """Decision.effects always uses PRECEDENCE order, not author order."""
    manifest = _manifest(
        t=ToolDefinition(
            name="t",
            effects=(Effect.READ, Effect.NETWORK, Effect.DESTRUCTIVE),
        ),
    )
    decision = classify(ToolCall(tool="t"), manifest)
    assert decision.effects == (Effect.DESTRUCTIVE, Effect.NETWORK, Effect.READ)


def test_classify_rationale_is_human_readable() -> None:
    manifest = _manifest(
        t=ToolDefinition(name="t", effects=(Effect.NETWORK, Effect.READ)),
    )
    decision = classify(ToolCall(tool="t"), manifest)

    assert "'t'" in decision.rationale
    assert "network" in decision.rationale
    assert "read" in decision.rationale


def test_classify_rationale_is_byte_stable() -> None:
    """Same inputs produce identical rationale strings."""
    manifest = _manifest(
        t=ToolDefinition(name="t", effects=(Effect.WRITE, Effect.READ)),
    )
    a = classify(ToolCall(tool="t"), manifest).rationale
    b = classify(ToolCall(tool="t"), manifest).rationale
    assert a == b


def test_classify_ignores_arguments_in_phase_2() -> None:
    """Phase 2 classifier doesn't refine on arguments; manifest is the spec."""
    manifest = _manifest(
        t=ToolDefinition(name="t", effects=(Effect.READ,)),
    )
    a = classify(ToolCall(tool="t", arguments={}), manifest)
    b = classify(ToolCall(tool="t", arguments={"path": "/etc/passwd"}), manifest)
    assert a.effects == b.effects
    assert a.most_restrictive == b.most_restrictive


def test_classify_with_posture_constrained_tool() -> None:
    """Permitted_postures is stored on the definition; Phase 2 doesn't gate on it."""
    manifest = _manifest(
        write_file=ToolDefinition(
            name="write_file",
            effects=(Effect.WRITE,),
            permitted_postures=(Posture.INTERACTIVE, Posture.AUTONOMOUS),
        ),
    )
    decision = classify(ToolCall(tool="write_file"), manifest)
    assert decision.most_restrictive is Effect.WRITE


# ---------- error paths ----------


def test_classify_raises_manifest_error_for_undeclared_tool() -> None:
    manifest = Manifest(tools={})
    with pytest.raises(ManifestError, match="not declared"):
        classify(ToolCall(tool="ghost"), manifest)


def test_classify_undeclared_tool_carries_name_in_message() -> None:
    manifest = Manifest(tools={})
    with pytest.raises(ManifestError) as exc_info:
        classify(ToolCall(tool="missing_tool"), manifest)
    assert "missing_tool" in str(exc_info.value)


# ---------- determinism ----------


def test_classify_is_deterministic_within_one_call() -> None:
    manifest = _manifest(
        t=ToolDefinition(name="t", effects=(Effect.SPAWN, Effect.NETWORK)),
    )
    call = ToolCall(tool="t")
    decisions = [classify(call, manifest) for _ in range(10)]
    assert all(d == decisions[0] for d in decisions)


def test_decision_is_frozen() -> None:
    decision = Decision(
        tool="t",
        effects=(Effect.READ,),
        most_restrictive=Effect.READ,
        rationale="example",
    )
    with pytest.raises(AttributeError):
        decision.tool = "u"  # type: ignore[misc]


def test_tool_call_is_frozen() -> None:
    call = ToolCall(tool="t")
    with pytest.raises(AttributeError):
        call.tool = "u"  # type: ignore[misc]


# ---------- public API ----------


def test_decision_classify_toolcall_in_public_api() -> None:
    import spine_lite

    for name in ("Decision", "ToolCall", "classify"):
        assert name in spine_lite.__all__
