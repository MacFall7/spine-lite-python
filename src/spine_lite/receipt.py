"""Decision receipts.

A :class:`Receipt` is a structured record of a single classified call
under a posture. Receipts are content-addressable: serialising a receipt
to its canonical JSON form produces byte-identical output across runs
and platforms given identical inputs, and :meth:`Receipt.content_hash`
hashes that canonical form with SHA-256.

Pure module: no clocks, no randomness, no I/O. Wall-clock metadata that
needs to live alongside a receipt belongs in the hook layer; the
receipt itself stays content-addressable.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from spine_lite.effects import Effect
    from spine_lite.posture import Disposition, Posture


@dataclass(frozen=True, slots=True, kw_only=True)
class Receipt:
    """A deterministic record of one classified call under a posture.

    Attributes:
        tool: Name of the tool that was classified.
        arguments: Arguments echoed from the input call. Stored as
            authored; canonical serialisation sorts keys.
        effects: Canonical effect tuple from the classifier (ordered by
            ``PRECEDENCE``).
        most_restrictive: Dominant effect under ``PRECEDENCE``.
        rationale: Byte-stable rationale from the classifier.
        posture: Operational posture at the time of evaluation.
        disposition: ``ALLOW``, ``DENY``, or ``ESCALATE`` from
            :func:`spine_lite.posture.evaluate`.
        require_confirmation: Echoed from the tool's manifest definition
            so receipts stay self-contained for replay.

    Examples:
        >>> from spine_lite import Effect, Posture, Disposition
        >>> r = Receipt(
        ...     tool="t",
        ...     arguments={"a": 1},
        ...     effects=(Effect.READ,),
        ...     most_restrictive=Effect.READ,
        ...     rationale="...",
        ...     posture=Posture.INTERACTIVE,
        ...     disposition=Disposition.ALLOW,
        ...     require_confirmation=False,
        ... )
        >>> len(r.content_hash())
        64
    """

    tool: str
    arguments: dict[str, Any]
    effects: tuple[Effect, ...]
    most_restrictive: Effect
    rationale: str
    posture: Posture
    disposition: Disposition
    require_confirmation: bool

    def to_canonical_dict(self) -> dict[str, Any]:
        """Return a canonical dict representation.

        Keys are sorted; enum values are serialised as their string
        forms; the effect tuple is serialised as a list. Suitable as
        input to :func:`json.dumps` with ``sort_keys=True`` for byte-
        stable output.

        Returns:
            A dict whose JSON encoding is byte-stable across runs.
        """
        return {
            "arguments": self.arguments,
            "disposition": self.disposition.value,
            "effects": [e.value for e in self.effects],
            "most_restrictive": self.most_restrictive.value,
            "posture": self.posture.value,
            "rationale": self.rationale,
            "require_confirmation": self.require_confirmation,
            "tool": self.tool,
        }

    def to_canonical_json(self) -> str:
        """Return a byte-stable JSON encoding.

        Uses ``sort_keys=True``, ``ensure_ascii=False`` (so the rationale
        stays human-readable in its original encoding), and a compact
        separator pair. Two receipts with identical fields produce
        byte-identical output.
        """
        return json.dumps(
            self.to_canonical_dict(),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """Return the SHA-256 hex digest of :meth:`to_canonical_json`.

        Identical receipts produce identical hashes. Different receipts —
        even ones differing only in argument order before canonicalisation
        — produce identical hashes once round-tripped through this method.
        """
        encoded = self.to_canonical_json().encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


__all__ = ["Receipt"]
