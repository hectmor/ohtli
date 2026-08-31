from __future__ import annotations

from ohtli.domain.project import Project


def _split_entry(raw_text: str) -> tuple[str | None, str | None]:
    """Split a raw Inbox entry into the title it would become and the
    body content that follows it.

    The title is the first non-empty line, with any leading markdown
    heading marks and surrounding whitespace stripped. The notes are
    everything after that line. Either is None when absent. Both are
    derived in a single pass so they can never disagree about where the
    title ends and the body begins.
    """
    lines = raw_text.splitlines()
    for index, line in enumerate(lines):
        title = line.strip().lstrip("#").strip()
        if title:
            notes = "\n".join(lines[index + 1 :]).strip()
            return title, notes or None
    return None, None


def _derive_title(raw_text: str) -> str | None:
    return _split_entry(raw_text)[0]


def derive_notes(raw_text: str) -> str | None:
    """The body content of a raw Inbox entry, if any.

    Exposed so Execution can carry the entry's original content into the
    Project's Representation. Kept out of `transform()` so that function
    stays a pure Domain transformation, structurally parallel to
    `capture.transform()`.
    """
    return _split_entry(raw_text)[1]


def is_applicable(raw_text: str, existing_titles: set[str]) -> bool:
    """Processing is applicable only if a non-empty title can be derived
    from the entry, and no Project with that title already exists.

    Applicability is evaluated independently from, and prior to,
    Execution.
    """
    title = _derive_title(raw_text)
    return title is not None and title not in existing_titles


def transform(raw_text: str) -> Project:
    """The Processing transformation: interpret an existing Inbox entry
    as a new Project.

    This function does not check applicability and does not persist
    anything, or touch the Inbox entry itself. It is a pure
    transformation, called only after applicability has already been
    confirmed by the caller.
    """
    return Project(title=_derive_title(raw_text))
