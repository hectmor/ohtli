from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.resource import Resource
from ohtli.representation.context import OPERATIONAL

BODY_TEMPLATE = """# {title}

## Summary

## Content

## Examples

## References

## Related Notes
"""


def to_representation(
    resource: Resource, *, today: date | None = None
) -> dict[str, Any]:
    """Build the Current Representation for a Resource.

    Property order and section structure follow
    implementations/platforms/obsidian/docs/metadata/resource.md and
    the existing Templater template. `status` starts at `draft` (the
    first Lifecycle value); `context` is independent from `status`,
    per the same Lifecycle Independence invariant established for
    Project and Area (Phase 13).
    """
    today = today or date.today()
    return {
        "properties": {
            "id": resource.id,
            "note_type": "resource",
            "created": today.isoformat(),
            "updated": today.isoformat(),
            "tags": [],
            "aliases": [],
            "status": "draft",
            "context": OPERATIONAL,
        },
        "title": resource.title,
        "body": BODY_TEMPLATE.format(title=resource.title),
    }


def from_representation(representation: dict[str, Any]) -> Resource:
    """Reconstruct the Resource Domain Object from its Current
    Representation.

    Only identity and title are Domain semantics; status, tags, and
    timestamps remain Metadata/Representation concerns and are not
    part of the Domain Object itself.
    """
    props = representation["properties"]
    return Resource(id=props["id"], title=representation["title"])
