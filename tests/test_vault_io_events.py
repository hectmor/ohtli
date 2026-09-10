from ohtli.event.event import Event
from ohtli.vault_io.events import append_event, read_events


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


def test_read_events_on_missing_file_returns_empty_list(tmp_path):
    assert read_events(events_dir=tmp_path) == []


def test_append_then_read_round_trip(tmp_path):
    event = _make_event()
    append_event(event, events_dir=tmp_path)

    events = read_events(events_dir=tmp_path)
    assert len(events) == 1
    assert events[0] == event


def test_events_are_returned_in_chronological_append_order(tmp_path):
    first = _make_event(object_id="first")
    second = _make_event(object_id="second", event_type="Project Archived", workflow="archive")
    append_event(first, events_dir=tmp_path)
    append_event(second, events_dir=tmp_path)

    events = read_events(events_dir=tmp_path)
    assert [e.object_id for e in events] == ["first", "second"]


def test_append_event_does_not_alter_previously_written_lines(tmp_path):
    append_event(_make_event(object_id="first"), events_dir=tmp_path)
    before = read_events(events_dir=tmp_path)[0]

    append_event(_make_event(object_id="second"), events_dir=tmp_path)
    after = read_events(events_dir=tmp_path)[0]

    assert before == after
