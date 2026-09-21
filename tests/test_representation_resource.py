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


def test_representation_body_has_a_notes_section():
    rep = to_representation(Resource(title="Guide"), today=date(2026, 9, 14))

    assert "## Notes" in rep["body"]
    assert rep["body"].index("## Examples") < rep["body"].index("## Notes") < rep["body"].index("## References")


def test_carried_notes_land_in_the_notes_section_nested_below_it():
    rep = to_representation(Resource(title="Guide"), today=date(2026, 9, 14), notes="raw text\n# heading")

    body = rep["body"]
    notes_section = body[body.index("## Notes") : body.index("## References")]
    assert "raw text" in notes_section
    assert "### heading" in notes_section
    for other in ("## Summary", "## Content", "## Examples"):
        section = body[body.index(other) : body.index("\n## ", body.index(other) + 1)]
        assert "raw text" not in section, f"raw Inbox text must not land under {other}"


def test_without_notes_the_rest_of_the_body_is_unchanged():
    plain = to_representation(Resource(title="Guide"), today=date(2026, 9, 14))["body"]
    with_none = to_representation(Resource(title="Guide"), today=date(2026, 9, 14), notes=None)["body"]

    assert plain == with_none
    assert "raw" not in plain
