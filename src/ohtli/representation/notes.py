from __future__ import annotations

import re
from datetime import date
from typing import Any

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


def append_under_heading(body: str, heading: str, entry_text: str, *, level: int = 2) -> str:
    """Append `entry_text` at the end of the `heading` section in `body`.

    Used by Processing's Update to add an Inbox entry's raw text to an
    existing object's landing section (`## Notes`, `## Discussion` for
    Meeting) without disturbing the sections around it. `entry_text`'s own
    headings are nested below `level` first (`nest_under_heading_level`),
    the same rule Create already applies via `notes=`.

    The insertion point is the next heading at or above `level` after
    `heading`, or the end of the body if `heading` is its last section
    (e.g. Area's `## Notes`). If `heading` is missing — a note written
    before this section existed — it is appended, with the text, at the
    end of the body: nothing is silently dropped.

    Repeated calls accumulate: each call's text lands after whatever the
    previous call left, still inside the same section.
    """
    heading_re = re.compile(rf"^{re.escape(heading)}[ \t]*$", re.MULTILINE)
    nested = nest_under_heading_level(entry_text, level).strip("\n")

    match = heading_re.search(body)
    if match is None:
        return body.rstrip("\n") + "\n\n" + heading + "\n\n" + nested + "\n"

    boundary_re = re.compile(r"^#{1,%d} " % level, re.MULTILINE)
    boundary = boundary_re.search(body, match.end())
    insert_at = boundary.start() if boundary else len(body)

    before = body[:insert_at].rstrip("\n")
    after = body[insert_at:]
    return before + "\n\n" + nested + "\n\n" + after if after else before + "\n\n" + nested + "\n"


def apply_update(
    representation: dict[str, Any], *, heading: str, entry_text: str, today: date | None = None
) -> dict[str, Any]:
    """Processing's Update: append `entry_text` under `heading` and record
    when it happened.

    Mirrors `understanding.enrich`'s shape: only `body` and `updated`
    change. `id` and everything else in `properties` are untouched
    (`Identity Preservation`, processing-workflow.md: "Updating an
    existing object never changes its identity").
    """
    today = today or date.today()
    new_body = append_under_heading(representation["body"], heading, entry_text)
    properties = dict(representation["properties"])
    properties["updated"] = today.isoformat()
    return {**representation, "properties": properties, "body": new_body}
