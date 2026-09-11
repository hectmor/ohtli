from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.representation.area import from_representation as area_from_representation
from ohtli.representation.area import to_representation as area_to_representation
from ohtli.representation.project import from_representation as project_from_representation
from ohtli.representation.project import to_representation as project_to_representation
from ohtli.vault_io import paths
from ohtli.vault_io.markdown import (
    list_existing_area_titles,
    list_existing_titles,
    read_area,
    read_project,
    write_area,
    write_project,
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
