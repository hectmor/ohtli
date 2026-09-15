from datetime import date

from ohtli.domain.reference import Reference
from ohtli.representation.reference import from_representation, to_representation


def test_representation_round_trip_preserves_identity_and_title():
    reference = Reference(title="Round Trip")
    rep = to_representation(reference, today=date(2026, 9, 15))
    restored = from_representation(rep)

    assert restored.id == reference.id
    assert restored.title == reference.title


def test_representation_has_canonical_property_order_and_defaults():
    reference = Reference(title="Ordered")
    rep = to_representation(reference, today=date(2026, 9, 15))
    keys = list(rep["properties"].keys())

    assert keys[:4] == ["id", "note_type", "created", "updated"]
    assert rep["properties"]["note_type"] == "reference"
    assert rep["properties"]["status"] == "captured"
    assert rep["properties"]["context"] == "operational"


def test_representation_body_matches_the_existing_template_sections():
    rep = to_representation(Reference(title="A Paper"), today=date(2026, 9, 15))

    for section in ("## Citation", "## Summary", "## Key Points", "## Notes", "## Links"):
        assert section in rep["body"]


def test_representation_without_notes_leaves_the_notes_section_blank():
    rep = to_representation(Reference(title="Blank"), today=date(2026, 9, 15))

    assert "## Notes\n\n## Links" in rep["body"]


def test_representation_places_notes_in_the_notes_section():
    rep = to_representation(
        Reference(title="With Notes"), today=date(2026, 9, 15), notes="Captured from Processing."
    )

    assert "## Notes\n\nCaptured from Processing.\n\n## Links" in rep["body"]


def test_notes_are_not_part_of_the_domain_object():
    reference = Reference(title="Round Trip")
    rep = to_representation(reference, today=date(2026, 9, 15), notes="Some body text.")
    restored = from_representation(rep)

    assert restored == reference
    assert not hasattr(restored, "notes")
