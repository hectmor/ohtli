import dataclasses

import pytest

from ohtli.event.event import Event


def _make_event(**overrides):
    defaults = dict(
        event_type="Project Created",
        object_id="abc-123",
        object_type="Project",
        actor="human",
        execution_id="exec-1",
        workflow="capture",
    )
    defaults.update(overrides)
    return Event(**defaults)


def test_event_is_immutable():
    event = _make_event()
    with pytest.raises(dataclasses.FrozenInstanceError):
        event.event_type = "Something Else"


def test_event_generates_a_unique_id_and_timestamp():
    first = _make_event()
    second = _make_event()

    assert first.event_id != second.event_id
    assert first.occurred_at
    assert second.occurred_at


def test_event_has_no_title_field():
    assert not hasattr(_make_event(), "title")
