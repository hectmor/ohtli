from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from typing import Any, Callable

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.event.event import Event
from ohtli.execution.specs import PROJECT, DomainSpec
from ohtli.representation import context as archive_transform
from ohtli.vault_io.events import append_event
from ohtli.vault_io.markdown import read_inbox_entry, resolve_inbox_entry, rewrite_note
from ohtli.workflow import archive as archive_workflow
from ohtli.workflow import capture, processing
from ohtli.workflow import evaluation as evaluation_workflow
from ohtli.workflow.evaluation import OperationalResult


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


def _emit(
    *,
    event_type: str,
    domain_object: Project | Area,
    actor: Actor,
    execution_id: str,
    workflow: str,
    events_dir: Path | None,
) -> Event:
    """Record one Event for a successful operation.

    Shared by every `execute_*` function's single success path, so
    emission logic is never duplicated per workflow. `Event !=
    Current State`: this never influences applicability or any
    returned Domain Object/Representation.
    """
    event = Event(
        event_type=event_type,
        object_id=domain_object.id,
        object_type=type(domain_object).__name__,
        actor=actor.value,
        execution_id=execution_id,
        workflow=workflow,
    )
    append_event(event, events_dir=events_dir)
    return event


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
    event: Event | None


def execute_capture(
    request: ExecutionRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
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
    `events_dir` is the equivalent for the Event log.
    """
    existing_titles = spec.list_existing_titles(base_dir=base_dir)

    if not capture.is_applicable(request.title, existing_titles):
        return ExecutionResult(request=request, applicable=False, project=None, path=None, event=None)

    domain_object = capture.transform(request.title, spec.domain_type)
    representation = spec.to_representation(domain_object)
    path = spec.write(representation, base_dir=base_dir)
    event = _emit(
        event_type=f"{spec.domain_type.__name__} Created",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="capture",
        events_dir=events_dir,
    )

    return ExecutionResult(request=request, applicable=True, project=domain_object, path=path, event=event)


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
    event: Event | None


def execute_processing(
    request: ProcessingRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
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
        return ProcessingResult(request=request, applicable=False, project=None, path=None, event=None)

    domain_object = processing.transform(raw_text, spec.domain_type)
    representation = spec.to_representation(domain_object, notes=processing.derive_notes(raw_text))
    path = spec.write(representation, base_dir=base_dir)
    resolve_inbox_entry(request.entry_path)
    event = _emit(
        event_type=f"{spec.domain_type.__name__} Created",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="processing",
        events_dir=events_dir,
    )

    return ProcessingResult(request=request, applicable=True, project=domain_object, path=path, event=event)


@dataclass(frozen=True)
class ArchiveRequest:
    """Reused for both Archive and Reactivate: `archive-workflow.md`
    states these are two operations of the same workflow, not
    separate workflows, so one Request shape serves both.
    """

    title: str
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class ArchiveResult:
    request: ArchiveRequest
    applicable: bool
    project: Project | Area | None
    path: Path | None
    event: Event | None


def _execute_contextual_transition(
    request: ArchiveRequest,
    *,
    spec: DomainSpec,
    base_dir: Path | None,
    events_dir: Path | None,
    is_applicable: Callable[[str], bool],
    transition: Callable[[dict[str, Any]], dict[str, Any]],
    event_verb: str,
    workflow: str,
) -> ArchiveResult:
    path = spec.file_path(request.title, base_dir=base_dir)
    if not path.exists():
        return ArchiveResult(request=request, applicable=False, project=None, path=None, event=None)

    representation = spec.read(path)
    current_context = representation["properties"].get("context")

    if not is_applicable(current_context):
        return ArchiveResult(request=request, applicable=False, project=None, path=None, event=None)

    updated_representation = transition(representation)
    rewrite_note(path, updated_representation)
    domain_object = spec.from_representation(updated_representation)
    event = _emit(
        event_type=f"{spec.domain_type.__name__} {event_verb}",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow=workflow,
        events_dir=events_dir,
    )

    return ArchiveResult(request=request, applicable=True, project=domain_object, path=path, event=event)


def execute_archive(
    request: ArchiveRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> ArchiveResult:
    """Execute the Archive operation: move a Domain Object from
    operational to historical presence.

    Only `context` (and `updated`) change; `status`, `id`, and the
    file's path are untouched — Archive is not a lifecycle transition
    (`archive-workflow.md`'s Lifecycle Independence invariant).
    """
    return _execute_contextual_transition(
        request,
        spec=spec,
        base_dir=base_dir,
        events_dir=events_dir,
        is_applicable=archive_workflow.is_applicable,
        transition=archive_transform.archive,
        event_verb="Archived",
        workflow="archive",
    )


def execute_reactivate(
    request: ArchiveRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> ArchiveResult:
    """Execute the Reactivate operation: restore operational presence.

    The inverse of `execute_archive`. Does not imply any lifecycle
    transition.
    """
    return _execute_contextual_transition(
        request,
        spec=spec,
        base_dir=base_dir,
        events_dir=events_dir,
        is_applicable=archive_workflow.is_reactivate_applicable,
        transition=archive_transform.reactivate,
        event_verb="Reactivated",
        workflow="reactivate",
    )


_RESULT_VERBS = {
    OperationalResult.PROGRESS: "Progress Observed",
    OperationalResult.MAINTENANCE: "Maintenance Performed",
    OperationalResult.OUTCOME_REACHED: "Outcome Reached",
    OperationalResult.NO_EFFECTIVE_CHANGE: "No Effective Change Observed",
    OperationalResult.DEGRADATION: "Degradation Observed",
}


@dataclass(frozen=True)
class EvaluationRequest:
    title: str
    result: OperationalResult
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class EvaluationResult:
    request: EvaluationRequest
    applicable: bool
    project: Project | Area | None
    path: Path | None
    event: Event | None


def execute_evaluation(
    request: EvaluationRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> EvaluationResult:
    """Execute the Evaluate operation: record the actual operational
    result of work already performed on an actionable Project or Area.

    Evaluate is the only one of Execution's three conceptual
    operations (Select, Act, Evaluate) this function represents —
    Select and Act happen outside Ohtli's code ("Ohtli distinguishes
    performing work from recording that work",
    `execution-workflow.md`). `request.result` is the already-observed
    outcome supplied by the caller, not computed here.

    Unlike Capture/Processing/Archive/Reactivate, this touches no
    representation file: `rewrite_note`/`write_*` are never called.
    Results are not required to exist as stored status values, and
    `status` must never be inferred from a result (Outcome and
    Lifecycle Separation) — only the emitted Event records what
    happened.
    """
    path = spec.file_path(request.title, base_dir=base_dir)
    if not path.exists():
        return EvaluationResult(request=request, applicable=False, project=None, path=None, event=None)

    representation = spec.read(path)
    current_context = representation["properties"].get("context")

    if not evaluation_workflow.is_applicable(current_context, request.result, spec.allowed_results):
        return EvaluationResult(request=request, applicable=False, project=None, path=None, event=None)

    domain_object = spec.from_representation(representation)
    event = _emit(
        event_type=f"{spec.domain_type.__name__} {_RESULT_VERBS[request.result]}",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="evaluation",
        events_dir=events_dir,
    )

    return EvaluationResult(
        request=request, applicable=True, project=domain_object, path=path, event=event
    )
