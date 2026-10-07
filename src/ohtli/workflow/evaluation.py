from __future__ import annotations

from enum import Enum

from ohtli.representation.context import OPERATIONAL


class OperationalResult(Enum):
    """The Actual Operational Result of the Evaluate operation
    (`execution-workflow.md`). Not a Domain Object, not a stored
    status value — recorded only as an Event.
    """

    PROGRESS = "progress"
    MAINTENANCE = "maintenance"
    OUTCOME_REACHED = "outcome_reached"
    NO_EFFECTIVE_CHANGE = "no_effective_change"
    DEGRADATION = "degradation"


def is_applicable(
    current_context: str, result: OperationalResult, allowed_results: frozenset[OperationalResult]
) -> bool:
    """Evaluate is applicable only if the target currently participates
    in operational context, and the result is one this Domain Object
    can produce.

    Named `evaluation.py`, not `execution.py`: the canonical spec's
    "Execution workflow" would collide with the codebase's existing
    `execution/execution.py` module. Evaluate is the only one of
    Execution's three operations (Select, Act, Evaluate) Ohtli can
    represent — Act is real-world work, performed outside this code.
    """
    return current_context == OPERATIONAL and result in allowed_results


def is_target_located(*, matches: int) -> bool:
    """The note to evaluate is located only when exactly one note of its
    type carries the title.

    Evaluate's Event is permanent (#163): misattributing it to a decoy
    sitting at a renamed note's old slug would be a lasting wrong write,
    not merely a stale read. Zero matches means the title exists only in
    name; more than one is ambiguous. Not imported from `archive.py`/
    `knowledge.py`/`processing.py` — workflows never call each other.

    Pure: `matches` (how many Ohtli notes of this type carry the title) is
    gathered by Execution.
    """
    return matches == 1
