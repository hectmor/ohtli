from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ohtli.domain.area import Area
from ohtli.domain.meeting import Meeting
from ohtli.domain.project import Project
from ohtli.domain.reference import Reference
from ohtli.domain.resource import Resource
from ohtli.representation.area import from_representation as area_from_representation
from ohtli.representation.area import to_representation as area_to_representation
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
    list_existing_meeting_titles,
    list_existing_reference_titles,
    list_existing_resource_titles,
    list_existing_titles,
    read_area,
    read_meeting,
    read_project,
    read_reference,
    read_resource,
    write_area,
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
    to_representation: Callable[..., dict[str, Any]]
    from_representation: Callable[[dict[str, Any]], Any]
    write: Callable[..., Path]
    read: Callable[[Path], dict[str, Any]]
    file_path: Callable[..., Path]
    list_existing_titles: Callable[..., set[str]]
    allowed_results: frozenset[OperationalResult]


PROJECT = DomainSpec(
    domain_type=Project,
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
