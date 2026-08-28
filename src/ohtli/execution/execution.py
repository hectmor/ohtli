from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ohtli.domain.project import Project
from ohtli.representation.project import to_representation
from ohtli.vault_io.markdown import list_existing_titles, write_project
from ohtli.workflow import capture


class Actor(Enum):
    """The four structurally equivalent Actor kinds (ADR-0004).

    No function in this module branches on which Actor kind is
    passed. Actor participates only as context attached to the
    Execution Request.
    """

    HUMAN = "human"
    DETERMINISTIC = "deterministic"
    AI_ASSISTED = "ai_assisted"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class ExecutionRequest:
    title: str
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class ExecutionResult:
    request: ExecutionRequest
    applicable: bool
    project: Project | None
    path: Path | None


def execute_capture(request: ExecutionRequest, *, base_dir: Path | None = None) -> ExecutionResult:
    """Execute the Capture workflow for a single Project title.

    Request != Execution: this function represents the occurrence.
    Applicability is checked before any transformation or persistence
    happens, and is fully independent of `request.actor`.

    `base_dir` defaults to the real vault; tests pass a temporary
    directory so they never touch the user's actual vault content.
    """
    existing_titles = list_existing_titles(base_dir=base_dir)

    if not capture.is_applicable(request.title, existing_titles):
        return ExecutionResult(request=request, applicable=False, project=None, path=None)

    project = capture.transform(request.title)
    representation = to_representation(project)
    path = write_project(representation, base_dir=base_dir)

    return ExecutionResult(request=request, applicable=True, project=project, path=path)
