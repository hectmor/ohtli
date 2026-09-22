from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ohtli.domain.area import Area
from ohtli.domain.journal_entry import JournalEntry
from ohtli.domain.meeting import Meeting
from ohtli.domain.project import Project
from ohtli.domain.reference import Reference
from ohtli.domain.resource import Resource
from ohtli.representation.area import from_representation as area_from_representation
from ohtli.representation.area import to_representation as area_to_representation
from ohtli.representation.journal_entry import from_representation as journal_entry_from_representation
from ohtli.representation.journal_entry import to_representation as journal_entry_to_representation
from ohtli.representation.meeting import from_representation as meeting_from_representation
from ohtli.representation.meeting import to_representation as meeting_to_representation
from ohtli.representation.project import from_representation as project_from_representation
from ohtli.representation.project import to_representation as project_to_representation
from ohtli.representation.reference import from_representation as reference_from_representation
from ohtli.representation.reference import to_representation as reference_to_representation
from ohtli.representation.resource import from_representation as resource_from_representation
from ohtli.representation.resource import to_representation as resource_to_representation
from ohtli.vault_io import paths
from ohtli.vault_io.markdown import (
    list_existing_area_titles,
    list_existing_journal_entry_titles,
    list_existing_meeting_titles,
    list_existing_reference_titles,
    list_existing_resource_titles,
    list_existing_titles,
    read_area,
    read_journal_entry,
    read_meeting,
    read_project,
    read_reference,
    read_resource,
    write_area,
    write_journal_entry,
    write_meeting,
    write_project,
    write_reference,
    write_resource,
)
from ohtli.workflow.evaluation import OperationalResult


@dataclass(frozen=True)
class DomainSpec:
    """Bundles the per-Domain-Object pieces Capture, Processing, and
    Archive need (construction, representation, persistence,
    applicability lookup, existing-note lookup), so `execution.py`
    stays generic across Domain Objects instead of growing a duplicate
    `execute_*` function per type.
    """

    domain_type: type
    # The representation's `note_type` value (e.g. `journal_entry`). Used where
    # a relationship records the kind of its target, instead of guessing it
    # from the Python class name (`JournalEntry`.lower() != `journal_entry`).
    note_type: str
    # The Domain Object's name as the Event Model writes it in event names
    # ("Journal Entry Created"), as opposed to the Python class name
    # (`JournalEntry`) that identifies the type in code and in `object_type`.
    display_name: str
    # The heading Processing's Update appends new Inbox-derived text under
    # (`representation/notes.py::append_under_heading`) — the same section
    # Create already carries `notes=` into. Explicit, not derived from the
    # body template: every type but Meeting uses `## Notes`.
    notes_heading: str
    to_representation: Callable[..., dict[str, Any]]
    from_representation: Callable[[dict[str, Any]], Any]
    write: Callable[..., Path]
    read: Callable[[Path], dict[str, Any]]
    file_path: Callable[..., Path]
    list_existing_titles: Callable[..., set[str]]
    allowed_results: frozenset[OperationalResult]


PROJECT = DomainSpec(
    domain_type=Project,
    note_type="project",
    display_name="Project",
    notes_heading="## Notes",
    to_representation=project_to_representation,
    from_representation=project_from_representation,
    write=write_project,
    read=read_project,
    file_path=paths.project_file_path,
    list_existing_titles=list_existing_titles,
    allowed_results=frozenset(
        {
            OperationalResult.PROGRESS,
            OperationalResult.OUTCOME_REACHED,
            OperationalResult.NO_EFFECTIVE_CHANGE,
            OperationalResult.DEGRADATION,
        }
    ),
)

AREA = DomainSpec(
    domain_type=Area,
    note_type="area",
    display_name="Area",
    notes_heading="## Notes",
    to_representation=area_to_representation,
    from_representation=area_from_representation,
    write=write_area,
    read=read_area,
    file_path=paths.area_file_path,
    list_existing_titles=list_existing_area_titles,
    allowed_results=frozenset(
        {
            OperationalResult.MAINTENANCE,
            OperationalResult.NO_EFFECTIVE_CHANGE,
            OperationalResult.DEGRADATION,
        }
    ),
)

RESOURCE = DomainSpec(
    domain_type=Resource,
    note_type="resource",
    display_name="Resource",
    notes_heading="## Notes",
    to_representation=resource_to_representation,
    from_representation=resource_from_representation,
    write=write_resource,
    read=read_resource,
    file_path=paths.resource_file_path,
    list_existing_titles=list_existing_resource_titles,
    # Resource is not an Execution target (execution-workflow.md's
    # Related Domain Objects list); an empty set makes execute_evaluation
    # always not-applicable for Resource with zero branching in
    # execution.py, the same mechanism Phase 15 used for narrower
    # exclusions (Area excluding only Outcome Reached).
    allowed_results=frozenset(),
)

REFERENCE = DomainSpec(
    domain_type=Reference,
    note_type="reference",
    display_name="Reference",
    notes_heading="## Notes",
    to_representation=reference_to_representation,
    from_representation=reference_from_representation,
    write=write_reference,
    read=read_reference,
    file_path=paths.reference_file_path,
    list_existing_titles=list_existing_reference_titles,
    # Reference is not an Execution target either, same as Resource.
    allowed_results=frozenset(),
)

MEETING = DomainSpec(
    domain_type=Meeting,
    note_type="meeting",
    display_name="Meeting",
    notes_heading="## Discussion",
    to_representation=meeting_to_representation,
    from_representation=meeting_from_representation,
    write=write_meeting,
    read=read_meeting,
    file_path=paths.meeting_file_path,
    list_existing_titles=list_existing_meeting_titles,
    # Meeting may participate in Execution through coordination but is
    # not itself an execution target (execution-workflow.md).
    allowed_results=frozenset(),
)

JOURNAL_ENTRY = DomainSpec(
    domain_type=JournalEntry,
    note_type="journal_entry",
    display_name="Journal Entry",
    notes_heading="## Notes",
    to_representation=journal_entry_to_representation,
    from_representation=journal_entry_from_representation,
    write=write_journal_entry,
    read=read_journal_entry,
    file_path=paths.journal_entry_file_path,
    list_existing_titles=list_existing_journal_entry_titles,
    # Journal Entry is not an Execution target (execution-workflow.md's
    # Related Domain Objects list).
    allowed_results=frozenset(),
)


ALL_SPECS: tuple[DomainSpec, ...] = (PROJECT, AREA, RESOURCE, REFERENCE, MEETING, JOURNAL_ENTRY)


def display_name_of(type_name: str) -> str:
    """The display name for a Domain class name (`JournalEntry` -> `Journal Entry`).

    Event names use this, not the class name. An unknown name raises instead
    of falling back to the class name: a silent fallback would reintroduce the
    exact leak (`JournalEntry`) this exists to prevent.
    """
    for spec in ALL_SPECS:
        if spec.domain_type.__name__ == type_name:
            return spec.display_name
    raise KeyError(f"no Domain Object spec is named {type_name!r}")


def spec_by_note_type(note_type: str) -> DomainSpec:
    """The spec for a `note_type` value (e.g. `"project"`).

    A relationship instance stores its target's kind as this string
    (`relationship-representation.md`'s `target_type`), not a class name, so
    resolving it back to a directory/spec needs this lookup rather than
    `display_name_of`'s. Raises on an unknown value for the same reason
    `display_name_of` does: silently returning nothing would hide a real bug.
    """
    for spec in ALL_SPECS:
        if spec.note_type == note_type:
            return spec
    raise KeyError(f"no Domain Object spec has note_type {note_type!r}")
