"""Tests for the PreToolUse hook adapter."""

from __future__ import annotations

import io
import json

import pytest

from spine_lite import (
    Disposition,
    Effect,
    Manifest,
    Posture,
    Receipt,
    ToolDefinition,
)
from spine_lite.hook import (
    EXIT_ALLOW,
    EXIT_DENY,
    EXIT_ESCALATE,
    EXIT_HOOK_ERROR,
    EXIT_MANIFEST_ERROR,
    main,
    run_hook,
)


def _manifest(**tools: ToolDefinition) -> Manifest:
    return Manifest(tools=dict(tools))


# ---------- run_hook (pure-ish core) ----------


def test_run_hook_allows_read_under_interactive() -> None:
    manifest = _manifest(
        read_file=ToolDefinition(name="read_file", effects=(Effect.READ,)),
    )
    payload = json.dumps({"tool": "read_file"})
    receipt, exit_code = run_hook(manifest, payload, posture=Posture.INTERACTIVE)

    assert isinstance(receipt, Receipt)
    assert receipt.tool == "read_file"
    assert receipt.disposition is Disposition.ALLOW
    assert exit_code == EXIT_ALLOW


def test_run_hook_denies_write_under_locked() -> None:
    manifest = _manifest(
        write_file=ToolDefinition(name="write_file", effects=(Effect.WRITE,)),
    )
    payload = json.dumps({"tool": "write_file", "arguments": {"path": "x"}})
    receipt, exit_code = run_hook(manifest, payload, posture=Posture.LOCKED)

    assert receipt.disposition is Disposition.DENY
    assert exit_code == EXIT_DENY


def test_run_hook_escalates_under_interactive_with_confirmation() -> None:
    manifest = _manifest(
        nuke=ToolDefinition(
            name="nuke",
            effects=(Effect.DESTRUCTIVE,),
            require_confirmation=True,
        ),
    )
    payload = json.dumps({"tool": "nuke"})
    receipt, exit_code = run_hook(manifest, payload, posture=Posture.INTERACTIVE)

    assert receipt.disposition is Disposition.ESCALATE
    assert exit_code == EXIT_ESCALATE


def test_run_hook_autonomous_with_confirmation_denies() -> None:
    manifest = _manifest(
        nuke=ToolDefinition(
            name="nuke",
            effects=(Effect.DESTRUCTIVE,),
            require_confirmation=True,
        ),
    )
    payload = json.dumps({"tool": "nuke"})
    receipt, exit_code = run_hook(manifest, payload, posture=Posture.AUTONOMOUS)

    assert receipt.disposition is Disposition.DENY
    assert exit_code == EXIT_DENY


def test_run_hook_accepts_bytes_payload() -> None:
    manifest = _manifest(
        t=ToolDefinition(name="t", effects=(Effect.READ,)),
    )
    payload = json.dumps({"tool": "t"}).encode("utf-8")
    receipt, exit_code = run_hook(manifest, payload, posture=Posture.INTERACTIVE)
    assert receipt.tool == "t"
    assert exit_code == EXIT_ALLOW


def test_run_hook_carries_arguments_into_receipt() -> None:
    manifest = _manifest(t=ToolDefinition(name="t", effects=(Effect.READ,)))
    payload = json.dumps({"tool": "t", "arguments": {"k": "v"}})
    receipt, _ = run_hook(manifest, payload, posture=Posture.INTERACTIVE)
    assert receipt.arguments == {"k": "v"}


def test_run_hook_default_posture_is_interactive() -> None:
    manifest = _manifest(t=ToolDefinition(name="t", effects=(Effect.READ,)))
    receipt, _ = run_hook(manifest, json.dumps({"tool": "t"}))
    assert receipt.posture is Posture.INTERACTIVE


# ---------- run_hook error paths ----------


def test_run_hook_invalid_json_raises_hook_error() -> None:
    from spine_lite.exceptions import HookError

    manifest = _manifest()
    with pytest.raises(HookError, match="not valid JSON"):
        run_hook(manifest, "{not json}", posture=Posture.INTERACTIVE)


def test_run_hook_payload_not_object_raises_hook_error() -> None:
    from spine_lite.exceptions import HookError

    manifest = _manifest()
    with pytest.raises(HookError, match="JSON object"):
        run_hook(manifest, "[1, 2, 3]", posture=Posture.INTERACTIVE)


def test_run_hook_missing_tool_field_raises_hook_error() -> None:
    from spine_lite.exceptions import HookError

    manifest = _manifest()
    with pytest.raises(HookError, match="missing 'tool'"):
        run_hook(manifest, "{}", posture=Posture.INTERACTIVE)


def test_run_hook_empty_tool_name_raises_hook_error() -> None:
    from spine_lite.exceptions import HookError

    manifest = _manifest()
    with pytest.raises(HookError, match="missing 'tool'"):
        run_hook(manifest, json.dumps({"tool": ""}), posture=Posture.INTERACTIVE)


def test_run_hook_non_string_tool_field_raises_hook_error() -> None:
    from spine_lite.exceptions import HookError

    manifest = _manifest()
    with pytest.raises(HookError, match="missing 'tool'"):
        run_hook(manifest, json.dumps({"tool": 42}), posture=Posture.INTERACTIVE)


def test_run_hook_arguments_not_object_raises_hook_error() -> None:
    from spine_lite.exceptions import HookError

    manifest = _manifest(t=ToolDefinition(name="t", effects=(Effect.READ,)))
    with pytest.raises(HookError, match="'arguments' field must be"):
        run_hook(
            manifest,
            json.dumps({"tool": "t", "arguments": [1, 2, 3]}),
            posture=Posture.INTERACTIVE,
        )


def test_run_hook_undeclared_tool_raises_manifest_error() -> None:
    from spine_lite.exceptions import ManifestError

    manifest = _manifest()
    with pytest.raises(ManifestError, match="not declared"):
        run_hook(
            manifest,
            json.dumps({"tool": "ghost"}),
            posture=Posture.INTERACTIVE,
        )


# ---------- main (full I/O wrapper) ----------


def test_main_allow_writes_canonical_json_to_stdout() -> None:
    manifest = _manifest(t=ToolDefinition(name="t", effects=(Effect.READ,)))
    stdin = io.StringIO(json.dumps({"tool": "t"}))
    stdout = io.StringIO()
    stderr = io.StringIO()

    code = main(manifest, stdin=stdin, stdout=stdout, stderr=stderr)

    assert code == EXIT_ALLOW
    output = stdout.getvalue()
    assert output.endswith("\n")
    parsed = json.loads(output)
    assert parsed["tool"] == "t"
    assert parsed["disposition"] == "allow"
    assert stderr.getvalue() == ""


def test_main_deny_returns_exit_one() -> None:
    manifest = _manifest(
        write=ToolDefinition(name="write", effects=(Effect.WRITE,)),
    )
    stdin = io.StringIO(json.dumps({"tool": "write"}))
    stdout = io.StringIO()
    stderr = io.StringIO()

    code = main(
        manifest,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        posture=Posture.LOCKED,
    )

    assert code == EXIT_DENY


def test_main_escalate_returns_exit_two() -> None:
    manifest = _manifest(
        nuke=ToolDefinition(
            name="nuke",
            effects=(Effect.DESTRUCTIVE,),
            require_confirmation=True,
        ),
    )
    stdin = io.StringIO(json.dumps({"tool": "nuke"}))
    stdout = io.StringIO()
    stderr = io.StringIO()

    code = main(
        manifest,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        posture=Posture.INTERACTIVE,
    )

    assert code == EXIT_ESCALATE


def test_main_invalid_json_returns_hook_error_exit() -> None:
    manifest = _manifest()
    stdin = io.StringIO("{not json}")
    stdout = io.StringIO()
    stderr = io.StringIO()

    code = main(manifest, stdin=stdin, stdout=stdout, stderr=stderr)

    assert code == EXIT_HOOK_ERROR
    parsed = json.loads(stdout.getvalue())
    assert parsed["error"] == "HookError"
    assert parsed["disposition"] == "deny"
    assert "HookError" in stderr.getvalue()


def test_main_undeclared_tool_returns_manifest_error_exit() -> None:
    manifest = _manifest()
    stdin = io.StringIO(json.dumps({"tool": "ghost"}))
    stdout = io.StringIO()
    stderr = io.StringIO()

    code = main(manifest, stdin=stdin, stdout=stdout, stderr=stderr)

    assert code == EXIT_MANIFEST_ERROR
    parsed = json.loads(stdout.getvalue())
    assert parsed["error"] == "ManifestError"


def test_main_writes_byte_stable_receipt_for_identical_input() -> None:
    manifest = _manifest(t=ToolDefinition(name="t", effects=(Effect.READ,)))

    def run_once() -> str:
        stdin = io.StringIO(json.dumps({"tool": "t"}))
        stdout = io.StringIO()
        stderr = io.StringIO()
        main(manifest, stdin=stdin, stdout=stdout, stderr=stderr)
        return stdout.getvalue()

    a = run_once()
    b = run_once()
    assert a == b


def test_main_receipt_content_hash_is_stable_across_runs() -> None:
    """E2E byte-stability: hash the stdout JSON across two runs."""
    manifest = _manifest(t=ToolDefinition(name="t", effects=(Effect.READ,)))

    stdin1 = io.StringIO(json.dumps({"tool": "t", "arguments": {"path": "x"}}))
    out1 = io.StringIO()
    stderr1 = io.StringIO()
    main(manifest, stdin=stdin1, stdout=out1, stderr=stderr1)

    stdin2 = io.StringIO(json.dumps({"tool": "t", "arguments": {"path": "x"}}))
    out2 = io.StringIO()
    stderr2 = io.StringIO()
    main(manifest, stdin=stdin2, stdout=out2, stderr=stderr2)

    a = json.loads(out1.getvalue())
    b = json.loads(out2.getvalue())
    assert a == b
