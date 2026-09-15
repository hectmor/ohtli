from datetime import date

from ohtli.domain.meeting import Meeting
from ohtli.representation.meeting import from_representation, to_representation


def test_representation_round_trip_preserves_identity_and_title():
    meeting = Meeting(title="Round Trip")
    rep = to_representation(meeting, today=date(2026, 9, 15))
    restored = from_representation(rep)

    assert restored.id == meeting.id
    assert restored.title == meeting.title


def test_representation_has_canonical_property_order_and_defaults():
    meeting = Meeting(title="Ordered")
    rep = to_representation(meeting, today=date(2026, 9, 15))
    keys = list(rep["properties"].keys())

    assert keys[:4] == ["id", "note_type", "created", "updated"]
    assert rep["properties"]["note_type"] == "meeting"
    assert rep["properties"]["status"] == "recorded"
    assert rep["properties"]["context"] == "operational"


def test_representation_body_matches_the_existing_template_sections():
    rep = to_representation(Meeting(title="Weekly Sync"), today=date(2026, 9, 15))

    for section in (
        "## Objective",
        "## Participants",
        "## Agenda",
        "## Discussion",
        "## Decisions",
        "## Action Items",
        "## References",
    ):
        assert section in rep["body"]


def test_representation_without_notes_leaves_the_discussion_section_blank():
    rep = to_representation(Meeting(title="Blank"), today=date(2026, 9, 15))

    assert "## Discussion\n\n## Decisions" in rep["body"]


def test_representation_places_notes_in_the_discussion_section():
    rep = to_representation(
        Meeting(title="With Notes"), today=date(2026, 9, 15), notes="Discussed the roadmap."
    )

    assert "## Discussion\n\nDiscussed the roadmap.\n\n## Decisions" in rep["body"]


def test_carried_headings_are_nested_below_the_discussion_section():
    rep = to_representation(
        Meeting(title="T"), today=date(2026, 9, 15), notes="## Objective\nRealigned scope."
    )

    assert "### Objective\nRealigned scope." in rep["body"]


def test_notes_are_not_part_of_the_domain_object():
    meeting = Meeting(title="Round Trip")
    rep = to_representation(meeting, today=date(2026, 9, 15), notes="Some body text.")
    restored = from_representation(rep)

    assert restored == meeting
    assert not hasattr(restored, "notes")
