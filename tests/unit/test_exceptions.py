"""Tests for the exception hierarchy."""

from __future__ import annotations

import pytest

from spine_lite.exceptions import (
    ClassificationError,
    HookError,
    ManifestError,
    PostureError,
    SpineLiteError,
)


@pytest.mark.parametrize(
    "exc_class",
    [ManifestError, ClassificationError, PostureError, HookError],
)
def test_subclasses_inherit_from_base(exc_class: type[SpineLiteError]) -> None:
    assert issubclass(exc_class, SpineLiteError)


def test_base_inherits_from_exception() -> None:
    assert issubclass(SpineLiteError, Exception)


def test_can_raise_and_catch_subclass_via_base() -> None:
    with pytest.raises(SpineLiteError):
        raise ManifestError("bad manifest")


def test_specific_subclass_catches_only_itself() -> None:
    with pytest.raises(ClassificationError):
        raise ClassificationError("ambiguous")
    with pytest.raises(ManifestError):
        raise ManifestError("invalid schema")


def test_message_round_trip() -> None:
    err = HookError("malformed payload")
    assert str(err) == "malformed payload"
