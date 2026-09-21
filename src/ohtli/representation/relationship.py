from __future__ import annotations

import uuid
from datetime import date
from typing import Any

RELATIONSHIPS_KEY = "relationships"


def relationships_of_type(
    representation: dict[str, Any], relationship_type: str
) -> list[dict[str, Any]]:
    """The Current Relationship Set entries of one canonical type.

    A note that was never linked has no `relationships` key at all
    (`Relationship Absence` is not a Relationship State), so this is an
    empty list, not an error.
    """
    entries = representation["properties"].get(RELATIONSHIPS_KEY) or []
    return [entry for entry in entries if entry.get("type") == relationship_type]


def relate(
    representation: dict[str, Any],
    *,
    relationship_type: str,
    target_id: str,
    target_type: str,
    target_link: str,
    relationship_id: str | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    """Add one Relationship Instance to a note's Current Relationship Set.

    Modelled as a set of instances, not a state field
    (`relationship-representation.md`: `Relationship != State
    Dimension`). Every instance has its own identity, separate from
    the identity of either object it connects. The source is implicit —
    it is the note itself.

    `target_id` is the authority (stable identity survives rename and
    relocation). `target_link` is display-only decoration: nothing reads
    it back, and removing it loses no information.

    Pure: returns a new representation and never mutates its input. Only
    `relationships` and `updated` change — `status`, `context`, and `id`
    are untouched, because a link is not a lifecycle or presence change.
    """
    today = today or date.today()
    properties = dict(representation["properties"])
    entries = list(properties.get(RELATIONSHIPS_KEY) or [])
    entries.append(
        {
            "id": relationship_id or str(uuid.uuid4()),
            "type": relationship_type,
            "target_id": target_id,
            "target_type": target_type,
            "target_link": target_link,
        }
    )
    properties[RELATIONSHIPS_KEY] = entries
    properties["updated"] = today.isoformat()
    return {**representation, "properties": properties}


def unrelate(
    representation: dict[str, Any], *, relationship_type: str, today: date | None = None
) -> dict[str, Any]:
    """Remove every Relationship Instance of one type from a note.

    When the removed instance was the last one, the `relationships` key
    is removed entirely, returning the note to exactly the shape of a
    never-linked one. Pure: never mutates its input.
    """
    today = today or date.today()
    properties = dict(representation["properties"])
    remaining = [
        entry
        for entry in (properties.get(RELATIONSHIPS_KEY) or [])
        if entry.get("type") != relationship_type
    ]
    if remaining:
        properties[RELATIONSHIPS_KEY] = remaining
    else:
        properties.pop(RELATIONSHIPS_KEY, None)
    properties["updated"] = today.isoformat()
    return {**representation, "properties": properties}
