"""Exception hierarchy.

All errors raised by spine-lite inherit from :class:`SpineLiteError`. Library
callers can catch the base class for blanket handling or the specific
subclasses for finer control. The hierarchy is closed in spirit — adding new
classes is permitted, but every new class must descend from the base.

Pure module: no I/O, no side effects.
"""

from __future__ import annotations


class SpineLiteError(Exception):
    """Base class for every error raised by spine-lite."""


class ManifestError(SpineLiteError):
    """Raised when a tool manifest is malformed or fails validation."""


class ClassificationError(SpineLiteError):
    """Raised when a tool call cannot be classified against a manifest."""


class PostureError(SpineLiteError):
    """Raised on illegal posture transitions or invalid posture state."""


class HookError(SpineLiteError):
    """Raised when the PreToolUse hook protocol is violated."""
