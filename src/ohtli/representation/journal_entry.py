from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.journal_entry import JournalEntry
from ohtli.representation.context import OPERATIONAL
from ohtli.representation.notes import nest_under_heading_level

_NOTES_LEVEL = 2  # `## Notes` — carried content must nest below it

BODY_TEMPLATE = """# {title}

## Ideas

## Reflections

## Observations

## Notes
{notes}
## References
"""


def to_representation(
    entry: JournalEntry, *, today: date | None = None, notes: str | None = None
) -> dict[str, Any]:
    """Build the Current Representation for a Journal Entry.

    Sections mirror the Domain Model's three Responsibilities (capture
    ideas / reflections / observations); Content is claimed collectively
    by those three, so there is deliberately no `## Content` section.
    `status` stays fixed at `created` (the single Lifecycle value);
    `context` is independent from `status`, per Lifecycle Independence.

    The Domain Model's Essential Attribute `Date` maps to `created`
    (Capture-time "today"). Known limitation: a backdated entry has a
    `created` that differs from the moment in its title.

    `notes` carries an Inbox entry's body when a Journal Entry
    originates from Processing, landing under `## Notes` — the section
    no Essential Attribute or Responsibility claims.
    """
    today = today or date.today()
    return {
        "properties": {
            "id": entry.id,
            "note_type": "journal_entry",
            "created": today.isoformat(),
            "updated": today.isoformat(),
            "tags": [],
            "aliases": [],
            "status": "created",
            "context": OPERATIONAL,
        },
        "title": entry.title,
        "body": BODY_TEMPLATE.format(
            title=entry.title,
            notes=f"\n{nest_under_heading_level(notes, _NOTES_LEVEL)}\n" if notes else "",
        ),
    }


def from_representation(representation: dict[str, Any]) -> JournalEntry:
    """Reconstruct the Journal Entry Domain Object from its Current
    Representation.

    Only identity and title are Domain semantics here; status, tags, and
    timestamps remain Metadata/Representation concerns.
    """
    props = representation["properties"]
    return JournalEntry(id=props["id"], title=representation["title"])
