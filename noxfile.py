"""Nox sessions for spine-lite.

Each session is the canonical entry point for a verification gate. CI invokes
these directly. Contributors run `nox -s lint typecheck test` before any
commit and the full set before any push.
"""

from __future__ import annotations

import nox

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["lint", "typecheck", "test"]

PYTHON_VERSIONS = ["3.11", "3.12", "3.13"]


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    session.install("-e", ".", "pytest", "pytest-cov", "hypothesis")
    session.run("pytest", *session.posargs)


@nox.session
def lint(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session(name="format")
def format_(session: nox.Session) -> None:
    session.install("ruff")
    session.run("ruff", "check", "--fix", ".")
    session.run("ruff", "format", ".")


@nox.session
def typecheck(session: nox.Session) -> None:
    session.install("-e", ".", "mypy", "pytest", "hypothesis", "pydantic", "typer")
    session.run("mypy", "src", "tests")


@nox.session
def coverage(session: nox.Session) -> None:
    session.install("-e", ".", "pytest", "pytest-cov", "hypothesis")
    session.run(
        "pytest",
        "--cov=spine_lite",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-fail-under=95",
        *session.posargs,
    )


@nox.session
def docs(session: nox.Session) -> None:
    session.install("-e", ".[docs]")
    session.run("mkdocs", "build", "--strict")


@nox.session(name="docs-serve")
def docs_serve(session: nox.Session) -> None:
    session.install("-e", ".[docs]")
    session.run("mkdocs", "serve", *session.posargs)
