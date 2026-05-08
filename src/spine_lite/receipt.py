"""Decision receipts (Phase 3).

Structured records of every classified call. Field ordering is deterministic
so receipts serialise to identical bytes given identical inputs. The hook
emits one receipt per tool call.

Pure module: serialisation only, no I/O.
"""

from __future__ import annotations
