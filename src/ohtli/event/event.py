from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Event:
    """An immutable, historical, object-centered, observable record
    (`docs/architecture/event-model/README.md`).

    Deliberately carries no `title` or other mutable Representation
    field: `Event != Current State` (`representation-invariants.md`).
    Only stable Domain identity (`object_id`, `object_type`) and the
    fact of what happened are recorded.
    """

    event_type: str
    object_id: str
    object_type: str
    actor: str
    execution_id: str
    workflow: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
