"""spine-lite: deterministic policy and effects runtime for LLM tool calls.

Phase 2 surface. Subsequent phases extend ``__all__`` as the classifier and
hook ship. See ``CLAUDE.md`` and ``docs/explanation/architecture.md``.
"""

from __future__ import annotations

import logging

from spine_lite.effects import PRECEDENCE, Effect, most_restrictive
from spine_lite.exceptions import (
    ClassificationError,
    HookError,
    ManifestError,
    PostureError,
    SpineLiteError,
)
from spine_lite.posture import Posture

__version__ = "0.1.0a0"

__all__ = [
    "PRECEDENCE",
    "ClassificationError",
    "Effect",
    "HookError",
    "ManifestError",
    "Posture",
    "PostureError",
    "SpineLiteError",
    "__version__",
    "most_restrictive",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
