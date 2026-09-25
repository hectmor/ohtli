"""Example Deterministic-actor trigger for Processing.

Demonstrates that the exact same `execute_processing` function used by
the Human-facing CLI (`ohtli process-inbox`) also serves a Deterministic
actor, with no actor-specific branching anywhere in domain, workflow, or
execution code. Ohtli has no trigger source of its own: something outside
it (a cron job, a file-watcher, a person) invokes this script, and that is
the Trigger. The CLI can do the same for any command:
`ohtli --actor deterministic <command>`.

Usage:
    python scripts/deterministic_inbox_trigger.py --vault DIR

`--vault` is required, so running the script can never read or delete a
vault's Inbox by accident. To use the repository's own vault, pass it
explicitly. Each processed Inbox entry is removed from that vault's Inbox.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ohtli.execution.execution import Actor, ProcessingRequest, execute_processing
from ohtli.vault_io import paths
from ohtli.vault_io.markdown import list_inbox_entries


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deterministic_inbox_trigger.py",
        description="Process every raw Inbox entry as a Deterministic actor in an explicitly chosen vault.",
    )
    parser.add_argument(
        "--vault",
        required=True,
        type=Path,
        metavar="DIR",
        help="Vault root directory to read the Inbox from and write into (required; nothing is touched without it)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.vault.is_dir():
        parser.error(f"--vault {args.vault} is not an existing directory")

    entries = list_inbox_entries(base_dir=args.vault / paths.INBOX_DIR.name)
    if not entries:
        print("Inbox is empty.")
        return 0

    for entry_path in entries:
        request = ProcessingRequest(entry_path=entry_path, actor=Actor.DETERMINISTIC)
        result = execute_processing(
            request,
            base_dir=args.vault / paths.PROJECTS_DIR.name,
            events_dir=args.vault / paths.EVENTS_DIR.name,
        )
        if not result.applicable:
            print(f"Not applicable: '{entry_path.name}' left untouched in Inbox.")
            continue
        print(f"Processed Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
