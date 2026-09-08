from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.execution.specs import PROJECT, DomainSpec
from ohtli.vault_io.markdown import read_inbox_entry, resolve_inbox_entry
from ohtli.workflow import capture, processing


class Actor(Enum):
    """The four structurally equivalent Actor kinds (ADR-0004).

    No function in this module branches on which Actor kind is
    passed. Actor participates only as context attached to the
    Execution Request.
    """

    HUMAN = "human"
    DETERMINISTIC = "deterministic"
    AI_ASSISTED = "ai_assisted"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class ExecutionRequest:
    title: str
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class ExecutionResult:
    request: ExecutionRequest
    applicable: bool
    project: Project | Area | None
    path: Path | None


def execute_capture(
    request: ExecutionRequest, *, spec: DomainSpec = PROJECT, base_dir: Path | None = None
) -> ExecutionResult:
    """Execute the Capture workflow for a single Domain Object title.

    Request != Execution: this function represents the occurrence.
    Applicability is checked before any transformation or persistence
    happens, and is fully independent of `request.actor`.

    `spec` selects which Domain Object Capture is preserving (defaults
    to `Project`, Phase 10 behavior unchanged); this is what lets
    Capture stay a single class of transformation instead of one
    function per Domain Object, per the Workflow Model.

    `base_dir` defaults to the real vault; tests pass a temporary
    directory so they never touch the user's actual vault content.
    """
    existing_titles = spec.list_existing_titles(base_dir=base_dir)

    if not capture.is_applicable(request.title, existing_titles):
        return ExecutionResult(request=request, applicable=False, project=None, path=None)

    domain_object = capture.transform(request.title, spec.domain_type)
    representation = spec.to_representation(domain_object)
    path = spec.write(representation, base_dir=base_dir)

    return ExecutionResult(request=request, applicable=True, project=domain_object, path=path)


@dataclass(frozen=True)
class ProcessingRequest:
    entry_path: Path
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class ProcessingResult:
    request: ProcessingRequest
    applicable: bool
    project: Project | Area | None
    path: Path | None


def execute_processing(
    request: ProcessingRequest, *, spec: DomainSpec = PROJECT, base_dir: Path | None = None
) -> ProcessingResult:
    """Execute the Processing workflow for a single Inbox entry.

    Request != Execution: this function represents the occurrence.
    Applicability is checked before any transformation or persistence
    happens, and is fully independent of `request.actor`.

    `processing.py` is never called from `capture.py` and vice versa
    (workflows do not invoke each other); this function implements its
    own applicability/transform logic, dispatched onto whichever Domain
    Object's representation and vault_io persistence `spec` selects
    (defaults to `Project`, Phase 10/11 behavior unchanged).

    `base_dir` defaults to the real vault's projects directory; tests
    pass a temporary directory so they never touch the user's actual
    vault content.
    """
    raw_text = read_inbox_entry(request.entry_path)
    existing_titles = spec.list_existing_titles(base_dir=base_dir)

    if not processing.is_applicable(raw_text, existing_titles):
        return ProcessingResult(request=request, applicable=False, project=None, path=None)

    domain_object = processing.transform(raw_text, spec.domain_type)
    representation = spec.to_representation(domain_object, notes=processing.derive_notes(raw_text))
    path = spec.write(representation, base_dir=base_dir)
    resolve_inbox_entry(request.entry_path)

    return ProcessingResult(request=request, applicable=True, project=domain_object, path=path)
