from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from typing import Any, Callable

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.event.event import Event
from ohtli.execution.specs import AREA, PROJECT, DomainSpec
from ohtli.representation import context as archive_transform
from ohtli.representation import relationship as relationship_transform
from ohtli.representation import understanding as understanding_transform
from ohtli.vault_io.events import append_event, read_events
from ohtli.vault_io.markdown import read_inbox_entry, resolve_inbox_entry, rewrite_note
from ohtli.workflow import archive as archive_workflow
from ohtli.workflow import capture, processing
from ohtli.workflow import evaluation as evaluation_workflow
from ohtli.workflow import knowledge as knowledge_workflow
from ohtli.workflow import review as review_workflow
from ohtli.workflow.evaluation import OperationalResult
from ohtli.workflow.review import ReviewAssessment, ReviewConclusion


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
    target_id: str | None = None,
) -> Event:
    """Record one Event for a successful operation.

    Shared by every `execute_*` function's single success path, so
    emission logic is never duplicated per workflow. `Event !=
    Current State`: this never influences applicability or any
    returned Domain Object/Representation.

    `target_id` is set only by Relationship Events, naming the other
    end of the relationship; every other operation leaves it `None`.
    """
    event = Event(
        event_type=event_type,
        object_id=domain_object.id,
        object_type=type(domain_object).__name__,
        actor=actor.value,
        execution_id=execution_id,
        workflow=workflow,
        target_id=target_id,
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


_CONCLUSION_VERBS = {
    ReviewConclusion.ATTENTION_REQUIRED: "Attention Identified",
    ReviewConclusion.NO_ATTENTION_REQUIRED: "No Attention Identified",
    ReviewConclusion.INSUFFICIENT_BASIS: "Insufficient Assessment Basis Identified",
}


@dataclass(frozen=True)
class ReviewRequest:
    title: str
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    since: str | None = None


@dataclass(frozen=True)
class ReviewResult:
    request: ReviewRequest
    applicable: bool
    project: Project | Area | None
    path: Path | None
    event: Event | None
    assessment: ReviewAssessment | None


def execute_review(
    request: ReviewRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> ReviewResult:
    """Execute the Review workflow for a single named Project or Area.

    Unlike Evaluate, applicability requires only that the target
    exists -- archived and completed objects remain reviewable
    (`review-workflow.md`'s "Review and Archive"). Observe and Assess
    are real, deterministic code here: unlike Execution's Act,
    Review's entire input (the note plus its Event history) already
    exists in code.

    Touches no representation file. `request.since`, when given,
    bounds which Events are considered relevant to this Review's
    temporal context.
    """
    path = spec.file_path(request.title, base_dir=base_dir)
    if not path.exists():
        return ReviewResult(
            request=request, applicable=False, project=None, path=None, event=None, assessment=None
        )

    representation = spec.read(path)
    domain_object = spec.from_representation(representation)

    all_events = read_events(events_dir=events_dir)
    observed = review_workflow.observe(all_events, domain_object.id, request.since)
    evaluation_events = [e for e in observed if e.workflow == "evaluation"]
    assessment = review_workflow.assess(representation["properties"], evaluation_events)

    event = _emit(
        event_type=f"{spec.domain_type.__name__} {_CONCLUSION_VERBS[assessment.conclusion]}",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="review",
        events_dir=events_dir,
    )

    return ReviewResult(
        request=request, applicable=True, project=domain_object, path=path, event=event, assessment=assessment
    )


@dataclass(frozen=True)
class KnowledgeRequest:
    title: str
    understanding_title: str
    understanding: str
    provenance: tuple[str, ...]
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class KnowledgeResult:
    request: KnowledgeRequest
    applicable: bool
    project: Project | Area | None
    path: Path | None
    event: Event | None


def execute_knowledge(
    request: KnowledgeRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> KnowledgeResult:
    """Execute Knowledge's Externalize operation: enrich an existing
    Project or Area with Developed Understanding supplied by the
    caller.

    Explore/Extract/Connect/Synthesize happen outside Ohtli's code
    (mirroring Execution's Act) -- the actor supplies the
    already-developed understanding, mirroring Evaluate's
    already-observed result. Unlike Evaluate/Review, this DOES write
    to the representation: Externalize's own definition is enriching
    an existing object, and Epistemic Provenance is only testable
    against a persisted representation.
    """
    path = spec.file_path(request.title, base_dir=base_dir)
    if not path.exists():
        return KnowledgeResult(request=request, applicable=False, project=None, path=None, event=None)

    if not knowledge_workflow.is_applicable(request.understanding, request.provenance):
        return KnowledgeResult(request=request, applicable=False, project=None, path=None, event=None)

    representation = spec.read(path)
    enriched_representation = understanding_transform.enrich(
        representation,
        understanding_title=request.understanding_title,
        understanding=request.understanding,
        provenance=request.provenance,
    )
    rewrite_note(path, enriched_representation)
    domain_object = spec.from_representation(enriched_representation)

    event = _emit(
        event_type=f"{spec.domain_type.__name__} Knowledge Enriched",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="knowledge",
        events_dir=events_dir,
    )

    return KnowledgeResult(request=request, applicable=True, project=domain_object, path=path, event=event)


def _link_display(target_path: Path, target_title: str) -> str:
    """A display-only, folder-qualified wikilink to the target note.

    Folder-qualified so two notes with the same slug in different
    folders (a Project and an Area both called "health") stay
    unambiguous. Non-authoritative: `target_id` is the authority, and no
    `execute_*` ever reads this back.
    """
    return f"[[{target_path.parent.name}/{target_path.stem}|{target_title}]]"


@dataclass(frozen=True)
class RelateRequest:
    source_title: str
    target_title: str
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    relationship_type: str = "belongs to"


@dataclass(frozen=True)
class UnrelateRequest:
    source_title: str
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    relationship_type: str = "belongs to"


@dataclass(frozen=True)
class RelationshipResult:
    request: RelateRequest | UnrelateRequest
    applicable: bool
    source: Project | Area | None
    path: Path | None
    event: Event | None


def execute_relate(
    request: RelateRequest,
    *,
    source_spec: DomainSpec = PROJECT,
    target_spec: DomainSpec = AREA,
    base_dir: Path | None = None,
    target_base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> RelationshipResult:
    """Execute Processing's `Relate` operation: establish a semantic
    relationship between two existing Domain Objects
    (`processing-workflow.md`).

    Both notes must exist. Which relationships are allowed, toward which
    target type, and how many, is decided by the canonical table in
    `workflow/processing.py` — Processing may establish only
    relationships the Interaction Model defines. The relationship is
    stored on the source note only (the inverse is not stored) and
    references the target by its stable `id`.

    `base_dir` is the source's directory and `target_base_dir` the
    target's; both default to the real vault, and tests pass temporary
    directories so they never touch it.
    """
    not_applicable = RelationshipResult(
        request=request, applicable=False, source=None, path=None, event=None
    )

    source_path = source_spec.file_path(request.source_title, base_dir=base_dir)
    target_path = target_spec.file_path(request.target_title, base_dir=target_base_dir)
    if not source_path.exists() or not target_path.exists():
        return not_applicable

    source_representation = source_spec.read(source_path)
    target_representation = target_spec.read(target_path)

    source_type = source_spec.domain_type.__name__
    target_type = target_spec.domain_type.__name__
    definition = processing.relationship_definition(source_type, request.relationship_type)
    existing = relationship_transform.relationships_of_type(
        source_representation, request.relationship_type
    )
    if not processing.is_relate_applicable(
        definition, target_type=target_type, existing_of_type=len(existing)
    ):
        return not_applicable

    target_id = target_representation["properties"]["id"]
    linked = relationship_transform.relate(
        source_representation,
        relationship_type=request.relationship_type,
        target_id=target_id,
        target_type=target_type.lower(),
        target_link=_link_display(target_path, target_representation["title"]),
    )
    rewrite_note(source_path, linked)
    domain_object = source_spec.from_representation(linked)

    event = _emit(
        event_type=f"{source_type} Linked to {target_type}",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="processing",
        events_dir=events_dir,
        target_id=target_id,
    )

    return RelationshipResult(
        request=request, applicable=True, source=domain_object, path=source_path, event=event
    )


def execute_unrelate(
    request: UnrelateRequest,
    *,
    spec: DomainSpec = PROJECT,
    base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> RelationshipResult:
    """Remove a relationship from a note.

    Needed because a `0..1` cardinality would otherwise leave the source
    permanently unable to move. Moving is unlink + link: two Events,
    since a changed relationship is a distinct instance
    (`relationship-representation.md`, "Relationship Changes").

    Removes the relationship of `request.relationship_type`. That is
    unambiguous while every defined relationship is `0..1`; an unbounded
    relationship would need the caller to name which target to unlink.
    """
    not_applicable = RelationshipResult(
        request=request, applicable=False, source=None, path=None, event=None
    )

    path = spec.file_path(request.source_title, base_dir=base_dir)
    if not path.exists():
        return not_applicable

    representation = spec.read(path)
    source_type = spec.domain_type.__name__
    definition = processing.relationship_definition(source_type, request.relationship_type)
    existing = relationship_transform.relationships_of_type(
        representation, request.relationship_type
    )
    if not processing.is_unrelate_applicable(definition, existing_of_type=len(existing)):
        return not_applicable

    removed_target_id = existing[0]["target_id"]
    unlinked = relationship_transform.unrelate(
        representation, relationship_type=request.relationship_type
    )
    rewrite_note(path, unlinked)
    domain_object = spec.from_representation(unlinked)

    event = _emit(
        event_type=f"{source_type} Unlinked from {definition.target_type}",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="processing",
        events_dir=events_dir,
        target_id=removed_target_id,
    )

    return RelationshipResult(
        request=request, applicable=True, source=domain_object, path=path, event=event
    )
