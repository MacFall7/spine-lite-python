"""Tests for the classifier.

Three layers:

1. Unit tests covering happy paths, error paths, frozen dataclass
   immutability, and the public-API surface.
2. Parametrized parity tests against the authored fixtures in
   ``tests/fixtures/``: round-trip JSON byte-stability per manifest,
   and case-by-case decision parity for ``manifest_basic.json``.
3. Hypothesis property tests for determinism, dominance, and round-trip
   stability — 1,000 examples each.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from spine_lite import (
    Decision,
    Effect,
    Manifest,
    ManifestError,
    Posture,
    ToolCall,
    ToolDefinition,
    classify,
    parse_manifest,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

_HYPOTHESIS_THOROUGH = settings(
    max_examples=1000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
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


# ---------- parity tests against authored fixtures ----------


_MANIFEST_FIXTURES = (
    "manifest_minimal.json",
    "manifest_basic.json",
    "manifest_full.json",
)


@pytest.mark.parametrize("fixture", _MANIFEST_FIXTURES)
def test_manifest_fixture_loads_cleanly(fixture: str) -> None:
    raw = (FIXTURES_DIR / fixture).read_text()
    manifest = parse_manifest(raw)
    assert isinstance(manifest, Manifest)


@pytest.mark.parametrize("fixture", _MANIFEST_FIXTURES)
def test_manifest_fixture_round_trip_byte_stable(fixture: str) -> None:
    """parse → dump → parse → dump produces identical bytes the second time."""
    raw = (FIXTURES_DIR / fixture).read_text()
    parsed = parse_manifest(raw)
    dumped_once = parsed.model_dump_json()
    re_parsed = parse_manifest(dumped_once)
    dumped_twice = re_parsed.model_dump_json()
    assert dumped_once == dumped_twice
    assert parsed == re_parsed


def _load_decision_cases() -> list[dict[str, object]]:
    payload = json.loads((FIXTURES_DIR / "decisions_basic.json").read_text())
    cases: list[dict[str, object]] = payload["cases"]
    return cases


@pytest.fixture(scope="module")
def basic_manifest() -> Manifest:
    return parse_manifest((FIXTURES_DIR / "manifest_basic.json").read_text())


@pytest.mark.parametrize(
    "case",
    _load_decision_cases(),
    ids=lambda c: str(c["name"]),
)
def test_decision_parity_against_fixture(
    case: dict[str, object],
    basic_manifest: Manifest,
) -> None:
    expected = case["expected"]
    assert isinstance(expected, dict)

    decision = classify(ToolCall(tool=str(case["tool"])), basic_manifest)

    assert decision.tool == expected["tool"]
    expected_effects = tuple(Effect(e) for e in expected["effects"])
    assert decision.effects == expected_effects
    assert decision.most_restrictive == Effect(str(expected["most_restrictive"]))


# ---------- hypothesis property tests ----------


_NAME_STRATEGY = st.text(
    alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
    min_size=1,
    max_size=15,
)

_EFFECTS_STRATEGY = st.lists(
    st.sampled_from(list(Effect)),
    min_size=1,
    max_size=6,
).map(tuple)

_POSTURES_STRATEGY = st.one_of(
    st.none(),
    st.lists(
        st.sampled_from(list(Posture)),
        min_size=1,
        max_size=4,
    ).map(tuple),
)


@st.composite
def _tool_definition_strategy(draw: st.DrawFn, name: str) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description=draw(st.one_of(st.none(), st.text(max_size=30))),
        effects=draw(_EFFECTS_STRATEGY),
        permitted_postures=draw(_POSTURES_STRATEGY),
        require_confirmation=draw(st.booleans()),
    )


@st.composite
def _manifest_strategy(draw: st.DrawFn) -> Manifest:
    names = draw(st.lists(_NAME_STRATEGY, min_size=1, max_size=5, unique=True))
    tools = {name: draw(_tool_definition_strategy(name=name)) for name in names}
    return Manifest(tools=tools)


@_HYPOTHESIS_THOROUGH
@given(manifest=_manifest_strategy())
def test_classify_is_deterministic_property(manifest: Manifest) -> None:
    """classify(call, manifest) returns the same Decision on every call."""
    for tool_name in manifest.tools:
        call = ToolCall(tool=tool_name)
        first = classify(call, manifest)
        second = classify(call, manifest)
        assert first == second


@_HYPOTHESIS_THOROUGH
@given(manifest=_manifest_strategy())
def test_classify_dominant_is_in_effects_property(manifest: Manifest) -> None:
    """The Decision's most_restrictive is always a member of its effects."""
    for tool_name in manifest.tools:
        decision = classify(ToolCall(tool=tool_name), manifest)
        assert decision.most_restrictive in decision.effects


@_HYPOTHESIS_THOROUGH
@given(manifest=_manifest_strategy())
def test_classify_effects_match_manifest_definition(manifest: Manifest) -> None:
    """The Decision's effects are exactly the manifest's declared effects."""
    for tool_name, definition in manifest.tools.items():
        decision = classify(ToolCall(tool=tool_name), manifest)
        assert decision.effects == definition.effects


@_HYPOTHESIS_THOROUGH
@given(manifest=_manifest_strategy())
def test_classify_rationale_is_byte_stable_property(manifest: Manifest) -> None:
    """Identical inputs produce byte-identical rationale strings."""
    for tool_name in manifest.tools:
        call = ToolCall(tool=tool_name)
        a = classify(call, manifest).rationale
        b = classify(call, manifest).rationale
        assert a == b


@_HYPOTHESIS_THOROUGH
@given(manifest=_manifest_strategy())
def test_classify_stable_across_manifest_round_trip(manifest: Manifest) -> None:
    """Manifest → JSON → Manifest produces identical decisions for every tool."""
    re_parsed = parse_manifest(manifest.model_dump_json())
    for tool_name in manifest.tools:
        call = ToolCall(tool=tool_name)
        original = classify(call, manifest)
        replayed = classify(call, re_parsed)
        assert original == replayed


@_HYPOTHESIS_THOROUGH
@given(
    manifest=_manifest_strategy(),
    arg_payload=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.text(max_size=20),
        max_size=5,
    ),
)
def test_classify_ignores_arguments_property(
    manifest: Manifest,
    arg_payload: dict[str, str],
) -> None:
    """Phase 2: arguments are stored on ToolCall but don't influence classification."""
    for tool_name in manifest.tools:
        no_args = classify(ToolCall(tool=tool_name), manifest)
        with_args = classify(ToolCall(tool=tool_name, arguments=arg_payload), manifest)
        assert no_args.effects == with_args.effects
        assert no_args.most_restrictive == with_args.most_restrictive
