from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    ProcessingRequest,
    execute_capture,
    execute_processing,
)


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
