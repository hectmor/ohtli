from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.resource import Resource
from ohtli.representation.context import OPERATIONAL
from ohtli.representation.notes import nest_under_heading_level

_NOTES_LEVEL = 2  # `## Notes` — carried content must nest below it

BODY_TEMPLATE = """# {title}

## Summary

## Content

## Examples

## Notes
{notes}
## References

## Related Notes
"""


def to_representation(
    resource: Resource, *, today: date | None = None, notes: str | None = None
) -> dict[str, Any]:
    """Build the Current Representation for a Resource.

    Property order and section structure follow
    implementations/platforms/obsidian/docs/metadata/resource.md and
    the existing Templater template. `status` starts at `draft` (the
    first Lifecycle value); `context` is independent from `status`,
    per the same Lifecycle Independence invariant established for
    Project and Area (Phase 13).

    `notes` carries an Inbox entry's body when a Resource originates
    from Processing. It lands in `## Notes`, the one section no
    Essential Attribute (Title, Content, Topic) or Responsibility
    claims: raw text is not yet synthesized knowledge, so it must not
    sit in `Summary` or `Content`.
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
        "body": BODY_TEMPLATE.format(
            title=resource.title,
            notes=f"\n{nest_under_heading_level(notes, _NOTES_LEVEL)}\n" if notes else "",
        ),
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
