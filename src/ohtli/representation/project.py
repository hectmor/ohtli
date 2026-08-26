from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.domain.project import Project

BODY_TEMPLATE = """# {title}

## Objective

## Scope

## Deliverables

## Tasks

## Notes

## References
"""


def to_representation(project: Project, *, today: date | None = None) -> dict[str, Any]:
    """Build the Current Representation for a Project.

    Property order and section structure follow
    implementations/platforms/obsidian/docs/templates/template-structure.md
    and implementations/platforms/obsidian/docs/metadata/project.md.
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
        "body": BODY_TEMPLATE.format(title=project.title),
    }


def from_representation(representation: dict[str, Any]) -> Project:
    """Reconstruct the Project Domain Object from its Current Representation.

    Only identity and title are Domain semantics; status, tags, and
    timestamps remain Metadata/Representation concerns and are not
    part of the Domain Object itself.
    """
    props = representation["properties"]
    return Project(id=props["id"], title=representation["title"])
