from __future__ import annotations

from typing import Callable, TypeVar

from ohtli.domain.project import Project

T = TypeVar("T")


def is_applicable(title: str, existing_titles: set[str], *, target_occupied: bool) -> bool:
    """Capture is applicable only if no object of this type with this
    title exists yet AND the file this title would be written to is free.

    A note is named by the slug of its title, so a new title can still land
    on a file that is already there: a hand-made note, or another title with
    the same slug ("Foo Bar" and "foo-bar"). The title check alone cannot see
    that, so `target_occupied` is required: no caller can forget it. Whether
    the path is occupied is a fact about the vault, gathered by Execution;
    this stays a pure predicate.

    Applicability is evaluated independently from, and prior to,
    Execution. This check carries no Project-specific knowledge, so it
    already applies unchanged to any Domain Object Capture is asked to
    preserve.
    """
    return title not in existing_titles and not target_occupied


def transform(title: str, domain_factory: Callable[..., T] = Project) -> T:
    """The Capture transformation: preserve a new Domain Object.

    This function does not check applicability and does not persist
    anything. It is a pure transformation, called only after
    applicability has already been confirmed by the caller.

    `domain_factory` defaults to `Project` (Phase 10 behavior,
    unchanged). Passing a different Domain Object's constructor (e.g.
    `Area`) generalizes Capture without duplicating this function per
    type — Capture is a class of transformation, not a per-object
    function, per the Workflow Model.
    """
    return domain_factory(title=title)
