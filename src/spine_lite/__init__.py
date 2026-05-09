"""spine-lite: deterministic policy and effects runtime for LLM tool calls.

Phase 2 surface. Subsequent phases extend ``__all__`` as the classifier and
hook ship. See ``CLAUDE.md`` and ``docs/explanation/architecture.md``.
"""

from __future__ import annotations

import logging

from spine_lite.classifier import Decision, ToolCall, classify
from spine_lite.effects import PRECEDENCE, Effect, most_restrictive
from spine_lite.exceptions import (
    ClassificationError,
    HookError,
    ManifestError,
    PostureError,
    SpineLiteError,
)
from spine_lite.manifest import Manifest, ToolDefinition, parse_manifest
from spine_lite.posture import Disposition, Posture, evaluate, transition
from spine_lite.receipt import Receipt

__version__ = "0.3.0a0"

__all__ = [
    "PRECEDENCE",
    "ClassificationError",
    "Decision",
    "Disposition",
    "Effect",
    "HookError",
    "Manifest",
    "ManifestError",
    "Posture",
    "PostureError",
    "Receipt",
    "SpineLiteError",
    "ToolCall",
    "ToolDefinition",
    "__version__",
    "classify",
    "evaluate",
    "most_restrictive",
    "parse_manifest",
    "transition",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
