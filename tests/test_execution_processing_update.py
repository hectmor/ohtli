"""Processing's Update: a title collision on the Inbox updates the existing
object instead of being refused (Phase 34), for every Domain Object.

Everything runs against `tmp_path`, never the real vault.
"""

import pytest

from ohtli.execution.execution import Actor, ExecutionRequest, ProcessingRequest, execute_capture, execute_processing
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.vault_io.events import read_events

CASES = [
    pytest.param(PROJECT, id="project"),
    pytest.param(AREA, id="area"),
    pytest.param(RESOURCE, id="resource"),
    pytest.param(REFERENCE, id="reference"),
    pytest.param(MEETING, id="meeting"),
    pytest.param(JOURNAL_ENTRY, id="journal_entry"),
]


def _capture(tmp_path, spec, title="Existing"):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN), spec=spec, base_dir=tmp_path / spec.note_type
    )


def _entry(tmp_path, text, name="entry.md"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _process(tmp_path, spec, entry, actor=Actor.HUMAN):
    return execute_processing(
        ProcessingRequest(entry_path=entry, actor=actor), spec=spec, base_dir=tmp_path / spec.note_type
    )


def _section(body, heading):
    start = body.index(heading)
    end = body.find("\n## ", start + 1)
    return body[start:] if end == -1 else body[start:end]


@pytest.mark.parametrize("spec", CASES)
def test_a_title_collision_updates_instead_of_creating(tmp_path, spec):
    existing = _capture(tmp_path, spec)

    result = _process(tmp_path, spec, _entry(tmp_path, "Existing\n\nnew material\n"))

    assert result.applicable and result.operation == "update"
    assert result.project.id == existing.project.id
    assert result.path == existing.path


@pytest.mark.parametrize("spec", CASES)
def test_identity_and_lifecycle_are_untouched_only_notes_and_updated_change(tmp_path, spec):
    existing = _capture(tmp_path, spec)
    before = spec.read(existing.path)

    result = _process(tmp_path, spec, _entry(tmp_path, "Existing\n\nnew material\n"))
    after = spec.read(result.path)

    for key in ("id", "status", "context", "created", "note_type"):
        assert after["properties"][key] == before["properties"][key], key
    assert after["title"] == before["title"]


@pytest.mark.parametrize("spec", CASES)
def test_the_new_text_lands_only_in_the_landing_section(tmp_path, spec):
    _capture(tmp_path, spec)

    result = _process(tmp_path, spec, _entry(tmp_path, "Existing\n\nnew material\n"))

    body = spec.read(result.path)["body"]
    assert "new material" in _section(body, spec.notes_heading)


@pytest.mark.parametrize("spec", CASES)
def test_two_successive_updates_both_land_without_clobbering_each_other(tmp_path, spec):
    _capture(tmp_path, spec)
    _process(tmp_path, spec, _entry(tmp_path, "Existing\n\nfirst update\n", name="a.md"))

    result = _process(tmp_path, spec, _entry(tmp_path, "Existing\n\nsecond update\n", name="b.md"))

    body = spec.read(result.path)["body"]
    section = _section(body, spec.notes_heading)
    assert "first update" in section and "second update" in section
    assert section.index("first update") < section.index("second update")


@pytest.mark.parametrize("spec", CASES)
def test_the_event_names_the_existing_object_and_carries_no_target(tmp_path, spec):
    existing = _capture(tmp_path, spec)

    result = _process(tmp_path, spec, _entry(tmp_path, "Existing\n\nnew material\n"))

    assert result.event.event_type == f"{spec.display_name} Updated"
    assert result.event.object_id == existing.project.id
    assert result.event.workflow == "processing"
    assert result.event.target_id is None


@pytest.mark.parametrize("spec", CASES)
def test_the_inbox_entry_is_resolved(tmp_path, spec):
    _capture(tmp_path, spec)
    entry = _entry(tmp_path, "Existing\n\nnew material\n")

    _process(tmp_path, spec, entry)

    assert not entry.exists()


@pytest.mark.parametrize("spec", CASES)
def test_a_blank_remainder_resolves_the_entry_with_no_write_and_no_event(tmp_path, spec):
    """The default the issue flags: a title collision with nothing to add
    still resolves the entry (spec: "No domain change required -> Resolve"),
    but writes nothing and emits no event."""
    existing = _capture(tmp_path, spec)
    before = existing.path.read_bytes()
    entry = _entry(tmp_path, "Existing\n\n   \n")

    result = _process(tmp_path, spec, entry)

    assert result.applicable and result.operation == "update"
    assert result.event is None
    assert not entry.exists(), "still resolved"
    assert existing.path.read_bytes() == before, "nothing changed, nothing is rewritten"
    assert read_events(events_dir=tmp_path) == []


@pytest.mark.parametrize("spec", CASES)
def test_human_and_deterministic_actors_behave_identically(tmp_path, spec):
    _capture(tmp_path, spec, title="By Human")
    _capture(tmp_path, spec, title="By Machine")

    human = _process(tmp_path, spec, _entry(tmp_path, "By Human\n\nbody\n", "h.md"), Actor.HUMAN)
    machine = _process(tmp_path, spec, _entry(tmp_path, "By Machine\n\nbody\n", "m.md"), Actor.DETERMINISTIC)

    assert human.operation == machine.operation == "update"
    assert human.event.event_type == machine.event.event_type
    assert (human.event.actor, machine.event.actor) == ("human", "deterministic")
