"""Claude Code PreToolUse hook adapter.

The thin I/O wrapper around the pure pipeline. Reads a JSON payload
from stdin, classifies the tool call against the configured manifest,
applies the posture state machine, builds a deterministic receipt, and
writes the receipt's canonical JSON form to stdout. Exit code signals
the disposition.

This is the only module in the package besides :mod:`spine_lite.cli`
that touches stdin, stdout, or wall-clock time. Everything inside is
pure.
"""

from __future__ import annotations

import json
import sys
from typing import IO, TYPE_CHECKING

from spine_lite.classifier import ToolCall, classify
from spine_lite.exceptions import HookError, ManifestError
from spine_lite.posture import Disposition, Posture, evaluate
from spine_lite.receipt import Receipt

if TYPE_CHECKING:
    from spine_lite.manifest import Manifest

# Exit-code contract.
EXIT_ALLOW = 0
EXIT_DENY = 1
EXIT_ESCALATE = 2
EXIT_HOOK_ERROR = 64
EXIT_MANIFEST_ERROR = 65

_DISPOSITION_EXIT: dict[Disposition, int] = {
    Disposition.ALLOW: EXIT_ALLOW,
    Disposition.DENY: EXIT_DENY,
    Disposition.ESCALATE: EXIT_ESCALATE,
}


def run_hook(
    manifest: Manifest,
    payload: str | bytes,
    *,
    posture: Posture = Posture.INTERACTIVE,
) -> tuple[Receipt, int]:
    """Execute the pipeline against ``payload`` under ``manifest``.

    The payload is expected to be a JSON object with at least a ``tool``
    field (string) and optionally an ``arguments`` field (object). Any
    other top-level keys are ignored; the hook contract is intentionally
    minimal so it can adapt to multiple host hook formats.

    Args:
        manifest: A validated manifest declaring every tool the host
            may invoke.
        payload: The raw stdin bytes or string from the host.
        posture: The current operational posture. Defaults to
            ``INTERACTIVE``; production setups should pass an explicit
            value via the CLI ``--posture`` flag.

    Returns:
        A tuple of ``(receipt, exit_code)``. The caller is responsible
        for writing the receipt to stdout and returning the exit code.

    Raises:
        HookError: If the payload is not valid JSON, is not a JSON
            object, is missing required fields, or has wrong-typed
            fields.
        ManifestError: If the requested tool is not declared in the
            manifest. Propagated unchanged from the classifier.
    """
    data = _parse_payload(payload)

    tool_name = data.get("tool")
    if not isinstance(tool_name, str) or not tool_name:
        raise HookError("payload missing 'tool' string field")

    arguments = data.get("arguments", {})
    if not isinstance(arguments, dict):
        raise HookError("'arguments' field must be a JSON object if present")

    decision = classify(ToolCall(tool=tool_name, arguments=arguments), manifest)
    definition = manifest.get(tool_name)
    disposition = evaluate(posture, definition, decision)

    receipt = Receipt(
        tool=tool_name,
        arguments=arguments,
        effects=decision.effects,
        most_restrictive=decision.most_restrictive,
        rationale=decision.rationale,
        posture=posture,
        disposition=disposition,
        require_confirmation=definition.require_confirmation,
    )

    return receipt, _DISPOSITION_EXIT[disposition]


def main(
    manifest: Manifest,
    *,
    stdin: IO[str] = sys.stdin,
    stdout: IO[str] = sys.stdout,
    stderr: IO[str] = sys.stderr,
    posture: Posture = Posture.INTERACTIVE,
) -> int:
    """End-to-end hook invocation.

    Reads stdin, runs :func:`run_hook`, writes the canonical receipt
    JSON to stdout, and returns the exit code. On error, writes a
    structured JSON error payload to stdout (so the host always parses
    a JSON object) and a one-line message to stderr.

    Args:
        manifest: A validated manifest.
        stdin: Input stream. Defaults to :data:`sys.stdin`.
        stdout: Output stream for the receipt or error JSON. Defaults
            to :data:`sys.stdout`.
        stderr: Output stream for human-readable error messages.
            Defaults to :data:`sys.stderr`.
        posture: Operational posture.

    Returns:
        Exit code per the contract:

        - ``0`` (``EXIT_ALLOW``) — disposition is ALLOW.
        - ``1`` (``EXIT_DENY``) — disposition is DENY.
        - ``2`` (``EXIT_ESCALATE``) — disposition is ESCALATE.
        - ``64`` (``EXIT_HOOK_ERROR``) — payload protocol violation.
        - ``65`` (``EXIT_MANIFEST_ERROR``) — tool not declared in manifest.
    """
    payload = stdin.read()
    try:
        receipt, exit_code = run_hook(manifest, payload, posture=posture)
        stdout.write(receipt.to_canonical_json())
        stdout.write("\n")
        return exit_code
    except ManifestError as exc:
        _write_error(stdout, stderr, "ManifestError", str(exc))
        return EXIT_MANIFEST_ERROR
    except HookError as exc:
        _write_error(stdout, stderr, "HookError", str(exc))
        return EXIT_HOOK_ERROR


def _parse_payload(payload: str | bytes) -> dict[str, object]:
    """Parse ``payload`` as a JSON object or raise HookError."""
    text = payload.decode("utf-8", errors="strict") if isinstance(payload, bytes) else payload
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HookError(f"payload is not valid JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise HookError("payload must be a JSON object at the top level")
    return data


def _write_error(
    stdout: IO[str],
    stderr: IO[str],
    error_type: str,
    message: str,
) -> None:
    payload = {
        "disposition": Disposition.DENY.value,
        "error": error_type,
        "message": message,
    }
    stdout.write(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")),
    )
    stdout.write("\n")
    stderr.write(f"{error_type}: {message}\n")
