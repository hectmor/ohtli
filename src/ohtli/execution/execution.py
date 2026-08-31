from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ohtli.domain.project import Project
from ohtli.representation.project import to_representation
from ohtli.vault_io.markdown import (
    list_existing_titles,
    read_inbox_entry,
    resolve_inbox_entry,
    write_project,
)
from ohtli.workflow import capture, processing


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


@dataclass(frozen=True)
class ProcessingRequest:
    entry_path: Path
    actor: Actor
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass(frozen=True)
class ProcessingResult:
    request: ProcessingRequest
    applicable: bool
    project: Project | None
    path: Path | None


def execute_processing(request: ProcessingRequest, *, base_dir: Path | None = None) -> ProcessingResult:
    """Execute the Processing workflow for a single Inbox entry.

    Request != Execution: this function represents the occurrence.
    Applicability is checked before any transformation or persistence
    happens, and is fully independent of `request.actor`.

    `processing.py` is never called from `capture.py` and vice versa
    (workflows do not invoke each other); this function implements its
    own applicability/transform logic against the same Project
    representation and vault_io persistence Capture already uses.

    `base_dir` defaults to the real vault's projects directory; tests
    pass a temporary directory so they never touch the user's actual
    vault content.
    """
    raw_text = read_inbox_entry(request.entry_path)
    existing_titles = list_existing_titles(base_dir=base_dir)

    if not processing.is_applicable(raw_text, existing_titles):
        return ProcessingResult(request=request, applicable=False, project=None, path=None)

    project = processing.transform(raw_text)
    representation = to_representation(project, notes=processing.derive_notes(raw_text))
    path = write_project(representation, base_dir=base_dir)
    resolve_inbox_entry(request.entry_path)

    return ProcessingResult(request=request, applicable=True, project=project, path=path)
