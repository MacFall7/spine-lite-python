"""Operator command-line interface.

Phase 3 ships the full subcommand surface: ``version``,
``validate-manifest``, ``classify``, ``hook``. The CLI is one of the two
modules in the package permitted to do I/O (the other is
:mod:`spine_lite.hook`); everything below it is pure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from spine_lite import __version__
from spine_lite.classifier import ToolCall, classify
from spine_lite.exceptions import ManifestError, SpineLiteError
from spine_lite.hook import main as hook_main
from spine_lite.manifest import parse_manifest
from spine_lite.posture import Posture

app = typer.Typer(
    name="spine-lite",
    help="Deterministic policy and effects runtime for LLM tool calls.",
    no_args_is_help=True,
    add_completion=False,
)


_MANIFEST_PATH_ARG = typer.Option(
    ...,
    "--manifest",
    "-m",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to the manifest file (JSON).",
)


@app.callback()
def _root() -> None:
    """Group callback — forces multi-command mode so subcommands stay namespaced."""


@app.command()
def version() -> None:
    """Print the installed spine-lite version and exit."""
    typer.echo(__version__)


@app.command(name="validate-manifest")
def validate_manifest(
    manifest_path: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="Path to a manifest file (JSON).",
        ),
    ],
) -> None:
    """Validate a manifest file against the schema.

    Exits 0 if the manifest validates; exits 1 with a structured error
    message on stderr if validation fails.
    """
    try:
        parse_manifest(manifest_path.read_text(encoding="utf-8"))
    except ManifestError as exc:
        typer.echo(f"invalid: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"valid: {manifest_path}")


@app.command(name="classify")
def classify_cmd(
    tool: Annotated[
        str,
        typer.Argument(help="Tool name as declared in the manifest."),
    ],
    manifest_path: Annotated[Path, _MANIFEST_PATH_ARG],
) -> None:
    """One-shot classification of a tool call.

    Prints a JSON Decision to stdout. Useful for debugging the manifest;
    the production path is ``spine-lite hook``.

    Exits 0 on success; exits 1 if the manifest is invalid or the tool
    is not declared.
    """
    try:
        manifest = parse_manifest(manifest_path.read_text(encoding="utf-8"))
        decision = classify(ToolCall(tool=tool), manifest)
    except SpineLiteError as exc:
        typer.echo(f"{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    payload = {
        "tool": decision.tool,
        "effects": [e.value for e in decision.effects],
        "most_restrictive": decision.most_restrictive.value,
        "rationale": decision.rationale,
    }
    typer.echo(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
    )


@app.command(name="hook")
def hook_cmd(
    manifest_path: Annotated[Path, _MANIFEST_PATH_ARG],
    posture_value: Annotated[
        str,
        typer.Option(
            "--posture",
            help="Operational posture: interactive, autonomous, dry_run, or locked.",
        ),
    ] = Posture.INTERACTIVE.value,
) -> None:
    """PreToolUse hook adapter: stdin JSON in, decision JSON out.

    Reads a hook payload from stdin, runs the full pipeline (manifest
    validation -> classification -> posture evaluation -> receipt),
    writes the receipt's canonical JSON form to stdout. Exit code
    signals the disposition (see :mod:`spine_lite.hook` for the
    contract).
    """
    try:
        manifest = parse_manifest(manifest_path.read_text(encoding="utf-8"))
    except ManifestError as exc:
        typer.echo(f"ManifestError: {exc}", err=True)
        raise typer.Exit(code=65) from exc

    try:
        posture = Posture(posture_value)
    except ValueError as exc:
        raise typer.BadParameter(
            f"unknown posture {posture_value!r}; "
            f"expected one of: {', '.join(p.value for p in Posture)}",
        ) from exc

    code = hook_main(
        manifest,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        posture=posture,
    )
    raise typer.Exit(code=code)


if __name__ == "__main__":  # pragma: no cover
    app()
