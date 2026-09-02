from __future__ import annotations

import re
from datetime import date
from typing import Any

from ohtli.domain.project import Project

_HEADING_RE = re.compile(r"^(#{1,6})(\s.*|)$")
_FENCE_RE = re.compile(r"^(```+|~~~+)")

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


def _nest_under_notes(notes: str) -> str:
    """Shift carried headings deep enough to nest under `## Notes`.

    Content arriving from an Inbox entry may carry its own headings. At
    their original level they would sit as siblings of the template's
    own sections rather than inside `## Notes` — an entry containing
    `## Objective` would produce a note with two `## Objective`
    headings. Shifting them below `## Notes` keeps the template's
    structure intact.

    The shift is uniform, so the body's relative heading structure is
    preserved, and headings already deep enough are left alone. Headings
    inside fenced code blocks are untouched: a `# comment` in a pasted
    snippet is code, not structure.
    """
    lines = notes.split("\n")
    headings: list[tuple[int, int]] = []
    fence: str | None = None

    for index, line in enumerate(lines):
        fence_match = _FENCE_RE.match(line.strip())
        if fence_match:
            marker = fence_match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        heading_match = _HEADING_RE.match(line)
        if heading_match:
            headings.append((index, len(heading_match.group(1))))

    if not headings:
        return notes

    shift = max(0, (_NOTES_LEVEL + 1) - min(level for _, level in headings))
    if not shift:
        return notes

    for index, level in headings:
        lines[index] = "#" * min(6, level + shift) + lines[index][level:]
    return "\n".join(lines)


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
            title=project.title, notes=f"\n{_nest_under_notes(notes)}\n" if notes else ""
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
