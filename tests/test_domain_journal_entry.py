from ohtli.domain.journal_entry import JournalEntry


def test_journal_entry_has_stable_generated_identity():
    e1 = JournalEntry(title="2026-07-29")
    e2 = JournalEntry(title="2026-07-29")
    assert e1.id != e2.id, "two distinct instances must not share identity"


def test_journal_entry_identity_is_independent_of_title_comparison():
    e = JournalEntry(title="2026-07-29")
    assert e.id
    assert e.title == "2026-07-29"
