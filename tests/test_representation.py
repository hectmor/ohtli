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


def _body_with_notes(notes: str) -> str:
    return to_representation(Project(title="T"), today=date(2026, 8, 25), notes=notes)["body"]


def test_carried_headings_are_nested_below_the_notes_section():
    body = _body_with_notes("## Objective\nReduce drop-off.")

    assert "### Objective\nReduce drop-off." in body
    assert body.count("## Objective") == 2, "template heading + the nested one, not a duplicate pair"
    assert "\n## Objective\nReduce drop-off." not in body


def test_carried_headings_keep_their_relative_structure():
    body = _body_with_notes("# Top\n\n## Under Top\n\n### Deeper")

    assert "# Top" in body
    assert "### Top" in body
    assert "#### Under Top" in body
    assert "##### Deeper" in body


def test_headings_already_deep_enough_are_left_alone():
    body = _body_with_notes("### Already Deep\n\n#### Deeper Still")

    assert "### Already Deep" in body
    assert "#### Deeper Still" in body


def test_headings_inside_fenced_code_blocks_are_not_shifted():
    body = _body_with_notes("## Real Heading\n\n```bash\n# not a heading\n```")

    assert "### Real Heading" in body
    assert "# not a heading" in body
    assert "## not a heading" not in body


def test_tilde_fences_are_honoured_and_backticks_inside_them_do_not_close_them():
    body = _body_with_notes("~~~\n# still code\n```\n# also code\n~~~\n\n## After Fence")

    assert "# still code" in body
    assert "# also code" in body
    assert "### After Fence" in body


def test_notes_without_headings_are_carried_verbatim():
    body = _body_with_notes("Just prose.\n\n- and a list")

    assert "Just prose.\n\n- and a list" in body


def test_notes_are_not_part_of_the_domain_object():
    """Notes are Representation, not Domain: they must not survive the
    round-trip back into a Project."""
    project = Project(title="Round Trip")
    rep = to_representation(project, today=date(2026, 8, 25), notes="Some body text.")
    restored = from_representation(rep)

    assert restored == project
    assert not hasattr(restored, "notes")
