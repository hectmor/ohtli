"""Processing (Inbox entry -> Domain Object) for every Domain Object.

Everything runs against `tmp_path`, never the real vault. Raw Inbox text must
land in the one section no Essential Attribute/Responsibility claims: `Notes`,
or `Discussion` for Meeting.
"""

import re

import pytest

from ohtli.execution.execution import Actor, ProcessingRequest, execute_processing
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.vault_io.events import read_events

# spec, folder, the section that receives raw Inbox text
CASES = [
    pytest.param(PROJECT, "projects", "## Notes", id="project"),
    pytest.param(AREA, "areas", "## Notes", id="area"),
    pytest.param(RESOURCE, "resources", "## Notes", id="resource"),
    pytest.param(REFERENCE, "references", "## Notes", id="reference"),
    pytest.param(MEETING, "meetings", "## Discussion", id="meeting"),
    pytest.param(JOURNAL_ENTRY, "journal", "## Notes", id="journal_entry"),
]


def _entry(tmp_path, text="From Inbox\n\nraw body line\n", name="entry.md"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def _process(tmp_path, spec, folder, entry, actor=Actor.HUMAN):
    return execute_processing(
        ProcessingRequest(entry_path=entry, actor=actor),
        spec=spec,
        base_dir=tmp_path / folder,
        events_dir=tmp_path,
    )


def _section(body, heading):
    start = body.index(heading)
    end = body.find("\n## ", start + 1)
    return body[start:] if end == -1 else body[start:end]


@pytest.mark.parametrize("spec,folder,heading", CASES)
def test_an_inbox_entry_becomes_the_chosen_domain_object(tmp_path, spec, folder, heading):
    entry = _entry(tmp_path)

    result = _process(tmp_path, spec, folder, entry)

    assert result.applicable
    assert isinstance(result.project, spec.domain_type)
    assert result.project.title == "From Inbox"
    assert result.path.parent == tmp_path / folder
    representation = spec.read(result.path)
    assert representation["properties"]["note_type"] == spec.note_type
    assert not entry.exists(), "a processed Inbox entry must be resolved"


@pytest.mark.parametrize("spec,folder,heading", CASES)
def test_raw_text_lands_only_in_the_unclaimed_section(tmp_path, spec, folder, heading):
    result = _process(tmp_path, spec, folder, _entry(tmp_path))

    body = spec.read(result.path)["body"]
    assert "raw body line" in _section(body, heading)
    assert body.count("raw body line") == 1, "the raw text must appear exactly once"


@pytest.mark.parametrize("spec,folder,heading", CASES)
def test_processing_emits_a_created_event_from_the_processing_workflow(tmp_path, spec, folder, heading):
    result = _process(tmp_path, spec, folder, _entry(tmp_path))

    (event,) = read_events(events_dir=tmp_path)
    assert event.event_type == f"{spec.display_name} Created"
    assert event.workflow == "processing"
    assert event.object_id == result.project.id
    assert event.object_type == spec.domain_type.__name__


@pytest.mark.parametrize("spec,folder,heading", CASES)
def test_a_duplicate_title_updates_the_existing_object_instead_of_being_refused(tmp_path, spec, folder, heading):
    """Was `test_a_duplicate_title_is_refused_with_no_effects`: a title
    collision is no longer refused, it means Update (Phase 34)."""
    first = _process(tmp_path, spec, folder, _entry(tmp_path, name="first.md"))
    before = spec.read(first.path)
    second = _entry(tmp_path, text="From Inbox\n\nother body\n", name="second.md")

    result = _process(tmp_path, spec, folder, second)

    assert result.applicable and result.operation == "update"
    assert result.project.id == first.project.id
    assert not second.exists(), "the entry is resolved either way"
    assert sorted(p.name for p in (tmp_path / folder).iterdir()) == [first.path.name]

    after = spec.read(result.path)
    for key in ("id", "status", "context", "created", "note_type"):
        assert after["properties"][key] == before["properties"][key], key

    assert "other body" in _section(after["body"], heading)
    other_headings = [h for h in re.findall(r"^## .+$", after["body"], re.MULTILINE) if h != heading]
    for other in other_headings:
        assert "other body" not in _section(after["body"], other), f"leaked into {other}"

    assert result.event.event_type == f"{spec.display_name} Updated"
    assert result.event.object_id == first.project.id
    assert result.event.workflow == "processing"
    assert len(read_events(events_dir=tmp_path)) == 2


@pytest.mark.parametrize("spec,folder,heading", CASES)
def test_a_blank_entry_is_refused(tmp_path, spec, folder, heading):
    entry = _entry(tmp_path, text="\n   \n")

    result = _process(tmp_path, spec, folder, entry)

    assert not result.applicable and entry.exists()
    assert read_events(events_dir=tmp_path) == []


@pytest.mark.parametrize("spec,folder,heading", CASES)
def test_human_and_deterministic_actors_behave_identically(tmp_path, spec, folder, heading):
    human = _process(tmp_path, spec, folder, _entry(tmp_path, "By Human\n\nbody\n", "h.md"), Actor.HUMAN)
    machine = _process(
        tmp_path, spec, folder, _entry(tmp_path, "By Machine\n\nbody\n", "m.md"), Actor.DETERMINISTIC
    )

    assert human.applicable and machine.applicable
    events = {e.object_id: e for e in read_events(events_dir=tmp_path)}
    assert events[human.project.id].event_type == events[machine.project.id].event_type
    assert (events[human.project.id].actor, events[machine.project.id].actor) == ("human", "deterministic")
    assert spec.read(human.path)["body"].count("body") == spec.read(machine.path)["body"].count("body")


def test_the_same_title_can_exist_as_different_domain_objects(tmp_path):
    """Applicability is per Domain Object namespace, as with Capture."""
    as_project = _process(tmp_path, PROJECT, "projects", _entry(tmp_path, name="a.md"))
    as_resource = _process(tmp_path, RESOURCE, "resources", _entry(tmp_path, name="b.md"))

    assert as_project.applicable and as_resource.applicable
    assert as_project.project.id != as_resource.project.id
