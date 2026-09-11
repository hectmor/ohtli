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
