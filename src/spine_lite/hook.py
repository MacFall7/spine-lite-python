"""Claude Code PreToolUse hook adapter (Phase 3).

Reads a hook payload from stdin, classifies the tool call against the
configured manifest, applies the posture state machine, and writes a
decision payload to stdout. Exit code signals allow vs. deny.

I/O lives here — the pure modules stay pure.
"""

from __future__ import annotations
