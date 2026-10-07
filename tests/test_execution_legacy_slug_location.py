"""`slugify`'s fix (#157) changes only the file name chosen for a NEW note.
Notes already on disk under their old, lossy slug must keep working exactly
as before, because every lookup of an existing note locates it by its
stored title (`find_notes_titled`), never by recomputing a slug (#156,
#160-#163).

The fixtures below mirror two real files in the vault this issue was
opened about: `references/art-culo-sobre-cach-distribuido.md` (title
"Artículo sobre caché distribuido") and `meetings/standup-r-pido.md`
(title "Standup rápido") -- written here under `tmp_path`, never touching
the real vault.
"""

from ohtli.execution.execution import (
    Actor,
    ArchiveRequest,
    ProcessingRequest,
    execute_archive,
    execute_capture,
    ExecutionRequest,
    execute_processing,
)
from ohtli.execution.specs import MEETING, REFERENCE
from ohtli.vault_io.markdown import read_note


def _write_legacy(spec, slug, title, tmp_path):
    """A real, valid Ohtli note of `spec`'s type, written under its OLD,
    lossy slug -- exactly as the pre-#157 `slugify` would have named it."""
    directory = tmp_path / spec.note_type
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{slug}.md"
    path.write_text(
        f"---\nid: 11111111-1111-1111-1111-111111111111\nnote_type: {spec.note_type}\n"
        "created: '2026-09-15'\nupdated: '2026-09-15'\ntags: []\naliases: []\n"
        f"status: captured\ncontext: operational\n---\n\n# {title}\n\nsome body text\n",
        encoding="utf-8",
    )
    return path


def test_recapturing_a_legacy_slug_title_is_title_exists_not_a_second_file(tmp_path):
    """The exact real-world risk this issue's design flagged: a title that
    now slugifies differently must never create a second file alongside
    the legacy one -- `title_exists` is checked by title, not by slug."""
    legacy = _write_legacy(MEETING, "standup-r-pido", "Standup rápido", tmp_path)

    result = execute_capture(
        ExecutionRequest(title="Standup rápido", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path / MEETING.note_type,
        events_dir=tmp_path / "events",
    )

    assert result.applicable is False and result.reason == "title_exists"
    assert not (tmp_path / MEETING.note_type / "standup-rapido.md").exists()
    assert legacy.exists()


def test_archive_finds_a_legacy_slug_note_by_title_and_rewrites_it_in_place(tmp_path):
    legacy = _write_legacy(MEETING, "standup-r-pido", "Standup rápido", tmp_path)

    result = execute_archive(
        ArchiveRequest(title="Standup rápido", actor=Actor.HUMAN),
        spec=MEETING,
        base_dir=tmp_path / MEETING.note_type,
        events_dir=tmp_path / "events",
    )

    assert result.applicable is True
    assert result.path == legacy
    assert read_note(legacy)["properties"]["context"] == "historical"


def test_processing_update_rewrites_a_legacy_slug_note_in_place(tmp_path):
    legacy = _write_legacy(
        REFERENCE, "art-culo-sobre-cach-distribuido", "Artículo sobre caché distribuido", tmp_path
    )
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    entry = inbox / "entry.md"
    entry.write_text("Artículo sobre caché distribuido\n\nuna nota nueva\n", encoding="utf-8")

    result = execute_processing(
        ProcessingRequest(entry_path=entry, actor=Actor.HUMAN),
        spec=REFERENCE,
        base_dir=tmp_path / REFERENCE.note_type,
        events_dir=tmp_path / "events",
    )

    assert result.applicable is True and result.operation == "update"
    assert result.path == legacy
    assert not entry.exists()
    assert "una nota nueva" in read_note(legacy)["body"]
