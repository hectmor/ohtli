from __future__ import annotations

from ohtli.representation.context import HISTORICAL, OPERATIONAL


# The Interaction Model relationship types whose SOURCE end is "required
# operationally by" its target (`archive-workflow.md`, "Operational Integrity").
# `supports` is the one canonical type whose direction matches the spec's own
# example: the required thing is the source, the requirer is the target.
# `belongs to`/`contains`/`references` are deliberately excluded — see the
# Phase 35 issue for the evidence (an existing, pinned test already asserts an
# Area can be archived while an operational Project still `belongs to` it).
OPERATIONALLY_REQUIRING_TYPES = frozenset({"supports"})


def is_applicable(current_context: str, *, has_operational_dependents: bool = False) -> bool:
    """Archive is applicable only if the target currently participates
    in operational context (`archive-workflow.md` Applicability) and its
    operational presence is not still required (`Operational Integrity`).

    `has_operational_dependents` is a fact the caller computes (Archive's
    own layering: this stays a pure predicate, the I/O that discovers
    dependents lives in `execution.py`, mirroring `is_relate_applicable`'s
    `already_linked` and `evaluation.is_applicable`'s allowed-results set).
    Defaulted so every pre-existing call — including Reactivate, which
    shares `_execute_contextual_transition` — is unaffected.

    Unlike Capture/Processing, Archive does not construct a new Domain
    Object — there is no `transform()` here. Archive only changes
    contextual presence, performed by `representation.context.archive`.
    """
    return current_context == OPERATIONAL and not has_operational_dependents


def is_reactivate_applicable(current_context: str) -> bool:
    """Reactivate is applicable only if the target currently
    participates in historical context.
    """
    return current_context == HISTORICAL
