from ohtli.vault_io import paths


def test_default_directory_is_journal_entries_never_the_daily_notes_folder():
    """journal/daily belongs to the user's Obsidian Daily Notes plugin
    (.obsidian/daily-notes.json); Journal Entry must never write there."""
    directory = paths.JOURNAL_ENTRIES_DIR

    assert directory.name == "entries"
    assert directory.parent.name == "journal"
    assert directory != directory.parent / "daily"


def test_a_date_title_becomes_a_date_named_file():
    assert paths.journal_entry_file_path("2026-07-29").name == "2026-07-29.md"


def test_a_date_time_title_slugifies_to_a_date_time_file_name():
    assert paths.journal_entry_file_path("2026-07-29 14:30").name == "2026-07-29-14-30.md"
