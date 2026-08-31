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


def test_representation_without_notes_leaves_the_notes_section_blank():
    rep = to_representation(Project(title="Blank"), today=date(2026, 8, 25))

    assert "## Notes\n\n## References" in rep["body"]


def test_representation_places_notes_in_the_notes_section():
    rep = to_representation(
        Project(title="With Notes"), today=date(2026, 8, 25), notes="Captured at standup."
    )

    assert "## Notes\n\nCaptured at standup.\n\n## References" in rep["body"]


def test_notes_are_not_part_of_the_domain_object():
    """Notes are Representation, not Domain: they must not survive the
    round-trip back into a Project."""
    project = Project(title="Round Trip")
    rep = to_representation(project, today=date(2026, 8, 25), notes="Some body text.")
    restored = from_representation(rep)

    assert restored == project
    assert not hasattr(restored, "notes")
