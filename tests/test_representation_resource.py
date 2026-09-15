from datetime import date

from ohtli.domain.resource import Resource
from ohtli.representation.resource import from_representation, to_representation


def test_representation_round_trip_preserves_identity_and_title():
    resource = Resource(title="Round Trip")
    rep = to_representation(resource, today=date(2026, 9, 14))
    restored = from_representation(rep)

    assert restored.id == resource.id
    assert restored.title == resource.title


def test_representation_has_canonical_property_order_and_defaults():
    resource = Resource(title="Ordered")
    rep = to_representation(resource, today=date(2026, 9, 14))
    keys = list(rep["properties"].keys())

    assert keys[:4] == ["id", "note_type", "created", "updated"]
    assert rep["properties"]["note_type"] == "resource"
    assert rep["properties"]["status"] == "draft"
    assert rep["properties"]["context"] == "operational"


def test_representation_body_matches_the_existing_template_sections():
    rep = to_representation(Resource(title="Guide"), today=date(2026, 9, 14))

    for section in ("## Summary", "## Content", "## Examples", "## References", "## Related Notes"):
        assert section in rep["body"]


def test_notes_are_not_part_of_the_domain_object():
    resource = Resource(title="Round Trip")
    rep = to_representation(resource, today=date(2026, 9, 14))
    restored = from_representation(rep)

    assert restored == resource
