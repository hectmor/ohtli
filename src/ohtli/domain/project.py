from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Project:
    """The Project Domain Object.

    Identity is independent of representation, physical location, or
    storage format. This class carries no filesystem, YAML, or
    Obsidian-specific knowledge.
    """

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
