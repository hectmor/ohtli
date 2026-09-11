from ohtli.event.event import Event
from ohtli.workflow.review import ReviewConclusion, assess, observe


def _event(**overrides):
    defaults = dict(
        event_type="Project Progress Observed",
        object_id="obj-1",
        object_type="Project",
        actor="human",
        execution_id="exec-1",
        workflow="evaluation",
        occurred_at="2026-09-01T00:00:00+00:00",
    )
    defaults.update(overrides)
    return Event(**defaults)


def test_observe_filters_by_object_id():
    events = [_event(object_id="obj-1"), _event(object_id="obj-2")]
    assert observe(events, "obj-1") == [events[0]]


def test_observe_filters_by_since():
    early = _event(occurred_at="2026-01-01T00:00:00+00:00")
    late = _event(occurred_at="2026-09-01T00:00:00+00:00")
    assert observe([early, late], "obj-1", since="2026-06-01") == [late]


def test_observe_with_since_none_returns_full_history():
    events = [_event(occurred_at="2020-01-01T00:00:00+00:00")]
    assert observe(events, "obj-1", since=None) == events


def test_assess_is_insufficient_basis_when_no_evaluation_events():
    result = assess({"status": "planned"}, [])
    assert result.conclusion == ReviewConclusion.INSUFFICIENT_BASIS


def test_assess_requires_attention_when_outcome_reached_but_status_not_completed():
    events = [_event(event_type="Project Outcome Reached")]
    result = assess({"status": "active"}, events)
    assert result.conclusion == ReviewConclusion.ATTENTION_REQUIRED
    assert "Outcome Reached" in " ".join(result.basis)


def test_assess_does_not_require_attention_when_outcome_reached_and_status_completed():
    events = [_event(event_type="Project Outcome Reached")]
    result = assess({"status": "completed"}, events)
    assert result.conclusion != ReviewConclusion.ATTENTION_REQUIRED


def test_assess_requires_attention_when_latest_evaluation_is_degradation():
    events = [
        _event(event_type="Area Maintenance Performed", occurred_at="2026-01-01T00:00:00+00:00"),
        _event(event_type="Area Degradation Observed", occurred_at="2026-06-01T00:00:00+00:00"),
    ]
    result = assess({"status": "active"}, events)
    assert result.conclusion == ReviewConclusion.ATTENTION_REQUIRED


def test_assess_defaults_to_no_attention_required():
    events = [_event(event_type="Project Progress Observed")]
    result = assess({"status": "active"}, events)
    assert result.conclusion == ReviewConclusion.NO_ATTENTION_REQUIRED
