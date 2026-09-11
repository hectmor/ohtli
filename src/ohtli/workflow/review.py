from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from ohtli.event.event import Event


class ReviewConclusion(Enum):
    """The conceptual conclusion of a Review Assessment
    (`review-workflow.md`). Not a Domain Object, not a stored status
    value.
    """

    ATTENTION_REQUIRED = "attention_required"
    NO_ATTENTION_REQUIRED = "no_attention_required"
    INSUFFICIENT_BASIS = "insufficient_basis"


@dataclass(frozen=True)
class ReviewAssessment:
    """Preserves the conceptual basis for the evaluation, per the
    spec's "Assessment Basis" invariant. Returned to the caller, never
    persisted — Externalization is a separate, deferred concern.
    """

    conclusion: ReviewConclusion
    basis: tuple[str, ...]
    finding: str | None = None


def observe(events: list[Event], object_id: str, since: str | None = None) -> list[Event]:
    """Inspect Events relevant to a Review's scope: this object's own
    history, optionally bounded by a temporal context.

    Observe does not modify the observed objects — it only filters an
    already-read Event log. `since=None` means the entire relevant
    history.
    """
    relevant = [e for e in events if e.object_id == object_id]
    if since is not None:
        relevant = [e for e in relevant if e.occurred_at >= since]
    return relevant


def assess(properties: dict[str, Any], evaluation_events: list[Event]) -> ReviewAssessment:
    """Evaluate the significance of observed state.

    Three closed rules, checked in order, with no actor branching.
    This is the only `Compare` this slice performs: divergence between
    an Outcome Reached Event and the target's stored `status` — a gap
    that exists only because Evaluate (Phase 15) deliberately never
    writes `status`.
    """
    if not evaluation_events:
        return ReviewAssessment(
            conclusion=ReviewConclusion.INSUFFICIENT_BASIS,
            basis=("no evaluation Events found in scope",),
        )

    has_outcome_reached = any(e.event_type.endswith("Outcome Reached") for e in evaluation_events)
    if has_outcome_reached and properties.get("status") != "completed":
        return ReviewAssessment(
            conclusion=ReviewConclusion.ATTENTION_REQUIRED,
            basis=(
                "an Outcome Reached Event exists",
                f"status is '{properties.get('status')}', not 'completed'",
            ),
            finding="lifecycle reconsideration may be appropriate",
        )

    latest = max(evaluation_events, key=lambda e: e.occurred_at)
    if latest.event_type.endswith("Degradation Observed"):
        return ReviewAssessment(
            conclusion=ReviewConclusion.ATTENTION_REQUIRED,
            basis=(f"most recent evaluation was '{latest.event_type}'",),
        )

    return ReviewAssessment(
        conclusion=ReviewConclusion.NO_ATTENTION_REQUIRED,
        basis=(f"most recent evaluation was '{latest.event_type}'",),
    )
