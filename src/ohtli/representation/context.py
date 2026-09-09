from __future__ import annotations

from datetime import date
from typing import Any

OPERATIONAL = "operational"
HISTORICAL = "historical"


def _set_context(
    representation: dict[str, Any], context: str, *, today: date | None = None
) -> dict[str, Any]:
    today = today or date.today()
    properties = dict(representation["properties"])
    properties["context"] = context
    properties["updated"] = today.isoformat()
    return {**representation, "properties": properties}


def archive(representation: dict[str, Any], *, today: date | None = None) -> dict[str, Any]:
    """Move a representation from operational to historical presence.

    Contextual presence is independent of lifecycle (`status`, per
    `archive-workflow.md`'s Lifecycle Independence invariant): only
    `context` (and `updated`) change here. Shared by every Domain
    Object's representation, since this transformation carries no
    Project/Area-specific knowledge — Archive is a class of
    transformation, generalized the same way Capture and Processing
    already are, not a per-object function.
    """
    return _set_context(representation, HISTORICAL, today=today)


def reactivate(representation: dict[str, Any], *, today: date | None = None) -> dict[str, Any]:
    """The inverse of `archive`: restore operational presence.

    Reactivate does not imply any lifecycle transition — `status` is
    left untouched, matching the spec's explicit example that
    Reactivate does not perform Completed -> Active.
    """
    return _set_context(representation, OPERATIONAL, today=today)
