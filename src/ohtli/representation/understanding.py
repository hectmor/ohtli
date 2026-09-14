from __future__ import annotations

from datetime import date
from typing import Any

from ohtli.representation.notes import nest_under_heading_level

_UNDERSTANDING_HEADING = "## Understanding"
_ENTRY_LEVEL = 3  # entries nest as `### {title}` under `## Understanding`


def enrich(
    representation: dict[str, Any],
    *,
    understanding_title: str,
    understanding: str,
    provenance: tuple[str, ...],
    today: date | None = None,
) -> dict[str, Any]:
    """Append one Developed Understanding entry to a note's body.

    Always appends, never overwrites or replaces an existing entry —
    Knowledge is iterative (`Iterative Knowledge`, `Understanding
    Evolves`); refining or revising a specific prior entry is
    deferred.

    Source information and derived understanding must remain
    conceptually distinct (`Source and Derivation Distinction`): the
    entry lives in its own `## Understanding` section, created on
    demand, never mixed into `## Notes` (which already carries
    Inbox-derived source text via Processing).

    Type-agnostic: works identically for Project and Area bodies,
    since it only manipulates the body's text, not any type-specific
    template structure.
    """
    today = today or date.today()
    body = representation["body"]

    nested_understanding = nest_under_heading_level(understanding, _ENTRY_LEVEL)
    provenance_line = "Developed from: " + "; ".join(provenance)
    entry = f"### {understanding_title}\n\n{nested_understanding}\n\n{provenance_line}\n"

    if _UNDERSTANDING_HEADING in body:
        new_body = body.rstrip("\n") + "\n\n" + entry
    else:
        new_body = body.rstrip("\n") + "\n\n" + _UNDERSTANDING_HEADING + "\n\n" + entry

    properties = dict(representation["properties"])
    properties["updated"] = today.isoformat()

    return {**representation, "properties": properties, "body": new_body}
