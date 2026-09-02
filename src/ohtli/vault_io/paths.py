from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]

PROJECTS_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "projects"
INBOX_DIR = _REPO_ROOT / "implementations" / "platforms" / "obsidian" / "vault" / "inbox"


def slugify(title: str) -> str:
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug or "untitled"


def project_file_path(title: str, base_dir: Path | None = None) -> Path:
    base = base_dir if base_dir is not None else PROJECTS_DIR
    return base / f"{slugify(title)}.md"
