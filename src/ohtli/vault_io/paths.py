from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

PROJECTS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "projects"
AREAS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "areas"
INBOX_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "inbox"
EVENTS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / ".ohtli"


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


def events_file_path(base_dir: Path | None = None) -> Path:
    """A single append-only log, not one file per object — unlike
    `project_file_path`/`area_file_path`, this does not depend on a
    title.
    """
    base = base_dir if base_dir is not None else EVENTS_DIR
    return base / "events.jsonl"
