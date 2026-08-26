from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from ohtli.vault_io import paths as paths

_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def write_project(representation: dict[str, Any], *, base_dir: Path | None = None) -> Path:
    path = paths.project_file_path(representation["title"], base_dir=base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = yaml.safe_dump(representation["properties"], sort_keys=False)
    content = f"---\n{frontmatter}---\n\n{representation['body']}"
    path.write_text(content, encoding="utf-8")
    return path


def read_project(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    _, frontmatter_text, body = text.split("---", 2)
    properties = yaml.safe_load(frontmatter_text)
    title_match = _TITLE_RE.search(body)
    title = title_match.group(1).strip() if title_match else path.stem
    return {"properties": properties, "title": title, "body": body.lstrip("\n")}


def list_existing_titles(*, base_dir: Path | None = None) -> set[str]:
    """The Current State this slice needs: which Project titles already exist.

    Read directly from the vault on every call. No event log, no cache.

    The vault's `projects/` directory already contains non-Project
    navigation notes (`README.md`, `index.md`) that predate this slice
    and carry no YAML frontmatter. A file without frontmatter is not a
    Project representation and is skipped rather than treated as an
    error.
    """
    directory = base_dir if base_dir is not None else paths.PROJECTS_DIR
    if not directory.exists():
        return set()

    titles = set()
    for md_file in directory.glob("*.md"):
        if not md_file.read_text(encoding="utf-8").startswith("---\n"):
            continue
        titles.add(read_project(md_file)["title"])
    return titles
