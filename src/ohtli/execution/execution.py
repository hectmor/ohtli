from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from typing import Any, Callable

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.event.event import Event
from ohtli.execution.specs import AREA, PROJECT, DomainSpec, display_name_of, spec_by_note_type
from ohtli.representation import context as archive_transform
from ohtli.representation.context import HISTORICAL, OPERATIONAL
from ohtli.representation import notes as notes_transform
from ohtli.representation import relationship as relationship_transform
from ohtli.representation import understanding as understanding_transform
from ohtli.vault_io import paths
from ohtli.vault_io.events import append_event, read_events
from ohtli.vault_io.markdown import (
    find_note_by_id,
    list_projects_linking_to,
    read_inbox_entry,
    resolve_inbox_entry,
    rewrite_note,
)
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
        event_type=f"{spec.display_name} Created",
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
    # "create" or "update"; `None` when `applicable` is False. Lets the CLI
    # choose its wording without parsing `event.event_type`.
    operation: str | None = None


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

    if not processing.is_applicable(raw_text):
        return ProcessingResult(request=request, applicable=False, project=None, path=None, event=None)

    if processing.is_update(raw_text, existing_titles):
        title = processing.derive_title(raw_text)
        path = spec.file_path(title, base_dir=base_dir)
        representation = spec.read(path)
        entry_text = processing.derive_notes(raw_text)

        event = None
        if entry_text is not None:
            representation = notes_transform.apply_update(
                representation, heading=spec.notes_heading, entry_text=entry_text
            )
            rewrite_note(path, representation)

        domain_object = spec.from_representation(representation)
        resolve_inbox_entry(request.entry_path)

        if entry_text is not None:
            event = _emit(
                event_type=f"{spec.display_name} Updated",
                domain_object=domain_object,
                actor=request.actor,
                execution_id=request.execution_id,
                workflow="processing",
                events_dir=events_dir,
            )

        return ProcessingResult(
            request=request, applicable=True, project=domain_object, path=path, event=event, operation="update"
        )

    domain_object = processing.transform(raw_text, spec.domain_type)
    representation = spec.to_representation(domain_object, notes=processing.derive_notes(raw_text))
    path = spec.write(representation, base_dir=base_dir)
    resolve_inbox_entry(request.entry_path)
    event = _emit(
        event_type=f"{spec.display_name} Created",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="processing",
        events_dir=events_dir,
    )

    return ProcessingResult(
        request=request, applicable=True, project=domain_object, path=path, event=event, operation="create"
    )


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
    # Only set by Archive (never Reactivate) when not applicable: "missing",
    # "wrong_context", or "operational_dependents". `archive-workflow.md`
    # ("Archive does not determine how the dependency should be resolved")
    # means the human needs to be told which one, not just that it failed.
    reason: str | None = None


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
        event_type=f"{spec.display_name} {event_verb}",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow=workflow,
        events_dir=events_dir,
    )

    return ArchiveResult(request=request, applicable=True, project=domain_object, path=path, event=event)


def read_operational_dependents(
    title: str, spec: DomainSpec, *, base_dir: Path | None = None
) -> tuple[dict[str, Any], ...]:
    """The still-operational objects `title` (of `spec`'s type) is required
    by, per `archive-workflow.md`'s Operational Integrity: the targets of
    `title`'s own `archive_workflow.OPERATIONALLY_REQUIRING_TYPES`
    relationships (today: `supports`) whose `context` is still `operational`.

    Not an `execute_*` operation: a read, no actor, no request, no event —
    same precedent as `read_contained_projects`. Empty when the note doesn't
    exist, has no such relationships, or every target has gone historical or
    is unresolvable (`find_note_by_id` treats a dangling `target_id` as "no
    dependency", not an error).

    The target's directory is derived from `base_dir`'s sibling by
    `note_type` when `base_dir` is given (the convention every multi-type
    test in this codebase already follows: `tmp_path / spec.note_type` per
    type, sharing one parent), or from the target spec's own real-vault
    default otherwise.
    """
    path = spec.file_path(title, base_dir=base_dir)
    if not path.exists():
        return ()

    representation = spec.read(path)
    entries = representation["properties"].get("relationships") or []

    dependents = []
    for entry in entries:
        if entry.get("type") not in archive_workflow.OPERATIONALLY_REQUIRING_TYPES:
            continue
        target_type, target_id = entry.get("target_type"), entry.get("target_id")
        if not target_type or not target_id:
            continue
        target_spec = spec_by_note_type(target_type)
        target_dir = (
            base_dir.parent / target_spec.note_type
            if base_dir is not None
            else target_spec.file_path("_", base_dir=None).parent
        )
        found = find_note_by_id(target_dir, target_id)
        # A note with no `context` field (pre-Phase-13, still a supported
        # shape: `test_a_pre_phase_13_note_without_context_can_be_linked`)
        # was never explicitly archived, so it is implicitly operational —
        # `operational` is what every note starts as; only Archive ever
        # writes `historical`. Only an explicit `historical` clears the block.
        if found is not None and found["context"] != HISTORICAL:
            dependents.append(found)
    return tuple(dependents)


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

    Refused, per Operational Integrity, while another operational object
    still `supports`-requires this one — checked via `read_operational_
    dependents` before the actual (unchanged) applicability/transition
    machinery runs, so `_execute_contextual_transition` and Reactivate's
    path stay untouched.
    """
    dependents = read_operational_dependents(request.title, spec, base_dir=base_dir)
    result = _execute_contextual_transition(
        request,
        spec=spec,
        base_dir=base_dir,
        events_dir=events_dir,
        is_applicable=lambda ctx: archive_workflow.is_applicable(
            ctx, has_operational_dependents=bool(dependents)
        ),
        transition=archive_transform.archive,
        event_verb="Archived",
        workflow="archive",
    )
    if result.applicable:
        return result

    if not spec.file_path(request.title, base_dir=base_dir).exists():
        reason = "missing"
    elif dependents:
        reason = "operational_dependents"
    else:
        reason = "wrong_context"
    return ArchiveResult(
        request=result.request, applicable=False, project=None, path=None, event=None, reason=reason
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
        event_type=f"{spec.display_name} {_RESULT_VERBS[request.result]}",
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
        event_type=f"{spec.display_name} {_CONCLUSION_VERBS[assessment.conclusion]}",
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
    Project, Area, or Resource with Developed Understanding supplied
    by the caller.

    Only those three are Externalize targets (`knowledge-workflow.md`);
    Reference, Meeting, and Journal Entry are Knowledge inputs, so any
    other `spec` is refused up front, before the filesystem is touched.

    Explore/Extract/Connect/Synthesize happen outside Ohtli's code
    (mirroring Execution's Act) -- the actor supplies the
    already-developed understanding, mirroring Evaluate's
    already-observed result. Unlike Evaluate/Review, this DOES write
    to the representation: Externalize's own definition is enriching
    an existing object, and Epistemic Provenance is only testable
    against a persisted representation.
    """
    if not knowledge_workflow.is_externalize_target(spec.domain_type.__name__):
        return KnowledgeResult(request=request, applicable=False, project=None, path=None, event=None)

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
        event_type=f"{spec.display_name} Knowledge Enriched",
        domain_object=domain_object,
        actor=request.actor,
        execution_id=request.execution_id,
        workflow="knowledge",
        events_dir=events_dir,
    )

    return KnowledgeResult(request=request, applicable=True, project=domain_object, path=path, event=event)


def _link_display(target_path: Path, target_title: str) -> str:
    """A display-only, folder-qualified wikilink to the target note.

    Built from the path relative to the vault root (without `.md`), so a
    note in a nested folder (`journal/entries/...`) gets its full path,
    and two notes with the same slug in different folders stay
    unambiguous. A path outside the vault (tests use temporary
    directories) falls back to `<parent directory name>/<stem>`.

    Non-authoritative: `target_id` is the authority, and no `execute_*`
    ever reads this back.
    """
    try:
        location = target_path.resolve().relative_to(paths.VAULT_DIR.resolve()).with_suffix("").as_posix()
    except ValueError:
        location = f"{target_path.parent.name}/{target_path.stem}"
    return f"[[{location}|{target_title}]]"


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
    # Which target to unlink. Optional for a `0..1` relationship (there is at
    # most one), required for a `0..*` one.
    target_title: str | None = None


@dataclass(frozen=True)
class RelationshipResult:
    request: RelateRequest | UnrelateRequest
    applicable: bool
    source: object | None
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
    target_id = target_representation["properties"]["id"]
    definition = processing.relationship_definition(
        source_type, request.relationship_type, target_type
    )
    existing = relationship_transform.relationships_of_type(
        source_representation, request.relationship_type
    )
    if not processing.is_relate_applicable(
        definition,
        target_type=target_type,
        existing_of_type=len(existing),
        already_linked=any(entry.get("target_id") == target_id for entry in existing),
    ):
        return not_applicable

    linked = relationship_transform.relate(
        source_representation,
        relationship_type=request.relationship_type,
        target_id=target_id,
        target_type=target_spec.note_type,
        target_link=_link_display(target_path, target_representation["title"]),
    )
    rewrite_note(source_path, linked)
    domain_object = source_spec.from_representation(linked)

    event = _emit(
        event_type=f"{source_spec.display_name} Linked to {target_spec.display_name}",
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
    target_spec: DomainSpec | None = None,
    base_dir: Path | None = None,
    target_base_dir: Path | None = None,
    events_dir: Path | None = None,
) -> RelationshipResult:
    """Remove a relationship from a note.

    A `0..1` relationship has at most one target, so naming it is
    optional (and, without it, this is what makes moving possible:
    unlink + link = two Events, since a changed relationship is a
    distinct instance — `relationship-representation.md`, "Relationship
    Changes"). A `0..*` relationship can hold many targets, so the
    request must name which one (`request.target_title`, with
    `target_spec`); exactly that instance is removed and the others are
    kept.

    The named target note must still exist: its stable `id` is what
    identifies the instance to remove. Unlinking a dangling relationship
    whose target note is gone is not handled here.
    """
    not_applicable = RelationshipResult(
        request=request, applicable=False, source=None, path=None, event=None
    )

    path = spec.file_path(request.source_title, base_dir=base_dir)
    if not path.exists():
        return not_applicable

    representation = spec.read(path)
    source_type = spec.domain_type.__name__

    named_target_id: str | None = None
    target_type: str | None = None
    if request.target_title is not None:
        if target_spec is None:
            return not_applicable
        target_path = target_spec.file_path(request.target_title, base_dir=target_base_dir)
        if not target_path.exists():
            return not_applicable
        named_target_id = target_spec.read(target_path)["properties"]["id"]
        target_type = target_spec.domain_type.__name__

    definition = processing.relationship_definition(
        source_type, request.relationship_type, target_type
    )
    existing = relationship_transform.relationships_of_type(
        representation, request.relationship_type
    )
    if not processing.is_unrelate_applicable(
        definition,
        existing_of_type=len(existing),
        target_named=named_target_id is not None,
        target_linked=any(entry.get("target_id") == named_target_id for entry in existing),
    ):
        return not_applicable

    removed_target_id = named_target_id or existing[0]["target_id"]
    unlinked = relationship_transform.unrelate(
        representation,
        relationship_type=request.relationship_type,
        target_id=named_target_id,
    )
    rewrite_note(path, unlinked)
    domain_object = spec.from_representation(unlinked)

    event = _emit(
        event_type=f"{spec.display_name} Unlinked from {display_name_of(definition.target_type)}",
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


@dataclass(frozen=True)
class ContainedProjectsResult:
    applicable: bool
    projects: tuple[dict[str, Any], ...]


def read_contained_projects(
    area_title: str,
    *,
    area_base_dir: Path | None = None,
    project_base_dir: Path | None = None,
) -> ContainedProjectsResult:
    """Read the derived view `Area contains Project`.

    Not an `execute_*` operation: it has no actor, no request and emits no
    event, because a read is not a state change. `Area contains Project` is
    never stored (the Interaction Model calls it the complement of `Project
    belongs to Area`), so it is computed from the Projects whose `belongs to`
    targets this Area. With a single source of truth it can neither go stale
    nor contradict the Project side.

    Applicable only when the Area exists. Archived (historical) Projects are
    included: Archive is non-cascading and their `belongs to` link persists.
    """
    area_path = AREA.file_path(area_title, base_dir=area_base_dir)
    if not area_path.exists():
        return ContainedProjectsResult(applicable=False, projects=())

    derived = processing.derived_relationship_for_pair("Area", "Project")
    area_id = AREA.read(area_path)["properties"]["id"]
    projects = list_projects_linking_to(
        area_id, derived.via.relationship_type, base_dir=project_base_dir
    )
    return ContainedProjectsResult(applicable=True, projects=tuple(projects))
