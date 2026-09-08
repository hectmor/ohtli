from __future__ import annotations

import re

_HEADING_RE = re.compile(r"^(#{1,6})(\s.*|)$")
_FENCE_RE = re.compile(r"^(```+|~~~+)")


def nest_under_heading_level(notes: str, heading_level: int) -> str:
    """Shift carried headings deep enough to nest under a heading at
    `heading_level` (e.g. 2 for `## Notes`).

    Content arriving from an Inbox entry may carry its own headings. At
    their original level they would sit as siblings of the target
    section's own template rather than inside it — an entry containing
    `## Objective` would produce a note with two `## Objective`
    headings. Shifting them below the target section keeps the
    template's structure intact.

    Shared by every Domain Object's representation module (`project.py`,
    `area.py`, ...) so this Inbox-carried-content rule is a single class
    of transformation, not duplicated per type.

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

    shift = max(0, (heading_level + 1) - min(level for _, level in headings))
    if not shift:
        return notes

    for index, level in headings:
        lines[index] = "#" * min(6, level + shift) + lines[index][level:]
    return "\n".join(lines)
