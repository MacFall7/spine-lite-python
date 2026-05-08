"""Tests for the closed Posture enum."""

from __future__ import annotations

import pytest

from spine_lite.posture import Posture


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


def test_posture_is_str_subclass() -> None:
    assert isinstance(Posture.INTERACTIVE, str)
    assert str(Posture.AUTONOMOUS) == "autonomous"


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
