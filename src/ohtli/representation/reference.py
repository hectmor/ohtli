from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.reference import Reference
from ohtli.representation.context import OPERATIONAL
from ohtli.representation.notes import nest_under_heading_level

_NOTES_LEVEL = 2  # `## Notes` — carried content must nest below it

BODY_TEMPLATE = """# {title}

## Citation

## Summary

## Key Points

## Notes
{notes}
## Links
"""


def to_representation(
    reference: Reference, *, today: date | None = None, notes: str | None = None
) -> dict[str, Any]:
    """Build the Current Representation for a Reference.

    Property order and section structure follow
    implementations/platforms/obsidian/docs/metadata/reference.md and
    the existing Templater template. `status` stays fixed at
    `captured` (Reference's Lifecycle has only one value); `context`
    is independent from `status`, per the same Lifecycle Independence
    invariant established for Project, Area, and Resource.

    `notes` carries an Inbox entry's body when Reference originates
    from Processing, reusing the same mechanism as Project/Area — the
    `Reference` Domain Object stays identity + title only.
    """
    today = today or date.today()
    return {
        "properties": {
            "id": reference.id,
            "note_type": "reference",
            "created": today.isoformat(),
            "updated": today.isoformat(),
            "tags": [],
            "aliases": [],
            "status": "captured",
            "context": OPERATIONAL,
        },
        "title": reference.title,
        "body": BODY_TEMPLATE.format(
            title=reference.title,
            notes=f"\n{nest_under_heading_level(notes, _NOTES_LEVEL)}\n" if notes else "",
        ),
    }


def from_representation(representation: dict[str, Any]) -> Reference:
    """Reconstruct the Reference Domain Object from its Current
    Representation.

    Only identity and title are Domain semantics; status, tags, and
    timestamps remain Metadata/Representation concerns and are not
    part of the Domain Object itself.
    """
    props = representation["properties"]
    return Reference(id=props["id"], title=representation["title"])
