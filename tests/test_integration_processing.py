"""End-to-end integration test for the Processing vertical slice.

Raw Inbox entry -> Applicability -> Transformation -> Representation
-> Filesystem -> Reloaded Object, with the entry's original content
carried into the Project note and the Inbox entry resolved (removed).

Exercised with both Human and Deterministic actors through the same
`execute_processing` code path to demonstrate actor-neutrality, mirroring
Phase 10's Capture integration test.
"""

from ohtli.execution.execution import Actor, ProcessingRequest, execute_processing
from ohtli.vault_io.markdown import read_project


def test_full_processing_slice_human_actor(tmp_path):
    entry_path = tmp_path / "inbox-entry.md"
    entry_path.write_text("Website Relaunch\n\nRedesign the marketing site.\n", encoding="utf-8")
    projects_dir = tmp_path / "projects"

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
    result = execute_processing(request, base_dir=projects_dir)

    assert result.applicable
    reloaded = read_project(result.path)
    assert reloaded["title"] == "Website Relaunch"
    assert reloaded["properties"]["id"] == result.project.id
    assert reloaded["properties"]["status"] == "planned"
    assert not entry_path.exists()
    assert "Redesign the marketing site." in reloaded["body"], (
        "the Inbox entry's content must survive Processing, not be discarded"
    )


def test_full_processing_slice_deterministic_actor_same_code_path(tmp_path):
    entry_path = tmp_path / "inbox-entry.md"
    entry_path.write_text("Scheduled Backup Audit\n\nCheck backups.\n", encoding="utf-8")
    projects_dir = tmp_path / "projects"

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.DETERMINISTIC)
    result = execute_processing(request, base_dir=projects_dir)

    assert result.applicable
    reloaded = read_project(result.path)
    assert reloaded["title"] == "Scheduled Backup Audit"
    assert reloaded["properties"]["id"] == result.project.id
    assert not entry_path.exists()


def test_human_and_deterministic_actors_produce_the_same_kind_of_processing_result(tmp_path):
    human_entry = tmp_path / "human-entry.md"
    human_entry.write_text("Actor Parity A\n", encoding="utf-8")
    deterministic_entry = tmp_path / "deterministic-entry.md"
    deterministic_entry.write_text("Actor Parity B\n", encoding="utf-8")
    projects_dir = tmp_path / "projects"

    human_result = execute_processing(
        ProcessingRequest(entry_path=human_entry, actor=Actor.HUMAN), base_dir=projects_dir
    )
    deterministic_result = execute_processing(
        ProcessingRequest(entry_path=deterministic_entry, actor=Actor.DETERMINISTIC),
        base_dir=projects_dir,
    )

    assert human_result.applicable == deterministic_result.applicable is True
    assert type(human_result.project) is type(deterministic_result.project)


def test_title_only_entry_produces_a_blank_template_body(tmp_path):
    """An entry with nothing but a title still yields the standard blank
    Project template — the Capture-shaped result, unchanged."""
    entry_path = tmp_path / "title-only.md"
    entry_path.write_text("Bare Title\n", encoding="utf-8")

    result = execute_processing(
        ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN), base_dir=tmp_path / "projects"
    )

    assert result.applicable
    assert "## Notes\n\n## References" in read_project(result.path)["body"]


def test_non_processable_entry_remains_untouched_in_inbox(tmp_path):
    entry_path = tmp_path / "blank-entry.md"
    entry_path.write_text("\n   \n", encoding="utf-8")
    projects_dir = tmp_path / "projects"

    request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
    result = execute_processing(request, base_dir=projects_dir)

    assert not result.applicable
    assert entry_path.exists()
    assert entry_path.read_text(encoding="utf-8") == "\n   \n"
