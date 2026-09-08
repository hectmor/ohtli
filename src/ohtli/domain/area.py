from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Area:
    """The Area Domain Object.

    Represents an ongoing responsibility, independent of any single
    Project. Identity is independent of representation, physical
    location, or storage format. This class carries no filesystem,
    YAML, or Obsidian-specific knowledge.
    """

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
