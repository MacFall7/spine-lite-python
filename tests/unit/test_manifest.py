"""Tests for the pydantic v2 manifest schema."""

from __future__ import annotations

import pytest

from spine_lite import Effect, ManifestError, Posture, parse_manifest
from spine_lite.manifest import Manifest, ToolDefinition

# ---------- ToolDefinition ----------


def test_tool_definition_minimal() -> None:
    tool = ToolDefinition(name="read_file", effects=(Effect.READ,))
    assert tool.name == "read_file"
    assert tool.description is None
    assert tool.effects == (Effect.READ,)
    assert tool.permitted_postures is None
    assert tool.require_confirmation is False
    assert tool.metadata == {}


def test_tool_definition_full() -> None:
    tool = ToolDefinition(
        name="git_force_push",
        description="Force push, dangerous",
        effects=(Effect.NETWORK, Effect.DESTRUCTIVE),
        permitted_postures=(Posture.INTERACTIVE,),
        require_confirmation=True,
        metadata={"owner": "ops"},
    )
    assert tool.description == "Force push, dangerous"
    assert tool.permitted_postures == (Posture.INTERACTIVE,)
    assert tool.require_confirmation is True
    assert tool.metadata == {"owner": "ops"}


def test_tool_definition_canonicalises_effects() -> None:
    """Effects are deduplicated and sorted by PRECEDENCE order."""
    tool = ToolDefinition(
        name="t",
        effects=(Effect.READ, Effect.DESTRUCTIVE, Effect.WRITE, Effect.READ),
    )
    assert tool.effects == (Effect.DESTRUCTIVE, Effect.WRITE, Effect.READ)


def test_tool_definition_canonicalises_postures() -> None:
    """Postures are deduplicated and sorted by enum declaration order."""
    tool = ToolDefinition(
        name="t",
        effects=(Effect.READ,),
        permitted_postures=(
            Posture.LOCKED,
            Posture.INTERACTIVE,
            Posture.AUTONOMOUS,
            Posture.INTERACTIVE,
        ),
    )
    assert tool.permitted_postures == (
        Posture.INTERACTIVE,
        Posture.AUTONOMOUS,
        Posture.LOCKED,
    )


def test_tool_definition_rejects_empty_effects() -> None:
    with pytest.raises(ManifestError):
        parse_manifest({"tools": {"t": {"name": "t", "effects": []}}})


def test_tool_definition_rejects_unknown_effect() -> None:
    with pytest.raises(ManifestError):
        parse_manifest({"tools": {"t": {"name": "t", "effects": ["telepath"]}}})


def test_tool_definition_rejects_extra_field() -> None:
    with pytest.raises(ManifestError):
        parse_manifest(
            {"tools": {"t": {"name": "t", "effects": ["read"], "extra": 1}}},
        )


def test_tool_definition_is_frozen() -> None:
    from pydantic import ValidationError

    tool = ToolDefinition(name="t", effects=(Effect.READ,))
    with pytest.raises(ValidationError):
        tool.name = "u"


# ---------- Manifest ----------


def test_manifest_empty_is_valid() -> None:
    manifest = Manifest(tools={})
    assert manifest.tools == {}


def test_manifest_get_hit() -> None:
    tool = ToolDefinition(name="read_file", effects=(Effect.READ,))
    manifest = Manifest(tools={"read_file": tool})
    assert manifest.get("read_file") is tool


def test_manifest_get_miss_raises_manifest_error() -> None:
    manifest = Manifest(tools={})
    with pytest.raises(ManifestError, match="not declared"):
        manifest.get("does_not_exist")


def test_manifest_name_key_mismatch_raises() -> None:
    with pytest.raises(ManifestError, match="tool name mismatch"):
        parse_manifest(
            {"tools": {"a": {"name": "b", "effects": ["read"]}}},
        )


def test_manifest_unknown_posture_rejected() -> None:
    with pytest.raises(ManifestError):
        parse_manifest(
            {
                "tools": {
                    "t": {
                        "name": "t",
                        "effects": ["read"],
                        "permitted_postures": ["paranoid"],
                    },
                },
            },
        )


def test_manifest_empty_postures_list_rejected() -> None:
    with pytest.raises(ManifestError, match="non-empty"):
        parse_manifest(
            {
                "tools": {
                    "t": {
                        "name": "t",
                        "effects": ["read"],
                        "permitted_postures": [],
                    },
                },
            },
        )


# ---------- parse_manifest ----------


def test_parse_manifest_from_dict() -> None:
    manifest = parse_manifest(
        {
            "tools": {
                "read_file": {"name": "read_file", "effects": ["read"]},
                "write_file": {"name": "write_file", "effects": ["write"]},
            },
        },
    )
    assert set(manifest.tools) == {"read_file", "write_file"}


def test_parse_manifest_from_json_string() -> None:
    manifest = parse_manifest(
        '{"tools": {"r": {"name": "r", "effects": ["read"]}}}',
    )
    assert manifest.get("r").effects == (Effect.READ,)


def test_parse_manifest_from_json_bytes() -> None:
    manifest = parse_manifest(
        b'{"tools": {"r": {"name": "r", "effects": ["read"]}}}',
    )
    assert manifest.get("r").effects == (Effect.READ,)


def test_parse_manifest_invalid_json_string_raises() -> None:
    with pytest.raises(ManifestError):
        parse_manifest("{not json}")


def test_parse_manifest_attaches_validation_error_as_cause() -> None:
    with pytest.raises(ManifestError) as exc_info:
        parse_manifest({"tools": {"t": {"name": "t", "effects": "not-a-list"}}})
    assert exc_info.value.__cause__ is not None


# ---------- round-trip ----------


def test_manifest_round_trip_preserves_canonical_form() -> None:
    """Authored unsorted; parsed canonical; re-dumped; re-parsed; equal."""
    raw = {
        "tools": {
            "shell_run": {
                "name": "shell_run",
                "description": "Arbitrary shell command",
                "effects": ["spawn", "execute", "network"],
                "permitted_postures": ["locked", "interactive"],
                "require_confirmation": False,
                "metadata": {"category": "shell"},
            },
        },
    }

    parsed = parse_manifest(raw)
    dumped = parsed.model_dump(mode="json")
    re_parsed = parse_manifest(dumped)

    assert parsed == re_parsed
    assert parsed.get("shell_run").effects == (
        Effect.SPAWN,
        Effect.EXECUTE,
        Effect.NETWORK,
    )
    assert parsed.get("shell_run").permitted_postures == (
        Posture.INTERACTIVE,
        Posture.LOCKED,
    )


def test_manifest_round_trip_via_json_is_byte_stable() -> None:
    """Same inputs produce byte-identical JSON output across calls."""
    data = {
        "tools": {
            "t": {
                "name": "t",
                "effects": ["destructive", "read"],
                "permitted_postures": ["locked", "interactive"],
            },
        },
    }
    a = parse_manifest(data).model_dump_json()
    b = parse_manifest(data).model_dump_json()
    assert a == b


def test_manifest_metadata_round_trips_unchanged() -> None:
    """Free-form metadata survives parse/dump."""
    data = {
        "tools": {
            "t": {
                "name": "t",
                "effects": ["read"],
                "metadata": {"owner": "ops", "tags": ["audit", "ro"]},
            },
        },
    }
    parsed = parse_manifest(data)
    assert parsed.get("t").metadata == {"owner": "ops", "tags": ["audit", "ro"]}
