"""Event names use each Domain Object's display name ("Journal Entry Created"),
while `object_type` stays the class name (`JournalEntry`).

The Event Model documents name the events; this file checks the code against
those documents rather than only against its own strings. All against `tmp_path`.
"""

import json
from pathlib import Path

import pytest

from ohtli.event.event import Event
from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    RelateRequest,
    execute_capture,
    execute_relate,
)
from ohtli.execution.specs import (
    ALL_SPECS,
    JOURNAL_ENTRY,
    PROJECT,
    RESOURCE,
    display_name_of,
)
from ohtli.vault_io import paths
from ohtli.vault_io.events import read_events
from ohtli.workflow import review as review_workflow

_EVENT_MODEL = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "event-model" / "README.md"


def _capture(tmp_path, spec, title="Subject"):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path / spec.note_type,
        events_dir=tmp_path,
    )


# ---- display_name on the specs ----------------------------------------------------


def test_every_spec_has_a_distinct_non_empty_display_name():
    names = [spec.display_name for spec in ALL_SPECS]

    assert all(name.strip() for name in names)
    assert len(set(names)) == len(names) == 6


def test_display_name_of_round_trips_every_class_name():
    for spec in ALL_SPECS:
        assert display_name_of(spec.domain_type.__name__) == spec.display_name
    assert display_name_of("JournalEntry") == "Journal Entry"


def test_an_unknown_type_name_raises_instead_of_leaking_a_class_name():
    with pytest.raises(KeyError):
        display_name_of("Nope")
    with pytest.raises(KeyError):
        display_name_of("Journal Entry")  # a display name is not a class name


def test_the_display_name_is_not_the_lookup_key_of_the_relationship_table():
    """The table is keyed by class name; a display name must not be a valid key."""
    from ohtli.workflow import processing

    assert processing.relationship_for_pair("JournalEntry", "Project") is not None
    assert processing.relationship_for_pair("Journal Entry", "Project") is None


# ---- the code matches the Event Model documents -----------------------------------


def test_the_event_model_documents_the_names_this_test_relies_on():
    text = _EVENT_MODEL.read_text(encoding="utf-8")

    assert "Journal Entry Created" in text
    assert "Resource Linked to Project" in text


def test_a_captured_journal_entry_emits_the_name_the_event_model_documents(tmp_path):
    assert "Journal Entry Created" in _EVENT_MODEL.read_text(encoding="utf-8")

    result = _capture(tmp_path, JOURNAL_ENTRY)

    assert result.event.event_type == "Journal Entry Created"


def test_a_link_emits_the_relationship_event_name_the_event_model_documents(tmp_path):
    """`Resource supports Project` is the relationship behind the documented
    example "Resource Linked to Project"."""
    assert "Resource Linked to Project" in _EVENT_MODEL.read_text(encoding="utf-8")
    _capture(tmp_path, RESOURCE, "Res")
    _capture(tmp_path, PROJECT, "Proj")

    result = execute_relate(
        RelateRequest(source_title="Res", target_title="Proj", actor=Actor.HUMAN, relationship_type="supports"),
        source_spec=RESOURCE,
        target_spec=PROJECT,
        base_dir=tmp_path / RESOURCE.note_type,
        target_base_dir=tmp_path / PROJECT.note_type,
        events_dir=tmp_path,
    )

    assert result.event.event_type == "Resource Linked to Project"


def test_no_emitted_event_name_contains_a_class_name_that_has_a_display_name(tmp_path):
    """The leak this exists to prevent: `JournalEntry` must never appear in an
    event name, on either side of a relationship event."""
    je = _capture(tmp_path, JOURNAL_ENTRY, "Entry")
    _capture(tmp_path, PROJECT, "Proj")
    execute_relate(
        RelateRequest(source_title="Entry", target_title="Proj", actor=Actor.HUMAN, relationship_type="references"),
        source_spec=JOURNAL_ENTRY,
        target_spec=PROJECT,
        base_dir=tmp_path / JOURNAL_ENTRY.note_type,
        target_base_dir=tmp_path / PROJECT.note_type,
        events_dir=tmp_path,
    )
    execute_relate(
        RelateRequest(source_title="Proj", target_title="Entry", actor=Actor.HUMAN, relationship_type="references"),
        source_spec=PROJECT,
        target_spec=JOURNAL_ENTRY,
        base_dir=tmp_path / PROJECT.note_type,
        target_base_dir=tmp_path / JOURNAL_ENTRY.note_type,
        events_dir=tmp_path,
    )

    names = [e.event_type for e in read_events(events_dir=tmp_path)]

    assert "Journal Entry Created" in names
    assert "Journal Entry Linked to Project" in names
    assert "Project Linked to Journal Entry" in names
    assert not [n for n in names if "JournalEntry" in n], names
    assert je.applicable


# ---- object_type stays the class name ---------------------------------------------


@pytest.mark.parametrize("spec", ALL_SPECS, ids=[s.note_type for s in ALL_SPECS])
def test_object_type_is_still_the_class_name_for_every_type(tmp_path, spec):
    result = _capture(tmp_path, spec)

    assert result.event.object_type == spec.domain_type.__name__
    assert result.event.event_type == f"{spec.display_name} Created"


def test_object_type_of_a_relationship_event_is_the_sources_class_name(tmp_path):
    _capture(tmp_path, JOURNAL_ENTRY, "Entry")
    _capture(tmp_path, PROJECT, "Proj")

    result = execute_relate(
        RelateRequest(source_title="Entry", target_title="Proj", actor=Actor.HUMAN, relationship_type="references"),
        source_spec=JOURNAL_ENTRY,
        target_spec=PROJECT,
        base_dir=tmp_path / JOURNAL_ENTRY.note_type,
        target_base_dir=tmp_path / PROJECT.note_type,
        events_dir=tmp_path,
    )

    assert result.event.object_type == "JournalEntry"
    assert result.event.event_type == "Journal Entry Linked to Project"


# ---- a log holding both the old and the new names ---------------------------------


def _legacy_line(event_type, object_id, workflow="capture"):
    return json.dumps(
        {
            "event_type": event_type,
            "object_id": object_id,
            "object_type": "JournalEntry",
            "actor": "human",
            "execution_id": "old",
            "workflow": workflow,
            "event_id": f"old-{event_type}",
            "occurred_at": "2026-09-01T00:00:00+00:00",
        }
    )


def test_a_log_with_both_the_old_and_the_new_names_is_read_without_error(tmp_path):
    """Historical events are immutable, so old `JournalEntry ...` lines stay in
    the log next to new `Journal Entry ...` ones."""
    log = paths.events_file_path(tmp_path)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(_legacy_line("JournalEntry Created", "je-1") + "\n", encoding="utf-8")

    new = _capture(tmp_path, JOURNAL_ENTRY, "New Entry")
    events = read_events(events_dir=tmp_path)

    assert [e.event_type for e in events] == ["JournalEntry Created", "Journal Entry Created"]
    assert events[0].object_type == events[1].object_type == "JournalEntry"
    assert new.applicable


def test_appending_new_events_never_modifies_the_existing_lines(tmp_path):
    log = paths.events_file_path(tmp_path)
    log.parent.mkdir(parents=True, exist_ok=True)
    legacy = _legacy_line("JournalEntry Created", "je-1") + "\n"
    log.write_text(legacy, encoding="utf-8")

    _capture(tmp_path, JOURNAL_ENTRY, "New Entry")

    assert log.read_text(encoding="utf-8").startswith(legacy), "old lines are byte-identical"


def test_review_observes_by_object_id_whatever_form_the_name_takes(tmp_path):
    def event(event_type, object_id="obj"):
        return Event(
            event_type=event_type,
            object_id=object_id,
            object_type="JournalEntry",
            actor="human",
            execution_id="e",
            workflow="evaluation",
        )

    events = [event("JournalEntry Created"), event("Journal Entry Created"), event("Other Created", "other")]

    assert len(review_workflow.observe(events, "obj")) == 2


@pytest.mark.parametrize("prefix", ["Project", "JournalEntry", "Journal Entry"])
def test_review_assesses_by_the_suffix_so_the_prefix_form_is_irrelevant(prefix):
    def evaluation(suffix):
        return Event(
            event_type=f"{prefix} {suffix}",
            object_id="obj",
            object_type="X",
            actor="human",
            execution_id="e",
            workflow="evaluation",
        )

    reached = review_workflow.assess({"status": "in_progress"}, [evaluation("Outcome Reached")])
    degraded = review_workflow.assess({"status": "completed"}, [evaluation("Degradation Observed")])
    none = review_workflow.assess({"status": "in_progress"}, [])

    assert reached.conclusion == review_workflow.ReviewConclusion.ATTENTION_REQUIRED
    assert degraded.conclusion == review_workflow.ReviewConclusion.ATTENTION_REQUIRED
    assert none.conclusion == review_workflow.ReviewConclusion.INSUFFICIENT_BASIS
