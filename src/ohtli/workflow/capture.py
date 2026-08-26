from __future__ import annotations

from ohtli.domain.project import Project


def is_applicable(title: str, existing_titles: set[str]) -> bool:
    """Capture is applicable only if no Project with this title exists yet.

    Applicability is evaluated independently from, and prior to,
    Execution.
    """
    return title not in existing_titles


def transform(title: str) -> Project:
    """The Capture transformation: preserve a new Project.

    This function does not check applicability and does not persist
    anything. It is a pure transformation, called only after
    applicability has already been confirmed by the caller.
    """
    return Project(title=title)
