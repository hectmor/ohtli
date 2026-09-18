from datetime import date

from ohtli.domain.journal_entry import JournalEntry
from ohtli.representation.journal_entry import from_representation, to_representation


def test_representation_round_trip_preserves_identity_and_title():
    entry = JournalEntry(title="2026-07-29")
    rep = to_representation(entry, today=date(2026, 9, 18))
    restored = from_representation(rep)

    assert restored.id == entry.id
    assert restored.title == entry.title


def test_representation_has_canonical_property_order_and_defaults():
    rep = to_representation(JournalEntry(title="2026-07-29"), today=date(2026, 9, 18))
    keys = list(rep["properties"].keys())

    assert keys[:4] == ["id", "note_type", "created", "updated"]
    assert rep["properties"]["note_type"] == "journal_entry"
    assert rep["properties"]["status"] == "created"
    assert rep["properties"]["context"] == "operational"


def test_note_type_is_distinct_from_the_daily_note_convention():
    rep = to_representation(JournalEntry(title="2026-07-29"), today=date(2026, 9, 18))

    assert rep["properties"]["note_type"] != "daily_note"


def test_representation_body_has_one_section_per_responsibility_and_no_content_section():
    rep = to_representation(JournalEntry(title="2026-07-29"), today=date(2026, 9, 18))

    for section in ("## Ideas", "## Reflections", "## Observations", "## Notes", "## References"):
        assert section in rep["body"]
    assert "## Content" not in rep["body"]


def test_representation_without_notes_leaves_the_notes_section_blank():
    rep = to_representation(JournalEntry(title="Blank"), today=date(2026, 9, 18))

    assert "## Notes\n\n## References" in rep["body"]


def test_representation_places_notes_in_the_notes_section():
    rep = to_representation(
        JournalEntry(title="With Notes"), today=date(2026, 9, 18), notes="A passing thought."
    )

    assert "## Notes\n\nA passing thought.\n\n## References" in rep["body"]


def test_notes_are_not_part_of_the_domain_object():
    entry = JournalEntry(title="Round Trip")
    rep = to_representation(entry, today=date(2026, 9, 18), notes="Some body text.")
    restored = from_representation(rep)

    assert restored == entry
    assert not hasattr(restored, "notes")
