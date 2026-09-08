from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.representation.area import to_representation as area_to_representation
from ohtli.representation.project import to_representation as project_to_representation
from ohtli.vault_io.markdown import (
    list_existing_area_titles,
    list_existing_titles,
    write_area,
    write_project,
)


@dataclass(frozen=True)
class DomainSpec:
    """Bundles the per-Domain-Object pieces Capture and Processing need
    (construction, representation, persistence, applicability lookup),
    so `execution.py` stays generic across Domain Objects instead of
    growing a duplicate `execute_capture`/`execute_processing` per type.
    """

    domain_type: type
    to_representation: Callable[..., dict[str, Any]]
    write: Callable[..., Path]
    list_existing_titles: Callable[..., set[str]]


PROJECT = DomainSpec(
    domain_type=Project,
    to_representation=project_to_representation,
    write=write_project,
    list_existing_titles=list_existing_titles,
)

AREA = DomainSpec(
    domain_type=Area,
    to_representation=area_to_representation,
    write=write_area,
    list_existing_titles=list_existing_area_titles,
)
