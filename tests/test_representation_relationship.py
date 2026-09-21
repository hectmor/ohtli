from datetime import date

from ohtli.domain.project import Project
from ohtli.representation.project import to_representation
from ohtli.representation.relationship import relate, relationships_of_type, unrelate

_LINK = "[[areas/health|Health]]"


def _project_rep():
    return to_representation(Project(title="P"), today=date(2026, 9, 1))


def _link(rep, **overrides):
    kwargs = dict(
        relationship_type="belongs to",
        target_id="area-1",
        target_type="area",
        target_link=_LINK,
        today=date(2026, 9, 20),
    )
    kwargs.update(overrides)
    return relate(rep, **kwargs)


def test_a_never_linked_note_has_no_relationships_key():
    rep = _project_rep()

    assert "relationships" not in rep["properties"]
    assert relationships_of_type(rep, "belongs to") == []


def test_relate_adds_one_instance_with_its_own_identity():
    linked = _link(_project_rep())

    (entry,) = linked["properties"]["relationships"]
    assert set(entry) == {"id", "type", "target_id", "target_type", "target_link"}
    assert entry["type"] == "belongs to"
    assert entry["target_id"] == "area-1"
    assert entry["target_type"] == "area"
    assert entry["target_link"] == _LINK
    assert entry["id"], "a relationship instance has its own identity"


def test_relationship_identity_is_not_the_identity_of_either_object():
    rep = _project_rep()
    (entry,) = _link(rep)["properties"]["relationships"]

    assert entry["id"] not in (rep["properties"]["id"], "area-1")


def test_two_instances_get_distinct_identities():
    once = _link(_project_rep())
    twice = _link(once, relationship_type="supports", target_id="area-2")

    ids = [e["id"] for e in twice["properties"]["relationships"]]
    assert len(ids) == 2 and ids[0] != ids[1]


def test_relate_only_changes_relationships_and_updated():
    rep = _project_rep()
    linked = _link(rep)

    changed = {
        k
        for k in linked["properties"]
        if k not in rep["properties"] or linked["properties"][k] != rep["properties"][k]
    }
    assert changed == {"relationships", "updated"}
    assert linked["properties"]["updated"] == "2026-09-20"
    assert linked["title"] == rep["title"]
    assert linked["body"] == rep["body"]


def test_relate_does_not_mutate_its_input():
    rep = _project_rep()
    _link(rep)

    assert "relationships" not in rep["properties"]


def test_unrelating_the_last_instance_removes_the_key_entirely():
    rep = _project_rep()
    unlinked = unrelate(_link(rep), relationship_type="belongs to", today=date(2026, 9, 21))

    assert "relationships" not in unlinked["properties"]
    assert set(unlinked["properties"]) == set(rep["properties"]), (
        "an unlinked note must return to exactly the shape of a never-linked one"
    )


def test_unrelate_keeps_instances_of_other_types():
    linked = _link(_link(_project_rep()), relationship_type="supports", target_id="area-2")
    unlinked = unrelate(linked, relationship_type="belongs to")

    (remaining,) = unlinked["properties"]["relationships"]
    assert remaining["type"] == "supports"


def test_unrelate_does_not_mutate_its_input():
    linked = _link(_project_rep())
    unrelate(linked, relationship_type="belongs to")

    assert len(linked["properties"]["relationships"]) == 1


def test_unrelate_on_a_note_without_relationships_is_harmless():
    rep = _project_rep()
    unlinked = unrelate(rep, relationship_type="belongs to", today=date(2026, 9, 21))

    assert "relationships" not in unlinked["properties"]
