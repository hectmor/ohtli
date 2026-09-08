from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.area import Area
from ohtli.representation.notes import nest_under_heading_level

_NOTES_LEVEL = 2  # `## Notes` — carried content must nest below it

BODY_TEMPLATE = """# {title}

## Purpose

## Responsibilities

## Goals

## Resources

## Active Projects

## Notes
{notes}"""


def to_representation(
    area: Area, *, today: date | None = None, notes: str | None = None
) -> dict[str, Any]:
    """Build the Current Representation for an Area.

    Property order and section structure follow
    implementations/platforms/obsidian/docs/metadata/area.md.

    `status` here is Area's lifecycle (Active/Archived, per the
    canonical Domain Model), not Project's progress-oriented `status`
    enum — same property name, different domain semantics, entirely a
    Representation concern.
    """
    today = today or date.today()
    return {
        "properties": {
            "id": area.id,
            "note_type": "area",
            "created": today.isoformat(),
            "updated": today.isoformat(),
            "tags": [],
            "aliases": [],
            "status": "active",
        },
        "title": area.title,
        "body": BODY_TEMPLATE.format(
            title=area.title,
            notes=f"\n{nest_under_heading_level(notes, _NOTES_LEVEL)}\n" if notes else "",
        ),
    }


def from_representation(representation: dict[str, Any]) -> Area:
    """Reconstruct the Area Domain Object from its Current Representation.

    Only identity and title are Domain semantics; status, tags, and
    timestamps remain Metadata/Representation concerns and are not
    part of the Domain Object itself.
    """
    props = representation["properties"]
    return Area(id=props["id"], title=representation["title"])
