from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ohtli.event.event import Event
from ohtli.vault_io import paths


def append_event(event: Event, *, events_dir: Path | None = None) -> Path:
    """Append one Event as a single JSON line.

    Append-only: no existing line is ever read, modified, or removed.
    """
    path = paths.events_file_path(events_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event)) + "\n")
    return path


def read_events(*, events_dir: Path | None = None) -> list[Event]:
    """All Events, in file (chronological) order.

    No filters, no projections, no replay — Current State is never
    reconstructed from this; it exists purely as historical evidence.
    """
    path = paths.events_file_path(events_dir)
    if not path.exists():
        return []

    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(Event(**json.loads(line)))
    return events
