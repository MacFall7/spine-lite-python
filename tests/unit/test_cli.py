"""Tests for the CLI entry point."""

from __future__ import annotations

from typer.testing import CliRunner

from spine_lite import __version__
from spine_lite.cli import app

runner = CliRunner()


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
