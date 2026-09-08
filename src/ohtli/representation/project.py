from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.project import Project
from ohtli.representation.notes import nest_under_heading_level

_NOTES_LEVEL = 2  # `## Notes` — carried content must nest below it

BODY_TEMPLATE = """# {title}

## Objective

## Scope

## Deliverables

## Tasks

## Notes
{notes}
## References
"""


def to_representation(
    project: Project, *, today: date | None = None, notes: str | None = None
) -> dict[str, Any]:
    """Build the Current Representation for a Project.

    Property order and section structure follow
    implementations/platforms/obsidian/docs/templates/template-structure.md
    and implementations/platforms/obsidian/docs/metadata/project.md.

    `notes` is optional free-form content for the `## Notes` section,
    used when a Project originates from an Inbox entry that already
    carried a body. It is a Representation concern, not Domain
    semantics: the `Project` Domain Object stays identity + title only.
    Omitting it reproduces the blank template exactly.
    """
    today = today or date.today()
    return {
        "properties": {
            "id": project.id,
            "note_type": "project",
            "created": today.isoformat(),
            "updated": today.isoformat(),
            "tags": [],
            "aliases": [],
            "status": "planned",
        },
        "title": project.title,
        "body": BODY_TEMPLATE.format(
            title=project.title,
            notes=f"\n{nest_under_heading_level(notes, _NOTES_LEVEL)}\n" if notes else "",
        ),
    }


def from_representation(representation: dict[str, Any]) -> Project:
    """Reconstruct the Project Domain Object from its Current Representation.

    Only identity and title are Domain semantics; status, tags, and
    timestamps remain Metadata/Representation concerns and are not
    part of the Domain Object itself.
    """
    props = representation["properties"]
    return Project(id=props["id"], title=representation["title"])
