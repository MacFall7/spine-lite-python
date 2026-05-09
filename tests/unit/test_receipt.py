"""Tests for the deterministic Receipt dataclass."""

from __future__ import annotations

import hashlib
import json

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from spine_lite import (
    Disposition,
    Effect,
    Posture,
    Receipt,
)

_HYPOTHESIS_THOROUGH = settings(
    max_examples=1000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def _receipt(
    *,
    tool: str = "t",
    arguments: dict[str, object] | None = None,
    effects: tuple[Effect, ...] = (Effect.READ,),
    most_restrictive: Effect = Effect.READ,
    rationale: str = "test rationale",
    posture: Posture = Posture.INTERACTIVE,
    disposition: Disposition = Disposition.ALLOW,
    require_confirmation: bool = False,
) -> Receipt:
    return Receipt(
        tool=tool,
        arguments=arguments or {},
        effects=effects,
        most_restrictive=most_restrictive,
        rationale=rationale,
        posture=posture,
        disposition=disposition,
        require_confirmation=require_confirmation,
    )


# ---------- construction ----------


def test_receipt_minimal() -> None:
    r = _receipt()
    assert r.tool == "t"
    assert r.effects == (Effect.READ,)
    assert r.disposition is Disposition.ALLOW


def test_receipt_is_frozen() -> None:
    r = _receipt()
    with pytest.raises(AttributeError):
        r.tool = "u"  # type: ignore[misc]


def test_receipt_in_public_api() -> None:
    import spine_lite

    assert "Receipt" in spine_lite.__all__
    assert spine_lite.Receipt is Receipt


# ---------- to_canonical_dict ----------


def test_to_canonical_dict_serialises_enums_as_values() -> None:
    r = _receipt(
        effects=(Effect.NETWORK, Effect.READ),
        most_restrictive=Effect.NETWORK,
        posture=Posture.AUTONOMOUS,
        disposition=Disposition.DENY,
    )
    d = r.to_canonical_dict()
    assert d["effects"] == ["network", "read"]
    assert d["most_restrictive"] == "network"
    assert d["posture"] == "autonomous"
    assert d["disposition"] == "deny"


def test_to_canonical_dict_keys_are_sorted_when_dumped() -> None:
    r = _receipt()
    payload = json.dumps(r.to_canonical_dict(), sort_keys=True)
    decoded = json.loads(payload)
    assert list(decoded.keys()) == sorted(decoded.keys())


# ---------- to_canonical_json ----------


def test_to_canonical_json_is_byte_stable() -> None:
    r1 = _receipt(arguments={"path": "./scratch/x"})
    r2 = _receipt(arguments={"path": "./scratch/x"})
    assert r1.to_canonical_json() == r2.to_canonical_json()


def test_to_canonical_json_uses_compact_separators() -> None:
    r = _receipt()
    blob = r.to_canonical_json()
    # Compact form: no whitespace after commas or colons.
    assert ", " not in blob
    assert ": " not in blob


def test_to_canonical_json_preserves_unicode_in_rationale() -> None:
    r = _receipt(rationale="rationale with em dash — and quote 'x'")
    blob = r.to_canonical_json()
    assert "—" in blob
    assert "'x'" in blob


def test_to_canonical_json_keys_are_sorted() -> None:
    r = _receipt()
    blob = r.to_canonical_json()
    decoded = json.loads(blob)
    assert list(decoded.keys()) == sorted(decoded.keys())


def test_to_canonical_json_round_trips_to_dict() -> None:
    r = _receipt(
        effects=(Effect.WRITE, Effect.READ),
        most_restrictive=Effect.WRITE,
    )
    decoded = json.loads(r.to_canonical_json())
    assert decoded == r.to_canonical_dict()


# ---------- content_hash ----------


def test_content_hash_is_64_hex_chars() -> None:
    h = _receipt().content_hash()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_content_hash_is_deterministic() -> None:
    r1 = _receipt(arguments={"k": "v"})
    r2 = _receipt(arguments={"k": "v"})
    assert r1.content_hash() == r2.content_hash()


def test_content_hash_changes_with_tool() -> None:
    a = _receipt(tool="a").content_hash()
    b = _receipt(tool="b").content_hash()
    assert a != b


def test_content_hash_changes_with_disposition() -> None:
    a = _receipt(disposition=Disposition.ALLOW).content_hash()
    b = _receipt(disposition=Disposition.DENY).content_hash()
    assert a != b


def test_content_hash_changes_with_effects() -> None:
    a = _receipt(effects=(Effect.READ,), most_restrictive=Effect.READ).content_hash()
    b = _receipt(effects=(Effect.WRITE,), most_restrictive=Effect.WRITE).content_hash()
    assert a != b


def test_content_hash_matches_sha256_of_canonical_json() -> None:
    r = _receipt()
    expected = hashlib.sha256(r.to_canonical_json().encode("utf-8")).hexdigest()
    assert r.content_hash() == expected


def test_content_hash_argument_key_order_independent() -> None:
    """Argument key order shouldn't change the hash — sort_keys handles it."""
    r1 = _receipt(arguments={"a": 1, "b": 2})
    r2 = _receipt(arguments={"b": 2, "a": 1})
    assert r1.content_hash() == r2.content_hash()


# ---------- hypothesis property tests ----------


_RECEIPT_STRATEGY = st.builds(
    Receipt,
    tool=st.text(min_size=1, max_size=20),
    arguments=st.dictionaries(
        st.text(min_size=1, max_size=10),
        st.one_of(st.integers(), st.text(max_size=20), st.booleans()),
        max_size=5,
    ),
    effects=st.lists(st.sampled_from(list(Effect)), min_size=1, max_size=6).map(tuple),
    most_restrictive=st.sampled_from(list(Effect)),
    rationale=st.text(max_size=100),
    posture=st.sampled_from(list(Posture)),
    disposition=st.sampled_from(list(Disposition)),
    require_confirmation=st.booleans(),
)


@_HYPOTHESIS_THOROUGH
@given(receipt=_RECEIPT_STRATEGY)
def test_to_canonical_json_byte_stable_property(receipt: Receipt) -> None:
    """Same receipt → identical JSON output across calls."""
    a = receipt.to_canonical_json()
    b = receipt.to_canonical_json()
    assert a == b


@_HYPOTHESIS_THOROUGH
@given(receipt=_RECEIPT_STRATEGY)
def test_content_hash_byte_stable_property(receipt: Receipt) -> None:
    """Same receipt → identical content_hash across calls."""
    assert receipt.content_hash() == receipt.content_hash()


@_HYPOTHESIS_THOROUGH
@given(receipt=_RECEIPT_STRATEGY)
def test_content_hash_matches_sha256_property(receipt: Receipt) -> None:
    """content_hash is exactly sha256(to_canonical_json)."""
    expected = hashlib.sha256(
        receipt.to_canonical_json().encode("utf-8"),
    ).hexdigest()
    assert receipt.content_hash() == expected
