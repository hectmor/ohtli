from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from ohtli.vault_io import paths as paths

_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

_RESERVED_INBOX_FILENAMES = {"README.md", "index.md"}


def _render_note(representation: dict[str, Any]) -> str:
    frontmatter = yaml.safe_dump(representation["properties"], sort_keys=False)
    return f"---\n{frontmatter}---\n\n{representation['body']}"


def _write_note(
    representation: dict[str, Any], path_fn: Any, *, base_dir: Path | None = None
) -> Path:
    path = path_fn(representation["title"], base_dir=base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_note(representation), encoding="utf-8")
    return path


def write_project(representation: dict[str, Any], *, base_dir: Path | None = None) -> Path:
    return _write_note(representation, paths.project_file_path, base_dir=base_dir)


def write_area(representation: dict[str, Any], *, base_dir: Path | None = None) -> Path:
    return _write_note(representation, paths.area_file_path, base_dir=base_dir)


def rewrite_note(path: Path, representation: dict[str, Any]) -> Path:
    """Rewrite a note's Current Representation at its existing path.

    Unlike `write_project`/`write_area` (Capture/Processing, which
    only ever create), Archive/Reactivate update a file that already
    exists — the path must not be recomputed from the (unchanged)
    title.
    """
    path.write_text(_render_note(representation), encoding="utf-8")
    return path


def read_note(path: Path) -> dict[str, Any]:
    """Parse a note's Current Representation from disk.

    Frontmatter/title/body structure is identical across every Domain
    Object's representation, so this parsing is a single, type-agnostic
    function rather than one per type.
    """
    text = path.read_text(encoding="utf-8")
    _, frontmatter_text, body = text.split("---", 2)
    properties = yaml.safe_load(frontmatter_text)
    title_match = _TITLE_RE.search(body)
    title = title_match.group(1).strip() if title_match else path.stem
    return {"properties": properties, "title": title, "body": body.lstrip("\n")}


read_project = read_note
read_area = read_note


def _list_existing_titles(directory: Path) -> set[str]:
    """The Current State this slice needs: which titles already exist in
    a given directory.

    Read directly from the vault on every call. No event log, no cache.

    Some vault directories already contain non-Domain-Object navigation
    notes (`README.md`, `index.md`) that carry no YAML frontmatter. A
    file without frontmatter is not a Domain Object representation and
    is skipped rather than treated as an error.
    """
    if not directory.exists():
        return set()

    titles = set()
    for md_file in directory.glob("*.md"):
        if not md_file.read_text(encoding="utf-8").startswith("---\n"):
            continue
        titles.add(read_note(md_file)["title"])
    return titles


def list_existing_titles(*, base_dir: Path | None = None) -> set[str]:
    directory = base_dir if base_dir is not None else paths.PROJECTS_DIR
    return _list_existing_titles(directory)


def list_existing_area_titles(*, base_dir: Path | None = None) -> set[str]:
    directory = base_dir if base_dir is not None else paths.AREAS_DIR
    return _list_existing_titles(directory)


def list_inbox_entries(*, base_dir: Path | None = None) -> list[Path]:
    """The raw, unprocessed Inbox entries.

    Inbox entries carry no frontmatter by design (`Inbox Entry != Domain
    Object`), so unlike `list_existing_titles` they cannot be told apart
    from navigation notes by content. Reserved navigation filenames are
    excluded by name instead.
    """
    directory = base_dir if base_dir is not None else paths.INBOX_DIR
    if not directory.exists():
        return []

    return sorted(
        md_file
        for md_file in directory.glob("*.md")
        if md_file.name not in _RESERVED_INBOX_FILENAMES
    )


def read_inbox_entry(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def resolve_inbox_entry(path: Path) -> None:
    """Resolve a processed Inbox entry by removing it.

    Removing the file is an implementation detail of the Filesystem
    Model, not a Domain decision (`Directory structure != Domain
    semantics`) — the entry never had identity to begin with.
    """
    path.unlink()
