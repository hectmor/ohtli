from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

VAULT_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault"

PROJECTS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "projects"
AREAS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "areas"
RESOURCES_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "resources"
REFERENCES_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "references"
MEETINGS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "meetings"
# Deliberately `journal/entries`, never `journal/daily`: the latter is owned by
# the user's Obsidian Daily Notes plugin (`.obsidian/daily-notes.json`).
JOURNAL_ENTRIES_DIR = (
    _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "journal" / "entries"
)
INBOX_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "inbox"
EVENTS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / ".ohtli"
# Generated (derived) dashboards live in a folder of their own that nothing else
# reads or writes, so they can never collide with a Domain Object note or be
# overwritten by a Capture, and no path-based lookup can mistake one for an Area.
AREA_DASHBOARDS_DIR = VAULT_DIR / "dashboards" / "areas"


def slugify(title: str) -> str:
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
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

    Built from the Area's own slug plus a fixed suffix (not by slugifying
    "<title> Dashboard"), so the file name always shares the Area note's stem,
    even for a title that slugifies to nothing (`untitled`).
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
