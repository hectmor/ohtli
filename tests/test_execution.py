from ohtli.domain.area import Area
from ohtli.execution.execution import (
    Actor,
    ArchiveRequest,
    EvaluationRequest,
    ExecutionRequest,
    KnowledgeRequest,
    ProcessingRequest,
    ReviewRequest,
    execute_archive,
    execute_capture,
    execute_evaluation,
    execute_knowledge,
    execute_processing,
    execute_reactivate,
    execute_review,
)
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, REFERENCE, RESOURCE
from ohtli.domain.journal_entry import JournalEntry
from ohtli.domain.meeting import Meeting
from ohtli.domain.reference import Reference
from ohtli.domain.resource import Resource
from ohtli.vault_io.events import read_events
from ohtli.workflow.evaluation import OperationalResult
from ohtli.workflow.review import ReviewConclusion


def test_execution_occurs_when_applicable(tmp_path):
    request = ExecutionRequest(title="First Project", actor=Actor.HUMAN)
    result = execute_capture(request, base_dir=tmp_path)

    assert result.applicable
    assert result.project is not None
    assert result.project.title == "First Project"
    assert result.path is not None
    assert result.path.exists()


def test_execution_does_not_occur_when_not_applicable(tmp_path):
    first = ExecutionRequest(title="Duplicate", actor=Actor.HUMAN)
    execute_capture(first, base_dir=tmp_path)

    second = ExecutionRequest(title="Duplicate", actor=Actor.DETERMINISTIC)
    result = execute_capture(second, base_dir=tmp_path)

    assert not result.applicable
    assert result.project is None
    assert result.path is None


def test_execution_preserves_identity_between_request_and_result(tmp_path):
    request = ExecutionRequest(title="Identity Check", actor=Actor.HUMAN)
    result = execute_capture(request, base_dir=tmp_path)

    assert result.request is request
    assert result.request.execution_id == request.execution_id


def test_processing_occurs_when_applicable(tmp_path):
    entry_path = tmp_path / "raw-entry.md"
    entry_path.write_text("New Idea From Inbox\n\nSome notes.\n", encoding="utf-8")

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
    result = execute_processing(request, base_dir=tmp_path / "projects")

    assert result.applicable
    assert result.project is not None
    assert result.project.title == "New Idea From Inbox"
    assert result.path is not None
    assert result.path.exists()
    assert not entry_path.exists(), "a processed Inbox entry must be resolved"


def test_processing_does_not_occur_when_entry_has_no_derivable_title(tmp_path):
    entry_path = tmp_path / "empty-entry.md"
    entry_path.write_text("\n   \n", encoding="utf-8")

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
    result = execute_processing(request, base_dir=tmp_path / "projects")

    assert not result.applicable
    assert result.project is None
    assert result.path is None
    assert entry_path.exists(), "a non-applicable Inbox entry must remain untouched"


def test_processing_does_not_occur_when_title_already_exists(tmp_path):
    projects_dir = tmp_path / "projects"
    first_entry = tmp_path / "first-entry.md"
    first_entry.write_text("Duplicate Title\n", encoding="utf-8")
    execute_processing(
        ProcessingRequest(entry_path=first_entry, actor=Actor.HUMAN), base_dir=projects_dir
    )

    second_entry = tmp_path / "second-entry.md"
    second_entry.write_text("Duplicate Title\n", encoding="utf-8")
    result = execute_processing(
        ProcessingRequest(entry_path=second_entry, actor=Actor.DETERMINISTIC), base_dir=projects_dir
    )

    assert not result.applicable
    assert result.project is None
    assert result.path is None
    assert second_entry.exists()


def test_capture_executes_for_a_different_domain_object_via_spec(tmp_path):
    """The same execute_capture generalizes to Area by passing spec=AREA
    — no duplicate execute_capture_area function."""
    request = ExecutionRequest(title="Health", actor=Actor.HUMAN)
    result = execute_capture(request, spec=AREA, base_dir=tmp_path)

    assert result.applicable
    assert isinstance(result.project, Area)
    assert result.project.title == "Health"
    assert result.path is not None
    assert result.path.exists()


def test_processing_executes_for_a_different_domain_object_via_spec(tmp_path):
    entry_path = tmp_path / "raw-entry.md"
    entry_path.write_text("New Area From Inbox\n\nOngoing responsibility.\n", encoding="utf-8")

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.DETERMINISTIC)
    result = execute_processing(request, spec=AREA, base_dir=tmp_path / "areas")

    assert result.applicable
    assert isinstance(result.project, Area)
    assert result.project.title == "New Area From Inbox"
    assert not entry_path.exists(), "a processed Inbox entry must be resolved"


def test_capture_project_and_area_do_not_share_an_applicability_namespace(tmp_path):
    projects_dir = tmp_path / "projects"
    areas_dir = tmp_path / "areas"

    project_result = execute_capture(
        ExecutionRequest(title="Shared Name", actor=Actor.HUMAN), base_dir=projects_dir
    )
    area_result = execute_capture(
        ExecutionRequest(title="Shared Name", actor=Actor.HUMAN), spec=AREA, base_dir=areas_dir
    )

    assert project_result.applicable
    assert area_result.applicable


def test_archive_is_not_applicable_when_target_does_not_exist(tmp_path):
    request = ArchiveRequest(title="Nonexistent", actor=Actor.HUMAN)
    result = execute_archive(request, base_dir=tmp_path)

    assert not result.applicable
    assert result.project is None
    assert result.path is None


def test_archive_then_reactivate_round_trip(tmp_path):
    execute_capture(ExecutionRequest(title="Round Trip", actor=Actor.HUMAN), base_dir=tmp_path)

    archived = execute_archive(
        ArchiveRequest(title="Round Trip", actor=Actor.HUMAN), base_dir=tmp_path
    )
    assert archived.applicable
    assert archived.path is not None

    reactivated = execute_reactivate(
        ArchiveRequest(title="Round Trip", actor=Actor.DETERMINISTIC), base_dir=tmp_path
    )
    assert reactivated.applicable
    assert reactivated.path == archived.path


def test_archive_is_not_applicable_a_second_time(tmp_path):
    execute_capture(ExecutionRequest(title="Once", actor=Actor.HUMAN), base_dir=tmp_path)
    execute_archive(ArchiveRequest(title="Once", actor=Actor.HUMAN), base_dir=tmp_path)

    second = execute_archive(ArchiveRequest(title="Once", actor=Actor.HUMAN), base_dir=tmp_path)

    assert not second.applicable


def test_reactivate_is_not_applicable_before_archive(tmp_path):
    execute_capture(ExecutionRequest(title="Never Archived", actor=Actor.HUMAN), base_dir=tmp_path)

    result = execute_reactivate(
        ArchiveRequest(title="Never Archived", actor=Actor.HUMAN), base_dir=tmp_path
    )

    assert not result.applicable


def test_archive_does_not_change_status_or_id(tmp_path):
    from ohtli.vault_io.markdown import read_project

    capture_result = execute_capture(
        ExecutionRequest(title="Preserve Me", actor=Actor.HUMAN), base_dir=tmp_path
    )
    before = read_project(capture_result.path)

    execute_archive(ArchiveRequest(title="Preserve Me", actor=Actor.HUMAN), base_dir=tmp_path)
    after = read_project(capture_result.path)

    assert after["properties"]["status"] == before["properties"]["status"]
    assert after["properties"]["id"] == before["properties"]["id"]
    assert after["properties"]["context"] == "historical"


def test_archive_is_non_cascading(tmp_path):
    """Archiving one Project must leave an unrelated Project untouched."""
    execute_capture(ExecutionRequest(title="Archive This", actor=Actor.HUMAN), base_dir=tmp_path)
    other = execute_capture(
        ExecutionRequest(title="Leave This Alone", actor=Actor.HUMAN), base_dir=tmp_path
    )

    execute_archive(ArchiveRequest(title="Archive This", actor=Actor.HUMAN), base_dir=tmp_path)

    from ohtli.vault_io.markdown import read_project

    untouched = read_project(other.path)
    assert untouched["properties"]["context"] == "operational"


def test_archive_and_reactivate_work_for_a_second_domain_object(tmp_path):
    execute_capture(
        ExecutionRequest(title="Household", actor=Actor.HUMAN), spec=AREA, base_dir=tmp_path
    )

    archived = execute_archive(
        ArchiveRequest(title="Household", actor=Actor.DETERMINISTIC), spec=AREA, base_dir=tmp_path
    )
    assert archived.applicable
    assert isinstance(archived.project, Area)

    reactivated = execute_reactivate(
        ArchiveRequest(title="Household", actor=Actor.HUMAN), spec=AREA, base_dir=tmp_path
    )
    assert reactivated.applicable
    assert isinstance(reactivated.project, Area)


def test_execute_capture_emits_a_created_event(tmp_path):
    request = ExecutionRequest(title="Event Test", actor=Actor.HUMAN)
    result = execute_capture(request, base_dir=tmp_path, events_dir=tmp_path)

    assert result.event is not None
    assert result.event.event_type == "Project Created"
    assert result.event.object_id == result.project.id
    assert result.event.object_type == "Project"
    assert result.event.actor == "human"
    assert result.event.execution_id == request.execution_id
    assert result.event.workflow == "capture"

    events = read_events(events_dir=tmp_path)
    assert events == [result.event]


def test_execute_processing_emits_the_same_event_type_as_capture(tmp_path):
    entry_path = tmp_path / "raw-entry.md"
    entry_path.write_text("Processed Event Test\n\nSome notes.\n", encoding="utf-8")

    result = execute_processing(
        ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN),
        base_dir=tmp_path / "projects",
        events_dir=tmp_path,
    )

    assert result.event.event_type == "Project Created"
    assert result.event.workflow == "processing"


def test_execute_archive_emits_an_archived_event(tmp_path):
    execute_capture(
        ExecutionRequest(title="Archive Event Test", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    result = execute_archive(
        ArchiveRequest(title="Archive Event Test", actor=Actor.DETERMINISTIC),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.event.event_type == "Project Archived"
    assert result.event.workflow == "archive"
    assert result.event.actor == "deterministic"


def test_execute_reactivate_emits_a_reactivated_event(tmp_path):
    execute_capture(
        ExecutionRequest(title="Reactivate Event Test", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    execute_archive(
        ArchiveRequest(title="Reactivate Event Test", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    result = execute_reactivate(
        ArchiveRequest(title="Reactivate Event Test", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.event.event_type == "Project Reactivated"
    assert result.event.workflow == "reactivate"


def test_not_applicable_operations_emit_no_event(tmp_path):
    execute_capture(
        ExecutionRequest(title="Duplicate Event Test", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    duplicate = execute_capture(
        ExecutionRequest(title="Duplicate Event Test", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    not_found = execute_archive(
        ArchiveRequest(title="Never Captured", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert duplicate.event is None
    assert not_found.event is None
    assert len(read_events(events_dir=tmp_path)) == 1, "only the first, applicable capture emits"


def test_full_round_trip_produces_three_ordered_events_for_the_same_object(tmp_path):
    captured = execute_capture(
        ExecutionRequest(title="Full Round Trip", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    execute_archive(
        ArchiveRequest(title="Full Round Trip", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    execute_reactivate(
        ArchiveRequest(title="Full Round Trip", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    events = read_events(events_dir=tmp_path)
    assert [e.event_type for e in events] == [
        "Project Created",
        "Project Archived",
        "Project Reactivated",
    ]
    assert all(e.object_id == captured.project.id for e in events)


def test_execute_evaluation_emits_the_correct_event_and_touches_no_representation(tmp_path):
    captured = execute_capture(
        ExecutionRequest(title="Evaluate Me", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    before_content = captured.path.read_text(encoding="utf-8")
    before_mtime = captured.path.stat().st_mtime_ns

    result = execute_evaluation(
        EvaluationRequest(title="Evaluate Me", result=OperationalResult.PROGRESS, actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable
    assert result.event.event_type == "Project Progress Observed"
    assert result.event.workflow == "evaluation"
    assert captured.path.read_text(encoding="utf-8") == before_content, "Evaluate must not rewrite the note"
    assert captured.path.stat().st_mtime_ns == before_mtime


def test_execute_evaluation_rejects_a_result_the_domain_object_does_not_allow(tmp_path):
    execute_capture(
        ExecutionRequest(title="Household Chores", actor=Actor.HUMAN),
        spec=AREA,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_evaluation(
        EvaluationRequest(
            title="Household Chores", result=OperationalResult.OUTCOME_REACHED, actor=Actor.HUMAN
        ),
        spec=AREA,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert not result.applicable
    assert result.event is None


def test_execute_evaluation_rejects_an_archived_target(tmp_path):
    execute_capture(
        ExecutionRequest(title="Archived Project", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    execute_archive(
        ArchiveRequest(title="Archived Project", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_evaluation(
        EvaluationRequest(
            title="Archived Project", result=OperationalResult.PROGRESS, actor=Actor.HUMAN
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert not result.applicable


def test_execute_evaluation_is_not_applicable_when_target_does_not_exist(tmp_path):
    result = execute_evaluation(
        EvaluationRequest(title="Never Captured", result=OperationalResult.PROGRESS, actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert not result.applicable
    assert result.project is None
    assert result.path is None


def test_execute_evaluation_allows_multiple_instances_for_the_same_object(tmp_path):
    execute_capture(
        ExecutionRequest(title="Iterative Work", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    first = execute_evaluation(
        EvaluationRequest(title="Iterative Work", result=OperationalResult.PROGRESS, actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    second = execute_evaluation(
        EvaluationRequest(
            title="Iterative Work", result=OperationalResult.NO_EFFECTIVE_CHANGE, actor=Actor.DETERMINISTIC
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert first.applicable
    assert second.applicable
    events = read_events(events_dir=tmp_path)
    assert [e.event_type for e in events if e.workflow == "evaluation"] == [
        "Project Progress Observed",
        "Project No Effective Change Observed",
    ]


def test_execute_review_is_not_applicable_when_target_does_not_exist(tmp_path):
    result = execute_review(
        ReviewRequest(title="Never Captured", actor=Actor.HUMAN), base_dir=tmp_path, events_dir=tmp_path
    )

    assert not result.applicable
    assert result.assessment is None


def test_execute_review_is_insufficient_basis_with_no_evaluations(tmp_path):
    execute_capture(
        ExecutionRequest(title="Fresh Project", actor=Actor.HUMAN), base_dir=tmp_path, events_dir=tmp_path
    )

    result = execute_review(
        ReviewRequest(title="Fresh Project", actor=Actor.HUMAN), base_dir=tmp_path, events_dir=tmp_path
    )

    assert result.applicable
    assert result.assessment.conclusion == ReviewConclusion.INSUFFICIENT_BASIS
    assert result.event.event_type == "Project Insufficient Assessment Basis Identified"


def test_execute_review_touches_no_representation(tmp_path):
    captured = execute_capture(
        ExecutionRequest(title="Untouched By Review", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    before_content = captured.path.read_text(encoding="utf-8")
    before_mtime = captured.path.stat().st_mtime_ns

    execute_review(
        ReviewRequest(title="Untouched By Review", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert captured.path.read_text(encoding="utf-8") == before_content
    assert captured.path.stat().st_mtime_ns == before_mtime


def test_execute_review_reviews_an_archived_target(tmp_path):
    execute_capture(
        ExecutionRequest(title="Archived And Reviewable", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    execute_archive(
        ArchiveRequest(title="Archived And Reviewable", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_review(
        ReviewRequest(title="Archived And Reviewable", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable, "an archived target must remain reviewable"


def test_execute_review_surfaces_attention_for_a_completed_gap(tmp_path):
    execute_capture(
        ExecutionRequest(title="Outcome Gap", actor=Actor.HUMAN), base_dir=tmp_path, events_dir=tmp_path
    )
    execute_evaluation(
        EvaluationRequest(title="Outcome Gap", result=OperationalResult.OUTCOME_REACHED, actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_review(
        ReviewRequest(title="Outcome Gap", actor=Actor.HUMAN), base_dir=tmp_path, events_dir=tmp_path
    )

    assert result.assessment.conclusion == ReviewConclusion.ATTENTION_REQUIRED
    assert result.event.event_type == "Project Attention Identified"


def test_execute_review_since_excludes_earlier_events(tmp_path):
    execute_capture(
        ExecutionRequest(title="Since Bound Test", actor=Actor.HUMAN), base_dir=tmp_path, events_dir=tmp_path
    )
    execute_evaluation(
        EvaluationRequest(title="Since Bound Test", result=OperationalResult.PROGRESS, actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    far_future = "2099-01-01T00:00:00+00:00"
    result = execute_review(
        ReviewRequest(title="Since Bound Test", actor=Actor.HUMAN, since=far_future),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.assessment.conclusion == ReviewConclusion.INSUFFICIENT_BASIS, (
        "a since bound in the future must exclude all prior evaluation Events"
    )


def test_execute_knowledge_enriches_and_emits_the_correct_event(tmp_path):
    execute_capture(
        ExecutionRequest(title="Enrich Me", actor=Actor.HUMAN), base_dir=tmp_path, events_dir=tmp_path
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="Enrich Me",
            understanding_title="A Finding",
            understanding="The root cause was X.",
            provenance=("Reference A", "Experience"),
            actor=Actor.HUMAN,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable
    assert result.event.event_type == "Project Knowledge Enriched"
    assert result.event.workflow == "knowledge"
    body = result.path.read_text(encoding="utf-8")
    assert "## Understanding" in body
    assert "The root cause was X." in body
    assert "Developed from: Reference A; Experience" in body


def test_execute_knowledge_rejects_empty_understanding(tmp_path):
    execute_capture(
        ExecutionRequest(title="No Understanding", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="No Understanding",
            understanding_title="Empty",
            understanding="   ",
            provenance=("Source",),
            actor=Actor.HUMAN,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert not result.applicable
    assert result.event is None


def test_execute_knowledge_rejects_empty_provenance(tmp_path):
    execute_capture(
        ExecutionRequest(title="No Provenance", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="No Provenance",
            understanding_title="Unsourced",
            understanding="Something.",
            provenance=(),
            actor=Actor.HUMAN,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert not result.applicable


def test_execute_knowledge_is_not_applicable_when_target_does_not_exist(tmp_path):
    result = execute_knowledge(
        KnowledgeRequest(
            title="Never Captured",
            understanding_title="F",
            understanding="T",
            provenance=("S",),
            actor=Actor.HUMAN,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert not result.applicable
    assert result.project is None
    assert result.path is None


def test_execute_knowledge_enriches_an_archived_target(tmp_path):
    execute_capture(
        ExecutionRequest(title="Archived And Enrichable", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    execute_archive(
        ArchiveRequest(title="Archived And Enrichable", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="Archived And Enrichable",
            understanding_title="F",
            understanding="T",
            provenance=("S",),
            actor=Actor.HUMAN,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable, "an archived target must remain enrichable"


def test_execute_knowledge_does_not_change_status_or_context(tmp_path):
    from ohtli.vault_io.markdown import read_project

    captured = execute_capture(
        ExecutionRequest(title="Preserve My Status", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    before = read_project(captured.path)

    execute_knowledge(
        KnowledgeRequest(
            title="Preserve My Status",
            understanding_title="F",
            understanding="T",
            provenance=("S",),
            actor=Actor.HUMAN,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    after = read_project(captured.path)

    assert after["properties"]["status"] == before["properties"]["status"]
    assert after["properties"]["context"] == before["properties"]["context"]


def test_execute_knowledge_second_enrichment_appends_rather_than_replaces(tmp_path):
    execute_capture(
        ExecutionRequest(title="Two Enrichments", actor=Actor.HUMAN),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    execute_knowledge(
        KnowledgeRequest(
            title="Two Enrichments",
            understanding_title="First",
            understanding="First understanding.",
            provenance=("Source A",),
            actor=Actor.HUMAN,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    result = execute_knowledge(
        KnowledgeRequest(
            title="Two Enrichments",
            understanding_title="Second",
            understanding="Second understanding.",
            provenance=("Source B",),
            actor=Actor.DETERMINISTIC,
        ),
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    body = result.path.read_text(encoding="utf-8")
    assert body.count("## Understanding") == 1
    assert "First understanding." in body
    assert "Second understanding." in body


def test_execute_knowledge_enriches_a_second_domain_object(tmp_path):
    execute_capture(
        ExecutionRequest(title="Household Knowledge", actor=Actor.HUMAN), spec=AREA, base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="Household Knowledge",
            understanding_title="F",
            understanding="T",
            provenance=("S",),
            actor=Actor.HUMAN,
        ),
        spec=AREA,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable
    assert result.event.event_type == "Area Knowledge Enriched"


def test_execute_capture_and_reactivate_work_for_resource(tmp_path):
    captured = execute_capture(
        ExecutionRequest(title="A Guide", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert captured.applicable
    assert isinstance(captured.project, Resource)
    assert captured.event.event_type == "Resource Created"

    archived = execute_archive(
        ArchiveRequest(title="A Guide", actor=Actor.DETERMINISTIC),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert archived.applicable
    assert archived.event.event_type == "Resource Archived"

    reactivated = execute_reactivate(
        ArchiveRequest(title="A Guide", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert reactivated.applicable
    assert reactivated.event.event_type == "Resource Reactivated"


def test_execute_review_works_for_resource(tmp_path):
    execute_capture(
        ExecutionRequest(title="Reviewable Resource", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_review(
        ReviewRequest(title="Reviewable Resource", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable
    assert result.assessment.conclusion == ReviewConclusion.INSUFFICIENT_BASIS
    assert result.event.event_type == "Resource Insufficient Assessment Basis Identified"


def test_execute_knowledge_works_for_resource(tmp_path):
    execute_capture(
        ExecutionRequest(title="Enrichable Resource", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="Enrichable Resource",
            understanding_title="Refined Understanding",
            understanding="A clearer explanation of the concept.",
            provenance=("New Reference",),
            actor=Actor.HUMAN,
        ),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable
    assert result.event.event_type == "Resource Knowledge Enriched"


def test_execute_evaluation_is_never_applicable_for_resource(tmp_path):
    """Resource is not an Execution target (execution-workflow.md):
    every OperationalResult value must be rejected, not just one."""
    execute_capture(
        ExecutionRequest(title="Not An Execution Target", actor=Actor.HUMAN),
        spec=RESOURCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    for result_value in OperationalResult:
        result = execute_evaluation(
            EvaluationRequest(
                title="Not An Execution Target", result=result_value, actor=Actor.HUMAN
            ),
            spec=RESOURCE,
            base_dir=tmp_path,
            events_dir=tmp_path,
        )
        assert not result.applicable, f"{result_value} must not be applicable for Resource"


def test_execute_capture_and_reactivate_work_for_reference(tmp_path):
    captured = execute_capture(
        ExecutionRequest(title="A Paper", actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert captured.applicable
    assert isinstance(captured.project, Reference)
    assert captured.event.event_type == "Reference Created"

    archived = execute_archive(
        ArchiveRequest(title="A Paper", actor=Actor.DETERMINISTIC),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert archived.applicable
    assert archived.event.event_type == "Reference Archived"

    reactivated = execute_reactivate(
        ArchiveRequest(title="A Paper", actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert reactivated.applicable
    assert reactivated.event.event_type == "Reference Reactivated"


def test_execute_processing_carries_inbox_content_into_reference_notes(tmp_path):
    entry_path = tmp_path / "raw-entry.md"
    entry_path.write_text(
        "Interesting Paper On Caching\n\nFound via a colleague, worth citing later.\n",
        encoding="utf-8",
    )

    result = execute_processing(
        ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path / "references",
        events_dir=tmp_path,
    )

    assert result.applicable
    assert isinstance(result.project, Reference)
    assert result.project.title == "Interesting Paper On Caching"
    assert result.event.event_type == "Reference Created"
    assert result.event.workflow == "processing"

    body = result.path.read_text(encoding="utf-8")
    assert "Found via a colleague, worth citing later." in body
    assert not entry_path.exists(), "a processed Inbox entry must be resolved"


def test_execute_review_works_for_reference(tmp_path):
    execute_capture(
        ExecutionRequest(title="Reviewable Reference", actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_review(
        ReviewRequest(title="Reviewable Reference", actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable
    assert result.assessment.conclusion == ReviewConclusion.INSUFFICIENT_BASIS
    assert result.event.event_type == "Reference Insufficient Assessment Basis Identified"


def test_execute_evaluation_is_never_applicable_for_reference(tmp_path):
    """Reference is not an Execution target (execution-workflow.md):
    every OperationalResult value must be rejected, not just one."""
    execute_capture(
        ExecutionRequest(title="Also Not An Execution Target", actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    for result_value in OperationalResult:
        result = execute_evaluation(
            EvaluationRequest(
                title="Also Not An Execution Target", result=result_value, actor=Actor.HUMAN
            ),
            spec=REFERENCE,
            base_dir=tmp_path,
            events_dir=tmp_path,
        )
        assert not result.applicable, f"{result_value} must not be applicable for Reference"


def test_execute_knowledge_currently_succeeds_for_reference_despite_not_being_a_spec_target(tmp_path):
    """Documents a known, accepted gap rather than leaving it an
    untested assumption: knowledge-workflow.md only names Project,
    Area, and Resource as Externalize targets -- Reference is a
    source, not an enrichment target. But nothing in execute_knowledge()
    or representation/understanding.py's enrich() is type-aware, so
    this call succeeds today. Excluded only by CLI omission (no
    enrich-reference command), not by a structural guard -- there is
    no spec evidence to justify inventing one for this phase."""
    execute_capture(
        ExecutionRequest(title="Enrichable Despite The Spec", actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="Enrichable Despite The Spec",
            understanding_title="F",
            understanding="T",
            provenance=("S",),
            actor=Actor.HUMAN,
        ),
        spec=REFERENCE,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable, (
        "known gap: execute_knowledge has no structural guard against non-Externalize-target "
        "Domain Objects; this must stay true until a future phase adds one deliberately"
    )
    assert result.event.event_type == "Reference Knowledge Enriched"


def test_execute_capture_and_reactivate_work_for_meeting(tmp_path):
    captured = execute_capture(
        ExecutionRequest(title="Weekly Sync", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert captured.applicable
    assert isinstance(captured.project, Meeting)
    assert captured.event.event_type == "Meeting Created"

    archived = execute_archive(
        ArchiveRequest(title="Weekly Sync", actor=Actor.DETERMINISTIC),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert archived.applicable
    assert archived.event.event_type == "Meeting Archived"

    reactivated = execute_reactivate(
        ArchiveRequest(title="Weekly Sync", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    assert reactivated.applicable
    assert reactivated.event.event_type == "Meeting Reactivated"


def test_execute_processing_carries_inbox_content_into_meeting_discussion(tmp_path):
    entry_path = tmp_path / "raw-entry.md"
    entry_path.write_text(
        "Quick Standup Notes\n\nAgreed to ship the fix by Friday.\n",
        encoding="utf-8",
    )

    result = execute_processing(
        ProcessingRequest(entry_path=entry_path, actor=Actor.DETERMINISTIC),
        spec=MEETING,
        base_dir=tmp_path / "meetings",
        events_dir=tmp_path,
    )

    assert result.applicable
    assert isinstance(result.project, Meeting)
    assert result.project.title == "Quick Standup Notes"
    assert result.event.event_type == "Meeting Created"
    assert result.event.workflow == "processing"

    body = result.path.read_text(encoding="utf-8")
    assert "Agreed to ship the fix by Friday." in body
    assert "## Discussion\n\nAgreed to ship the fix by Friday." in body
    assert not entry_path.exists(), "a processed Inbox entry must be resolved"


def test_execute_review_works_for_meeting(tmp_path):
    execute_capture(
        ExecutionRequest(title="Reviewable Meeting", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_review(
        ReviewRequest(title="Reviewable Meeting", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable
    assert result.assessment.conclusion == ReviewConclusion.INSUFFICIENT_BASIS
    assert result.event.event_type == "Meeting Insufficient Assessment Basis Identified"


def test_execute_evaluation_is_never_applicable_for_meeting(tmp_path):
    """Meeting is not an Execution target (execution-workflow.md):
    every OperationalResult value must be rejected, not just one."""
    execute_capture(
        ExecutionRequest(title="Coordination Only", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    for result_value in OperationalResult:
        result = execute_evaluation(
            EvaluationRequest(title="Coordination Only", result=result_value, actor=Actor.HUMAN),
            spec=MEETING,
            base_dir=tmp_path,
            events_dir=tmp_path,
        )
        assert not result.applicable, f"{result_value} must not be applicable for Meeting"


def test_execute_knowledge_currently_succeeds_for_meeting_despite_not_being_a_spec_target(tmp_path):
    """Same documented, accepted gap as Reference (Phase 19):
    knowledge-workflow.md names Meeting only as a source, never an
    Externalize target, but execute_knowledge() has no structural
    guard against this -- excluded only by CLI omission."""
    execute_capture(
        ExecutionRequest(title="Enrichable Meeting Despite The Spec", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="Enrichable Meeting Despite The Spec",
            understanding_title="F",
            understanding="T",
            provenance=("S",),
            actor=Actor.HUMAN,
        ),
        spec=MEETING,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable, (
        "known gap: execute_knowledge has no structural guard against non-Externalize-target "
        "Domain Objects; this must stay true until a future phase adds one deliberately"
    )
    assert result.event.event_type == "Meeting Knowledge Enriched"


def test_execute_capture_journal_entry_with_a_date_title_for_both_actors(tmp_path):
    human = execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    deterministic = execute_capture(
        ExecutionRequest(title="2026-07-30", actor=Actor.DETERMINISTIC),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert human.applicable and deterministic.applicable
    assert isinstance(human.project, JournalEntry)
    assert human.path.name == "2026-07-29.md"
    assert human.event.event_type == "JournalEntry Created"
    assert deterministic.event.actor == "deterministic"


def test_capture_rejects_a_second_journal_entry_for_the_same_moment(tmp_path):
    execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    duplicate = execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert not duplicate.applicable
    assert duplicate.event is None


def test_journal_entry_and_project_do_not_share_an_applicability_namespace(tmp_path):
    project = execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        base_dir=tmp_path / "projects",
        events_dir=tmp_path,
    )
    entry = execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path / "entries",
        events_dir=tmp_path,
    )

    assert project.applicable and entry.applicable


def test_execute_processing_carries_inbox_content_into_journal_entry_notes(tmp_path):
    for actor, name in ((Actor.HUMAN, "human"), (Actor.DETERMINISTIC, "deterministic")):
        entry_path = tmp_path / f"raw-{name}.md"
        entry_path.write_text(
            f"Pensamiento {name}\n\nMe di cuenta de que conviene escribir menos y revisar más.\n",
            encoding="utf-8",
        )

        result = execute_processing(
            ProcessingRequest(entry_path=entry_path, actor=actor),
            spec=JOURNAL_ENTRY,
            base_dir=tmp_path / "entries",
            events_dir=tmp_path,
        )

        assert result.applicable
        assert isinstance(result.project, JournalEntry)
        assert result.event.event_type == "JournalEntry Created"
        assert result.event.workflow == "processing"
        body = result.path.read_text(encoding="utf-8")
        assert "## Notes\n\nMe di cuenta de que conviene escribir menos y revisar más." in body
        assert not entry_path.exists(), "a processed Inbox entry must be resolved"


def test_execute_archive_and_reactivate_work_for_journal_entry(tmp_path):
    execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    archived = execute_archive(
        ArchiveRequest(title="2026-07-29", actor=Actor.DETERMINISTIC),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )
    reactivated = execute_reactivate(
        ArchiveRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert archived.applicable
    assert archived.event.event_type == "JournalEntry Archived"
    assert reactivated.applicable
    assert reactivated.event.event_type == "JournalEntry Reactivated"


def test_execute_evaluation_is_never_applicable_for_journal_entry(tmp_path):
    """Journal Entry is not an Execution target (execution-workflow.md):
    every OperationalResult value must be rejected, not just one."""
    execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    for result_value in OperationalResult:
        result = execute_evaluation(
            EvaluationRequest(title="2026-07-29", result=result_value, actor=Actor.HUMAN),
            spec=JOURNAL_ENTRY,
            base_dir=tmp_path,
            events_dir=tmp_path,
        )
        assert not result.applicable, f"{result_value} must not be applicable for Journal Entry"


def test_execute_knowledge_currently_succeeds_for_journal_entry_despite_not_being_a_spec_target(tmp_path):
    """Documented, accepted gap (same as Reference/Meeting):
    knowledge-workflow.md names Journal Entry only as a source, never
    an Externalize target, but execute_knowledge() has no structural
    guard -- excluded only by CLI omission (no enrich-journal-entry)."""
    execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_knowledge(
        KnowledgeRequest(
            title="2026-07-29",
            understanding_title="F",
            understanding="T",
            provenance=("S",),
            actor=Actor.HUMAN,
        ),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable, (
        "known gap: execute_knowledge has no structural guard against non-Externalize-target "
        "Domain Objects; this must stay true until a future phase adds one deliberately"
    )
    assert result.event.event_type == "JournalEntry Knowledge Enriched"


def test_execute_review_currently_succeeds_for_journal_entry_despite_being_context_not_subject(tmp_path):
    """Documented, accepted gap: review-workflow.md treats a Journal
    Entry as context for a broader Review, not a Review subject, but
    execute_review() is type-agnostic -- excluded only by CLI omission
    (no review-journal-entry)."""
    execute_capture(
        ExecutionRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    result = execute_review(
        ReviewRequest(title="2026-07-29", actor=Actor.HUMAN),
        spec=JOURNAL_ENTRY,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )

    assert result.applicable, (
        "known gap: execute_review has no structural guard against non-subject Domain Objects; "
        "this must stay true until a future phase adds one deliberately"
    )
    assert result.assessment.conclusion == ReviewConclusion.INSUFFICIENT_BASIS
    assert result.event.event_type == "JournalEntry Insufficient Assessment Basis Identified"
