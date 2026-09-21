"""Knowledge's Externalize enriches only Project, Area and Resource.

`knowledge-workflow.md` names exactly those three as enrichment targets;
Reference, Meeting and Journal Entry are Knowledge inputs. All against
`tmp_path`, never the real vault.
"""

import pytest

from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    KnowledgeRequest,
    execute_capture,
    execute_knowledge,
)
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE
from ohtli.vault_io.events import read_events

TARGETS = [
    pytest.param(PROJECT, id="project"),
    pytest.param(AREA, id="area"),
    pytest.param(RESOURCE, id="resource"),
]
NON_TARGETS = [
    pytest.param(REFERENCE, id="reference"),
    pytest.param(MEETING, id="meeting"),
    pytest.param(JOURNAL_ENTRY, id="journal_entry"),
]


def _capture(tmp_path, spec, title="Subject"):
    return execute_capture(
        ExecutionRequest(title=title, actor=Actor.HUMAN),
        spec=spec,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )


def _enrich(tmp_path, spec, title="Subject", actor=Actor.HUMAN):
    return execute_knowledge(
        KnowledgeRequest(
            title=title,
            understanding_title="Finding",
            understanding="Something learned.",
            provenance=("A source",),
            actor=actor,
        ),
        spec=spec,
        base_dir=tmp_path,
        events_dir=tmp_path,
    )


@pytest.mark.parametrize("spec", TARGETS)
def test_an_externalize_target_is_enriched(tmp_path, spec):
    captured = _capture(tmp_path, spec)

    result = _enrich(tmp_path, spec)

    assert result.applicable
    assert result.event.event_type == f"{spec.display_name} Knowledge Enriched"
    assert result.event.workflow == "knowledge"
    assert "Something learned." in captured.path.read_text(encoding="utf-8")


@pytest.mark.parametrize("spec", NON_TARGETS)
def test_a_non_target_is_refused_without_touching_the_note(tmp_path, spec):
    captured = _capture(tmp_path, spec)
    before = captured.path.read_bytes()

    result = _enrich(tmp_path, spec)

    assert not result.applicable
    assert result.project is None and result.path is None and result.event is None
    assert captured.path.read_bytes() == before
    assert [e.event_type for e in read_events(events_dir=tmp_path)] == [
        f"{spec.display_name} Created"
    ], "a refused enrichment emits no event"


@pytest.mark.parametrize("spec", NON_TARGETS)
def test_the_refusal_does_not_depend_on_the_note_existing(tmp_path, spec):
    result = _enrich(tmp_path, spec, title="Never Captured")

    assert not result.applicable and result.event is None
    assert read_events(events_dir=tmp_path) == []


@pytest.mark.parametrize("spec", NON_TARGETS)
def test_human_and_deterministic_actors_are_refused_identically(tmp_path, spec):
    _capture(tmp_path, spec)

    human = _enrich(tmp_path, spec, actor=Actor.HUMAN)
    machine = _enrich(tmp_path, spec, actor=Actor.DETERMINISTIC)

    assert not human.applicable and not machine.applicable
    assert human.event is None and machine.event is None


def test_the_target_set_and_the_specs_cover_every_domain_object():
    """If a seventh Domain Object is added, this forces a deliberate decision
    about whether it is an Externalize target."""
    assert {p.values[0].domain_type.__name__ for p in TARGETS + NON_TARGETS} == {
        "Project", "Area", "Resource", "Reference", "Meeting", "JournalEntry",
    }
