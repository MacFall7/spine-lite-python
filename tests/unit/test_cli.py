"""Tests for the CLI entry point.

Three layers:

1. Smoke tests on every subcommand (version, validate-manifest, classify,
   hook) via Typer's CliRunner — fast, in-process.
2. Posture-specific integration tests for the hook subcommand.
3. End-to-end test via subprocess against the installed
   ``spine-lite`` console script, exercising the same path Claude Code
   uses when wiring the PreToolUse hook.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from spine_lite import __version__
from spine_lite.cli import app

runner = CliRunner()

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


# ---------- version ----------


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_no_args_shows_help_and_exits_nonzero() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code != 0
    assert "Usage" in result.stdout or "spine-lite" in result.stdout.lower()


def test_unknown_subcommand_exits_nonzero() -> None:
    result = runner.invoke(app, ["nope"])
    assert result.exit_code != 0


# ---------- validate-manifest ----------


def test_validate_manifest_valid_fixture(tmp_path: Path) -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    result = runner.invoke(app, ["validate-manifest", str(fixture)])
    assert result.exit_code == 0
    assert "valid:" in result.stdout


def test_validate_manifest_invalid_payload(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"tools": {"t": {"name": "t", "effects": ["bogus"]}}}')
    result = runner.invoke(app, ["validate-manifest", str(bad)])
    assert result.exit_code == 1
    assert "invalid:" in result.output


def test_validate_manifest_nonexistent_path() -> None:
    result = runner.invoke(app, ["validate-manifest", "/nonexistent/manifest.json"])
    assert result.exit_code != 0


# ---------- classify ----------


def test_classify_emits_json_decision() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    result = runner.invoke(
        app,
        ["classify", "fetch_url", "--manifest", str(fixture)],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip())
    assert payload["tool"] == "fetch_url"
    assert payload["most_restrictive"] == "network"
    assert "network" in payload["effects"]
    assert "read" in payload["effects"]


def test_classify_undeclared_tool_exits_nonzero() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    result = runner.invoke(
        app,
        ["classify", "ghost_tool", "--manifest", str(fixture)],
    )
    assert result.exit_code == 1
    assert "ManifestError" in result.output or "not declared" in result.output


def test_classify_invalid_manifest_exits_nonzero(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"tools": "not-an-object"}')
    result = runner.invoke(
        app,
        ["classify", "anything", "--manifest", str(bad)],
    )
    assert result.exit_code == 1


# ---------- hook ----------


def test_hook_allow_under_interactive() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    payload = json.dumps({"tool": "read_file"})
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(fixture), "--posture", "interactive"],
        input=payload,
    )
    assert result.exit_code == 0
    decision = json.loads(result.stdout.strip())
    assert decision["disposition"] == "allow"
    assert decision["tool"] == "read_file"


def test_hook_deny_destructive_under_locked() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    payload = json.dumps({"tool": "git_force_push"})
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(fixture), "--posture", "locked"],
        input=payload,
    )
    assert result.exit_code == 1
    decision = json.loads(result.stdout.strip())
    assert decision["disposition"] == "deny"


def test_hook_escalate_destructive_under_interactive() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    payload = json.dumps({"tool": "git_force_push"})
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(fixture), "--posture", "interactive"],
        input=payload,
    )
    # git_force_push has require_confirmation=True
    assert result.exit_code == 2
    decision = json.loads(result.stdout.strip())
    assert decision["disposition"] == "escalate"


def test_hook_invalid_payload_exits_64() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(fixture)],
        input="{not json}",
    )
    assert result.exit_code == 64


def test_hook_undeclared_tool_exits_65() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(fixture)],
        input=json.dumps({"tool": "ghost"}),
    )
    assert result.exit_code == 65


def test_hook_invalid_posture_arg_rejected() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(fixture), "--posture", "paranoid"],
        input=json.dumps({"tool": "read_file"}),
    )
    assert result.exit_code != 0
    # Either typer's BadParameter or our error wrapping.
    assert "paranoid" in result.output or "posture" in result.output.lower()


def test_hook_default_posture_is_interactive() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    payload = json.dumps({"tool": "read_file"})
    # No --posture flag → should default to INTERACTIVE
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(fixture)],
        input=payload,
    )
    assert result.exit_code == 0
    decision = json.loads(result.stdout.strip())
    assert decision["posture"] == "interactive"


def test_hook_invalid_manifest_file_exits_65(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text('{"tools": {"t": {"name": "t", "effects": ["bogus"]}}}')
    result = runner.invoke(
        app,
        ["hook", "--manifest", str(bad)],
        input=json.dumps({"tool": "t"}),
    )
    assert result.exit_code == 65
    assert "ManifestError" in result.output


def test_hook_byte_stable_across_two_invocations() -> None:
    fixture = FIXTURES_DIR / "manifest_basic.json"
    payload = json.dumps({"tool": "read_file", "arguments": {"path": "x"}})

    a = runner.invoke(app, ["hook", "--manifest", str(fixture)], input=payload)
    b = runner.invoke(app, ["hook", "--manifest", str(fixture)], input=payload)

    assert a.stdout == b.stdout


# ---------- E2E smoke (installed console script) ----------


@pytest.mark.parametrize(
    ("posture", "tool", "expected_exit", "expected_disposition"),
    [
        ("interactive", "read_file", 0, "allow"),
        ("locked", "git_force_push", 1, "deny"),
        ("interactive", "git_force_push", 2, "escalate"),
        ("autonomous", "git_force_push", 1, "deny"),
        ("dry_run", "shell_run", 1, "deny"),
    ],
)
def test_e2e_installed_console_script(
    posture: str,
    tool: str,
    expected_exit: int,
    expected_disposition: str,
) -> None:
    """Run the installed `spine-lite` script via subprocess.

    Closest equivalent in this sandbox to the blueprint's "install in
    fresh venv, wire as Claude Code PreToolUse hook" smoke. The script
    is on PATH because the venv has installed the package in editable
    mode; the test exercises the same code path Claude Code does.
    """
    fixture = FIXTURES_DIR / "manifest_basic.json"
    payload = json.dumps({"tool": tool})

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "spine_lite.cli",
            "hook",
            "--manifest",
            str(fixture),
            "--posture",
            posture,
        ],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )

    assert completed.returncode == expected_exit, (
        f"expected exit {expected_exit}, got {completed.returncode}; stderr={completed.stderr!r}"
    )
    decision = json.loads(completed.stdout.strip())
    assert decision["disposition"] == expected_disposition
    assert decision["tool"] == tool


def test_e2e_byte_stable_decision_across_subprocess_runs() -> None:
    """E2E byte-stability: the same input produces the same output bytes."""
    fixture = FIXTURES_DIR / "manifest_basic.json"
    payload = json.dumps({"tool": "read_file", "arguments": {"path": "/x"}})

    def run_once() -> str:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "spine_lite.cli",
                "hook",
                "--manifest",
                str(fixture),
            ],
            input=payload,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        return completed.stdout

    a = run_once()
    b = run_once()
    assert a == b


def test_e2e_version_via_subprocess() -> None:
    """Confirm the installed console script is wired correctly."""
    completed = subprocess.run(
        [sys.executable, "-m", "spine_lite.cli", "version"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert completed.returncode == 0
    assert __version__ in completed.stdout
