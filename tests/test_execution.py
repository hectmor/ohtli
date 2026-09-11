from ohtli.domain.area import Area
from ohtli.execution.execution import (
    Actor,
    ArchiveRequest,
    EvaluationRequest,
    ExecutionRequest,
    ProcessingRequest,
    ReviewRequest,
    execute_archive,
    execute_capture,
    execute_evaluation,
    execute_processing,
    execute_reactivate,
    execute_review,
)
from ohtli.execution.specs import AREA
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
