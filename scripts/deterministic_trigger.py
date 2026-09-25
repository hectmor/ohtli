"""Example Deterministic-actor trigger.

Demonstrates that the exact same `execute_capture` function used by the
Human-facing CLI (ohtli/cli.py) also serves a Deterministic actor, with
no actor-specific branching anywhere in domain, workflow, or execution
code. Ohtli has no trigger source of its own: something outside it (a cron
job, a file-watcher, a person) invokes this script, and that is the Trigger.
The CLI can do the same for any command: `ohtli --actor deterministic <command>`.

Usage:
    python scripts/deterministic_trigger.py --vault DIR [TITLE]

`--vault` is required, so running the script can never write to a vault by
accident. To use the repository's own vault, pass it explicitly.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ohtli.cli import refusal_message
from ohtli.execution.execution import Actor, ExecutionRequest, execute_capture
from ohtli.vault_io import paths

DEFAULT_TITLE = "Deterministically Captured Project"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deterministic_trigger.py",
        description="Capture a Project as a Deterministic actor into an explicitly chosen vault.",
    )
    parser.add_argument("title", nargs="?", default=DEFAULT_TITLE, help="Title of the Project to capture")
    parser.add_argument(
        "--vault",
        required=True,
        type=Path,
        metavar="DIR",
        help="Vault root directory to write into (required; nothing is written without it)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.vault.is_dir():
        parser.error(f"--vault {args.vault} is not an existing directory")

    request = ExecutionRequest(title=args.title, actor=Actor.DETERMINISTIC)
    result = execute_capture(
        request,
        base_dir=args.vault / paths.PROJECTS_DIR.name,
        events_dir=args.vault / paths.EVENTS_DIR.name,
    )
    if not result.applicable:
        print(refusal_message(result, args.title, "Project"))
        return 1
    print(f"Captured Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
