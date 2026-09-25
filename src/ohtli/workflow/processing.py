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
# This table is that constraint made structural. It holds the 15
# relationships Processing can establish: `Project belongs to Area
# (0..1)`, every `references` and `supports` relationship (`Meeting
# supports Project` is `0..1`, the rest `0..*`), and `Project contains
# Meeting (0..*)`. The 16th, `Area contains Project`, is not here: it is
# derived (see `DERIVED_RELATIONSHIPS`) and can never be established.
#
# Type names are the Domain classes' `__name__` (`JournalEntry`, not
# "Journal Entry"): that is what Execution and the CLI look up.
#
# Every ordered (source type, target type) pair in the Interaction Model
# has exactly one relationship type (verified across all 16 canonical
# relationships), so the pair determines the type. A test pins that
# uniqueness: a future row that breaks it must fail loudly.
CANONICAL_RELATIONSHIPS: tuple[RelationshipDefinition, ...] = (
    RelationshipDefinition("Project", "belongs to", "Area", 1),
    RelationshipDefinition("Project", "references", "Resource", None),
    RelationshipDefinition("Project", "references", "Reference", None),
    RelationshipDefinition("Project", "references", "JournalEntry", None),
    RelationshipDefinition("Resource", "references", "Reference", None),
    RelationshipDefinition("Meeting", "references", "Reference", None),
    RelationshipDefinition("Meeting", "references", "Resource", None),
    RelationshipDefinition("JournalEntry", "references", "Project", None),
    RelationshipDefinition("JournalEntry", "references", "Area", None),
    RelationshipDefinition("JournalEntry", "references", "Resource", None),
    RelationshipDefinition("Reference", "supports", "Project", None),
    RelationshipDefinition("Reference", "supports", "Resource", None),
    RelationshipDefinition("Resource", "supports", "Project", None),
    RelationshipDefinition("Meeting", "supports", "Project", 1),
    RelationshipDefinition("Project", "contains", "Meeting", None),
)


def relationship_definition(
    source_type: str, relationship_type: str, target_type: str | None = None
) -> RelationshipDefinition | None:
    """The canonical definition for a source and relationship type.

    A type can have several targets (`Project references` Resource,
    Reference, Journal Entry), so callers that know the target must
    pass it. Omitting it returns the first match, which is unambiguous
    only for a relationship with a single target type.
    """
    for definition in CANONICAL_RELATIONSHIPS:
        if (
            definition.source_type == source_type
            and definition.relationship_type == relationship_type
            and (target_type is None or definition.target_type == target_type)
        ):
            return definition
    return None


def relationship_for_pair(source_type: str, target_type: str) -> RelationshipDefinition | None:
    """The single relationship defined from one type toward another."""
    for definition in CANONICAL_RELATIONSHIPS:
        if definition.source_type == source_type and definition.target_type == target_type:
            return definition
    return None


@dataclass(frozen=True)
class DerivedRelationshipDefinition:
    """A canonical relationship that is a view over another one.

    It is never stored and never established: `via` is the stored
    relationship it is the complement of, and it is the only place the
    relationship exists. Because there is a single source of truth, the
    two can never contradict each other.
    """

    source_type: str
    relationship_type: str
    target_type: str
    via: RelationshipDefinition


# `interaction-model/README.md` ("Relationship Semantics and Inverses") names
# `Project belongs to Area (0..1)` and `Area contains Project (0..*)` as
# "semantically complementary" and does not require an inverse to be a
# separate stored relationship. The Projects an Area contains are those whose
# `belongs to` targets it. `Project contains Meeting` is NOT here: the spec
# does not declare it complementary to `Meeting supports Project`, so it is an
# independent, stored relationship.
DERIVED_RELATIONSHIPS: tuple[DerivedRelationshipDefinition, ...] = (
    DerivedRelationshipDefinition(
        "Area", "contains", "Project", via=relationship_definition("Project", "belongs to", "Area")
    ),
)


def derived_relationship_for_pair(
    source_type: str, target_type: str
) -> DerivedRelationshipDefinition | None:
    """The derived relationship from one type toward another, if any."""
    for definition in DERIVED_RELATIONSHIPS:
        if definition.source_type == source_type and definition.target_type == target_type:
            return definition
    return None


def is_relate_applicable(
    definition: RelationshipDefinition | None,
    *,
    target_type: str,
    existing_of_type: int,
    already_linked: bool = False,
) -> bool:
    """`Relate` is applicable only for a relationship the Interaction
    Model defines, toward the target type it defines, while the source
    is under the relationship's cardinality, and only if this exact
    source/type/target is not already linked.

    `(source, type, target)` is treated as the semantic identity of a
    relationship: `relationship-representation.md` says instances with an
    equivalent source, type and target *may* have distinct identities and
    defers whether they may coexist to the Interaction Model, which states
    no rule. This is the rule this implementation adopts.

    The target's `context` is deliberately not consulted: an archived
    target is still a valid target (Independent Eligibility,
    `archive-workflow.md`). Existence of the two notes is checked by
    Execution, like every other `execute_*`.
    """
    if definition is None or target_type != definition.target_type or already_linked:
        return False
    return definition.max_targets is None or existing_of_type < definition.max_targets


def is_unrelate_applicable(
    definition: RelationshipDefinition | None,
    *,
    existing_of_type: int,
    target_named: bool = False,
    target_linked: bool = True,
) -> bool:
    """Unlinking is applicable only when there is something to remove.

    A `0..*` relationship can hold many targets, so unlinking it must
    name which one; a `0..1` relationship has at most one, so naming it
    is optional. A named target must actually be linked.
    """
    if definition is None or existing_of_type < 1:
        return False
    if definition.max_targets is None and not target_named:
        return False
    if target_named and not target_linked:
        return False
    return True


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


def derive_title(raw_text: str) -> str | None:
    """The title a raw Inbox entry would become, if any.

    Exposed alongside `derive_notes` so Execution can look up an existing
    object by title on the Update path, before `transform()` runs (Update
    never calls `transform`: the object it acts on already exists).
    """
    return _derive_title(raw_text)


def derive_notes(raw_text: str) -> str | None:
    """The body content of a raw Inbox entry, if any.

    Exposed so Execution can carry the entry's original content into the
    Project's Representation. Kept out of `transform()` so that function
    stays a pure Domain transformation, structurally parallel to
    `capture.transform()`.
    """
    return _split_entry(raw_text)[1]


def is_applicable(raw_text: str) -> bool:
    """Processing is applicable whenever a non-empty title can be derived
    from the entry.

    A derivable title is always actionable: Create when no object of the
    chosen type is named that yet, Update when one already is (`is_update`).
    Only a blank entry (no derivable title) is not applicable. Unlike
    `is_update`, this needs no `existing_titles`: it no longer decides
    between Create and Update, only whether Processing can do anything
    at all.

    Applicability is evaluated independently from, and prior to,
    Execution.
    """
    return _derive_title(raw_text) is not None


def is_create_applicable(*, target_occupied: bool) -> bool:
    """A Create is applicable only if the file its title maps to is free.

    Meaningful once `is_applicable` holds and `is_update` does not. Only
    Create asks this: Update rewrites the note that already holds the path,
    so an occupied path is exactly what it expects. The Update/Create choice
    compares TITLES, so an entry "foo-bar" is a Create while "Foo Bar"
    exists, and would have overwritten `foo-bar.md`. Capture owns the same
    rule; workflows never call each other, so each keeps its own copy.

    Pure: whether the path is occupied is gathered by Execution.
    """
    return not target_occupied


def is_update(raw_text: str, existing_titles: set[str]) -> bool:
    """Whether processing this entry means Update rather than Create:
    true when its derived title already names an existing object of the
    chosen type.

    Meaningful only once `is_applicable` holds; a blank entry (no
    derivable title) is neither Create- nor Update-applicable, and this
    returns `False` for it too.
    """
    title = _derive_title(raw_text)
    return title is not None and title in existing_titles


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
