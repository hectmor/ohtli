from __future__ import annotations

from pathlib import Path


def write_generated_file(path: Path, text: str, *, marker: str) -> str:
    """Write a generated (derived) file, overwriting only what this function
    itself could have written.

    A generated file is a copy of state that lives elsewhere (a dashboard),
    so it is never a source of truth and is regenerated whole, never merged.
    What it must never do is destroy something a person wrote, so the rule is
    strict: an existing file is overwritten **only if its first line is exactly
    `marker`**. Anything else is left untouched.

    Returns one of:
    - `"created"`: nothing was at `path`; the file (and parent folders) exist now.
    - `"updated"`: a previously generated file was rewritten with new content.
    - `"unchanged"`: a previously generated file already had exactly this
      content, so nothing was written (not even its modification time).
    - `"refused"`: `path` holds something that is not a file this function
      generated (no marker, a directory, not UTF-8, or a symbolic link).
      Nothing was written.

    `text` must itself start with `marker` plus a newline: a file written
    without the marker could never be recognised, and so never regenerated.
    The check is on the whole first line, so a line that merely begins with
    the marker is refused: it is safer to refuse a legitimate file than to
    overwrite an unrelated one.

    Line endings are normalised when the existing file is read (Python's
    universal newlines), so a generated file whose line endings an editor or
    git converted to `\\r\\n` is still recognised as generated. That is
    deliberate: refusing it would strand a legitimate dashboard, and the
    protection for hand-written files is the exact marker line, not the
    line-ending style. For the same reason `"unchanged"` means equal
    content modulo line endings; such a file is left as it is.

    A symbolic link is refused outright: writing through one could reach a
    file outside the vault.

    Operating-system errors while writing (permissions, a full disk) are not
    caught: they propagate, as they do for `vault_io.markdown._write_note`.
    """
    first_line = marker + "\n"
    if not text.startswith(first_line):
        raise ValueError("text must start with the marker line so the file can be recognised and regenerated")

    if path.is_symlink():
        return "refused"

    if path.exists():
        if not path.is_file():
            return "refused"
        try:
            existing = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return "refused"
        if not existing.startswith(first_line):
            return "refused"
        if existing == text:
            return "unchanged"
        path.write_text(text, encoding="utf-8")
        return "updated"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return "created"
