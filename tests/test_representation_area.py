from datetime import date

from ohtli.domain.area import Area
from ohtli.representation.area import from_representation, to_representation


def test_representation_round_trip_preserves_identity_and_title():
    area = Area(title="Round Trip")
    rep = to_representation(area, today=date(2026, 8, 25))
    restored = from_representation(rep)

    assert restored.id == area.id
    assert restored.title == area.title


def test_representation_has_canonical_property_order_and_lifecycle_status():
    area = Area(title="Ordered")
    rep = to_representation(area, today=date(2026, 8, 25))
    keys = list(rep["properties"].keys())

    assert keys[:4] == ["id", "note_type", "created", "updated"]
    assert rep["properties"]["note_type"] == "area"
    assert rep["properties"]["status"] == "active"


def test_representation_without_notes_leaves_the_notes_section_blank():
    rep = to_representation(Area(title="Blank"), today=date(2026, 8, 25))

    assert rep["body"].rstrip("\n").endswith("## Notes")


def test_representation_places_notes_in_the_notes_section():
    rep = to_representation(
        Area(title="With Notes"), today=date(2026, 8, 25), notes="Captured at standup."
    )

    assert "## Notes\n\nCaptured at standup." in rep["body"]


def test_carried_headings_are_nested_below_the_notes_section():
    rep = to_representation(
        Area(title="T"), today=date(2026, 8, 25), notes="## Objective\nReduce drop-off."
    )

    assert "### Objective\nReduce drop-off." in rep["body"]


def test_notes_are_not_part_of_the_domain_object():
    """Notes are Representation, not Domain: they must not survive the
    round-trip back into an Area."""
    area = Area(title="Round Trip")
    rep = to_representation(area, today=date(2026, 8, 25), notes="Some body text.")
    restored = from_representation(rep)

    assert restored == area
    assert not hasattr(restored, "notes")
