from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.meeting import Meeting
from ohtli.representation.context import OPERATIONAL
from ohtli.representation.notes import nest_under_heading_level

_DISCUSSION_LEVEL = 2  # `## Discussion` — carried content must nest below it

BODY_TEMPLATE = """# {title}

## Objective

## Participants

## Agenda

## Discussion
{notes}
## Decisions

## Action Items

## References
"""


def to_representation(
    meeting: Meeting, *, today: date | None = None, notes: str | None = None
) -> dict[str, Any]:
    """Build the Current Representation for a Meeting.

    Property order and section structure follow
    implementations/platforms/obsidian/docs/metadata/meeting.md and
    the existing Templater template. `status` stays fixed at
    `recorded` (Meeting's Lifecycle has only one value once `Archived`
    is removed, per Lifecycle Independence); `context` is independent
    from `status`, per the same invariant established for Project,
    Area, Resource, and Reference.

    `notes` carries an Inbox entry's body when Meeting originates from
    Processing, landing under `## Discussion` — the template section
    no Essential Attribute or Responsibility claims (unlike Resource's
    `## Content`, which is claimed and therefore excluded Processing
    in Phase 18). Reuses the same mechanism as Project/Area/Reference;
    the `Meeting` Domain Object stays identity + title only.
    """
    today = today or date.today()
    return {
        "properties": {
            "id": meeting.id,
            "note_type": "meeting",
            "created": today.isoformat(),
            "updated": today.isoformat(),
            "tags": [],
            "aliases": [],
            "status": "recorded",
            "context": OPERATIONAL,
        },
        "title": meeting.title,
        "body": BODY_TEMPLATE.format(
            title=meeting.title,
            notes=f"\n{nest_under_heading_level(notes, _DISCUSSION_LEVEL)}\n" if notes else "",
        ),
    }


def from_representation(representation: dict[str, Any]) -> Meeting:
    """Reconstruct the Meeting Domain Object from its Current
    Representation.

    Only identity and title are Domain semantics; status, tags, and
    timestamps remain Metadata/Representation concerns and are not
    part of the Domain Object itself.
    """
    props = representation["properties"]
    return Meeting(id=props["id"], title=representation["title"])
