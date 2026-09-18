from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class JournalEntry:
    """The Journal Entry Domain Object.

    Captures thoughts associated with a specific moment in time. The
    Domain Model lists Date and Content as Essential Attributes and no
    Title: `title` here is an implementation handle (the stack is
    title-keyed), conventionally the entry's moment, e.g. `2026-07-29`.
    Identity is independent of representation, physical location, or
    storage format. This class carries no filesystem, YAML, or
    Obsidian-specific knowledge.
    """

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
