"""Operator command-line interface.

Phase 1 exposes a single ``version`` subcommand. The ``validate-manifest``,
``classify``, and ``hook`` subcommands ship in Phases 2 and 3. The CLI is
the only place in the package where logging is configured and stdout is
written to directly.
"""

from __future__ import annotations

import typer

from spine_lite import __version__

app = typer.Typer(
    name="spine-lite",
    help="Deterministic policy and effects runtime for LLM tool calls.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def _root() -> None:
    """Group callback — forces multi-command mode so subcommands stay namespaced."""


@app.command()
def version() -> None:
    """Print the installed spine-lite version and exit."""
    typer.echo(__version__)


if __name__ == "__main__":  # pragma: no cover
    app()
