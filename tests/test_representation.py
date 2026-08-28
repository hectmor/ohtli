from datetime import date

from ohtli.domain.project import Project
from ohtli.representation.project import from_representation, to_representation


def test_representation_round_trip_preserves_identity_and_title():
    project = Project(title="Round Trip")
    rep = to_representation(project, today=date(2026, 8, 25))
    restored = from_representation(rep)

    assert restored.id == project.id
    assert restored.title == project.title


def test_representation_has_canonical_property_order_and_status():
    project = Project(title="Ordered")
    rep = to_representation(project, today=date(2026, 8, 25))
    keys = list(rep["properties"].keys())

    assert keys[:4] == ["id", "note_type", "created", "updated"]
    assert rep["properties"]["status"] == "planned"
