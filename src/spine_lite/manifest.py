"""Tool-manifest schema (Phase 2).

Pydantic v2 models for tool definitions, declared effects, and posture
constraints land here. The schema must round-trip the TypeScript reference
fixtures byte-for-byte after JSON normalisation. See
``docs/porting-notes.md`` for the source-of-truth schema.

Pure module: validation only, no I/O.
"""

from __future__ import annotations
