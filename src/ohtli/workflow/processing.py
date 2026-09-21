from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeVar

from ohtli.domain.project import Project

T = TypeVar("T")


@dataclass(frozen=True)
class RelationshipDefinition:
    """One relationship the Interaction Model defines.

    `max_targets` is the cardinality's upper bound (`None` = unbounded).
    """

    source_type: str
    relationship_type: str
    target_type: str
    max_targets: int | None


# `processing-workflow.md`, "Interaction Constrained": Processing may
# establish only relationships already defined by the Interaction Model.
# This table is that constraint made structural. One row for now: the
# first slice of the Interaction Model (Project belongs to Area, 0..1).
CANONICAL_RELATIONSHIPS: tuple[RelationshipDefinition, ...] = (
    RelationshipDefinition("Project", "belongs to", "Area", 1),
)


def relationship_definition(
    source_type: str, relationship_type: str
) -> RelationshipDefinition | None:
    for definition in CANONICAL_RELATIONSHIPS:
        if definition.source_type == source_type and definition.relationship_type == relationship_type:
            return definition
    return None


def is_relate_applicable(
    definition: RelationshipDefinition | None, *, target_type: str, existing_of_type: int
) -> bool:
    """`Relate` is applicable only for a relationship the Interaction
    Model defines, toward the target type it defines, and only while the
    source is under the relationship's cardinality (0..1 for `belongs
    to`, so a second link is refused).

    The target's `context` is deliberately not consulted: an archived
    target is still a valid target (Independent Eligibility,
    `archive-workflow.md`). Existence of the two notes is checked by
    Execution, like every other `execute_*`.
    """
    if definition is None or target_type != definition.target_type:
        return False
    return definition.max_targets is None or existing_of_type < definition.max_targets


def is_unrelate_applicable(definition: RelationshipDefinition | None, *, existing_of_type: int) -> bool:
    """Unlinking is applicable only when there is something to remove."""
    return definition is not None and existing_of_type >= 1


def _split_entry(raw_text: str) -> tuple[str | None, str | None]:
    """Split a raw Inbox entry into the title it would become and the
    body content that follows it.

    The title is the first non-empty line, with any leading markdown
    heading marks and surrounding whitespace stripped. The notes are
    everything after that line. Either is None when absent. Both are
    derived in a single pass so they can never disagree about where the
    title ends and the body begins.
    """
    lines = raw_text.splitlines()
    for index, line in enumerate(lines):
        title = line.strip().lstrip("#").strip()
        if title:
            notes = "\n".join(lines[index + 1 :]).strip()
            return title, notes or None
    return None, None


def _derive_title(raw_text: str) -> str | None:
    return _split_entry(raw_text)[0]


def derive_notes(raw_text: str) -> str | None:
    """The body content of a raw Inbox entry, if any.

    Exposed so Execution can carry the entry's original content into the
    Project's Representation. Kept out of `transform()` so that function
    stays a pure Domain transformation, structurally parallel to
    `capture.transform()`.
    """
    return _split_entry(raw_text)[1]


def is_applicable(raw_text: str, existing_titles: set[str]) -> bool:
    """Processing is applicable only if a non-empty title can be derived
    from the entry, and no Project with that title already exists.

    Applicability is evaluated independently from, and prior to,
    Execution.
    """
    title = _derive_title(raw_text)
    return title is not None and title not in existing_titles


def transform(raw_text: str, domain_factory: Callable[..., T] = Project) -> T:
    """The Processing transformation: interpret an existing Inbox entry
    as a new Domain Object.

    This function does not check applicability and does not persist
    anything, or touch the Inbox entry itself. It is a pure
    transformation, called only after applicability has already been
    confirmed by the caller.

    `domain_factory` defaults to `Project` (Phase 10/11 behavior,
    unchanged), and generalizes the same way as `capture.transform`.
    """
    return domain_factory(title=_derive_title(raw_text))
