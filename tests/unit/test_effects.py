"""Tests for the closed effects taxonomy."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from spine_lite.effects import PRECEDENCE, Effect, most_restrictive


def test_taxonomy_has_exactly_six_members() -> None:
    assert len(Effect) == 6


def test_taxonomy_member_names() -> None:
    assert {e.name for e in Effect} == {
        "READ",
        "WRITE",
        "NETWORK",
        "EXECUTE",
        "SPAWN",
        "DESTRUCTIVE",
    }


def test_effect_values_are_lowercase_strings() -> None:
    for member in Effect:
        assert member.value == member.name.lower()


def test_precedence_is_canonical_order() -> None:
    assert PRECEDENCE == (
        Effect.DESTRUCTIVE,
        Effect.SPAWN,
        Effect.EXECUTE,
        Effect.NETWORK,
        Effect.WRITE,
        Effect.READ,
    )


def test_precedence_covers_every_effect() -> None:
    assert set(PRECEDENCE) == set(Effect)
    assert len(PRECEDENCE) == len(Effect)


@pytest.mark.parametrize(
    ("effects", "expected"),
    [
        ({Effect.READ}, Effect.READ),
        ({Effect.READ, Effect.WRITE}, Effect.WRITE),
        ({Effect.READ, Effect.NETWORK}, Effect.NETWORK),
        ({Effect.WRITE, Effect.EXECUTE}, Effect.EXECUTE),
        ({Effect.EXECUTE, Effect.SPAWN}, Effect.SPAWN),
        ({Effect.NETWORK, Effect.DESTRUCTIVE}, Effect.DESTRUCTIVE),
        (set(Effect), Effect.DESTRUCTIVE),
    ],
)
def test_most_restrictive_returns_highest_precedence(
    effects: set[Effect],
    expected: Effect,
) -> None:
    assert most_restrictive(effects) is expected


def test_most_restrictive_accepts_frozenset() -> None:
    assert most_restrictive(frozenset({Effect.READ, Effect.WRITE})) is Effect.WRITE


def test_most_restrictive_accepts_list_with_duplicates() -> None:
    assert most_restrictive([Effect.READ, Effect.READ, Effect.WRITE]) is Effect.WRITE


def test_most_restrictive_accepts_generator() -> None:
    assert most_restrictive(e for e in [Effect.READ, Effect.NETWORK]) is Effect.NETWORK


def test_most_restrictive_empty_raises() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        most_restrictive(set())


_effect_set = st.sets(st.sampled_from(list(Effect)), min_size=1)


@given(effects=_effect_set)
def test_most_restrictive_is_deterministic(effects: set[Effect]) -> None:
    assert most_restrictive(effects) is most_restrictive(set(effects))


@given(effects=_effect_set)
def test_most_restrictive_returns_member_of_input(effects: set[Effect]) -> None:
    assert most_restrictive(effects) in effects


@given(effects=_effect_set)
def test_most_restrictive_dominates_every_input_element(effects: set[Effect]) -> None:
    result = most_restrictive(effects)
    result_idx = PRECEDENCE.index(result)
    for other in effects:
        assert PRECEDENCE.index(other) >= result_idx


@given(effects=_effect_set)
def test_most_restrictive_idempotent_under_singleton_wrap(effects: set[Effect]) -> None:
    once = most_restrictive(effects)
    twice = most_restrictive({once})
    assert once is twice
