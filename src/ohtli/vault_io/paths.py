from __future__ import annotations

import contextlib
import re
import unicodedata
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

VAULT_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault"

# Every writable location's path relative to the vault root: the single
# source of truth for the vault's folder layout. `vault_root` below uses it
# to point a DIFFERENT vault (`ohtli --vault DIR`) at this exact shape, and
# nothing may derive a subfolder name any other way — taking only a
# constant's `.name` would drop `JOURNAL_ENTRIES_DIR`'s `journal/`, and would
# collide `AREA_DASHBOARDS_DIR`'s name with `AREAS_DIR`'s.
_LAYOUT: dict[str, str] = {
    "PROJECTS_DIR": "projects",
    "AREAS_DIR": "areas",
    "RESOURCES_DIR": "resources",
    "REFERENCES_DIR": "references",
    "MEETINGS_DIR": "meetings",
    # Deliberately `journal/entries`, never `journal/daily`: the latter is owned by
    # the user's Obsidian Daily Notes plugin (`.obsidian/daily-notes.json`).
    "JOURNAL_ENTRIES_DIR": "journal/entries",
    "INBOX_DIR": "inbox",
    "EVENTS_DIR": ".ohtli",
    # Generated (derived) dashboards live in a folder of their own that nothing else
    # reads or writes, so they can never collide with a Domain Object note or be
    # overwritten by a Capture, and no path-based lookup can mistake one for an Area.
    "AREA_DASHBOARDS_DIR": "dashboards/areas",
}

PROJECTS_DIR = VAULT_DIR / _LAYOUT["PROJECTS_DIR"]
AREAS_DIR = VAULT_DIR / _LAYOUT["AREAS_DIR"]
RESOURCES_DIR = VAULT_DIR / _LAYOUT["RESOURCES_DIR"]
REFERENCES_DIR = VAULT_DIR / _LAYOUT["REFERENCES_DIR"]
MEETINGS_DIR = VAULT_DIR / _LAYOUT["MEETINGS_DIR"]
JOURNAL_ENTRIES_DIR = VAULT_DIR / _LAYOUT["JOURNAL_ENTRIES_DIR"]
INBOX_DIR = VAULT_DIR / _LAYOUT["INBOX_DIR"]
EVENTS_DIR = VAULT_DIR / _LAYOUT["EVENTS_DIR"]
AREA_DASHBOARDS_DIR = VAULT_DIR / _LAYOUT["AREA_DASHBOARDS_DIR"]


@contextlib.contextmanager
def vault_root(root: Path):
    """Point the whole vault layout at `root` for the duration of the `with`
    block, then put every constant back — even if the block raises.

    `ohtli --vault DIR` uses this: every `execute_*`/`read_*` call that omits
    `base_dir`/`events_dir` (most of them, throughout `cli.py`) falls back to
    these module constants at call time, so patching them here redirects the
    whole CLI without threading an override through every call site — the
    same reason `tests/conftest.py`'s autouse fixture patches `EVENTS_DIR`
    and `AREA_DASHBOARDS_DIR` for tests, generalized to every constant and to
    production use. Restoring afterwards matters because `main()` can run
    many times in one process and must never leak one `--vault` into the next
    call.
    """
    before = {"VAULT_DIR": VAULT_DIR}
    before.update((name, globals()[name]) for name in _LAYOUT)
    try:
        globals()["VAULT_DIR"] = root
        for name, sub in _LAYOUT.items():
            globals()[name] = root / sub
        yield
    finally:
        globals().update(before)


def slugify(title: str) -> str:
    """A note's file name stem: ASCII lowercase letters, digits and single
    hyphens (#157).

    Accented Latin letters lose their accents ("Café" -> "cafe"). NFKD
    splits each one into a base letter plus combining marks (category
    "Mn"), which are then dropped; NFKD also folds compatibility forms
    (ligatures, full-width letters, math-styled letters, superscripts).
    Casefold runs AFTER normalization, not before: some characters have no
    lowercase mapping of their own and only become ordinary letters once
    normalized (a math-bold capital, for instance) -- casefolding first
    would lose them instead of folding them to ASCII.

    A title with no Latin letters or digits left after this (Cyrillic,
    Greek, CJK, Arabic, emoji, symbols only) still falls back to
    "untitled", unchanged from before: one such note per folder, the next
    refused as `same_file_name`, never silently overwritten.

    Every pure-ASCII title slugifies identically to before: NFKD leaves
    ASCII untouched, ASCII has no combining marks, and `casefold()` equals
    `lower()` on ASCII. Changing this function changes only the file name
    chosen for a NEW note -- an existing note is always located by its
    stored title (`find_notes_titled`), never by recomputing its slug
    (#156, #160-#163).
    """
    decomposed = unicodedata.normalize("NFKD", title.strip())
    unaccented = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    slug = re.sub(r"[^a-z0-9]+", "-", unaccented.casefold()).strip("-")
    return slug or "untitled"


def _note_file_path(title: str, default_dir: Path, base_dir: Path | None) -> Path:
    base = base_dir if base_dir is not None else default_dir
    return base / f"{slugify(title)}.md"


def project_file_path(title: str, base_dir: Path | None = None) -> Path:
    return _note_file_path(title, PROJECTS_DIR, base_dir)


def area_file_path(title: str, base_dir: Path | None = None) -> Path:
    return _note_file_path(title, AREAS_DIR, base_dir)


def area_dashboard_file_path(area_title: str, base_dir: Path | None = None) -> Path:
    """Where an Area's generated dashboard lives: `<area-slug>-dashboard.md`.

    Built from `area_title`'s own slug plus a fixed suffix (not by
    slugifying "<title> Dashboard"), so a title that slugifies to nothing
    still gets `untitled-dashboard.md`, not a bare suffix.

    This is NOT guaranteed to share the Area note's actual file stem: the
    Area may have been renamed since it was captured, or (before #157)
    captured under a title whose slug has since changed shape. The
    dashboard is regenerated from `area_title` as given, and is a derived,
    disposable artifact (`write_generated_file`'s marker check), not a
    second identity for the Area.
    """
    base = base_dir if base_dir is not None else AREA_DASHBOARDS_DIR
    return base / f"{slugify(area_title)}-dashboard.md"


def resource_file_path(title: str, base_dir: Path | None = None) -> Path:
    return _note_file_path(title, RESOURCES_DIR, base_dir)


def reference_file_path(title: str, base_dir: Path | None = None) -> Path:
    return _note_file_path(title, REFERENCES_DIR, base_dir)


def meeting_file_path(title: str, base_dir: Path | None = None) -> Path:
    return _note_file_path(title, MEETINGS_DIR, base_dir)


def journal_entry_file_path(title: str, base_dir: Path | None = None) -> Path:
    return _note_file_path(title, JOURNAL_ENTRIES_DIR, base_dir)


def events_file_path(base_dir: Path | None = None) -> Path:
    """A single append-only log, not one file per object — unlike
    `project_file_path`/`area_file_path`, this does not depend on a
    title.
    """
    base = base_dir if base_dir is not None else EVENTS_DIR
    return base / "events.jsonl"
