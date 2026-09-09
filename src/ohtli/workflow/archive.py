from __future__ import annotations

from ohtli.representation.context import HISTORICAL, OPERATIONAL


def is_applicable(current_context: str) -> bool:
    """Archive is applicable only if the target currently participates
    in operational context (`archive-workflow.md` Applicability).

    Unlike Capture/Processing, Archive does not construct a new Domain
    Object — there is no `transform()` here. Archive only changes
    contextual presence, performed by `representation.context.archive`.
    """
    return current_context == OPERATIONAL


def is_reactivate_applicable(current_context: str) -> bool:
    """Reactivate is applicable only if the target currently
    participates in historical context.
    """
    return current_context == HISTORICAL
