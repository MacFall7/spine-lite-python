"""spine-lite: deterministic policy and effects runtime for LLM tool calls.

Phase 1 surface only. Subsequent phases extend `__all__` as the classifier,
posture machine, and hook ship. See ``CLAUDE.md`` and ``docs/architecture.md``.
"""

from __future__ import annotations

import logging

__version__ = "0.1.0a0"

__all__ = ["__version__"]

logging.getLogger(__name__).addHandler(logging.NullHandler())
