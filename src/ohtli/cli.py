from __future__ import annotations

import argparse
import sys

from ohtli.execution.execution import (
    Actor,
    ExecutionRequest,
    ProcessingRequest,
    execute_capture,
    execute_processing,
)
from ohtli.vault_io.markdown import list_inbox_entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ohtli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-project", help="Capture a new Project")
    create.add_argument("title")

    subparsers.add_parser("process-inbox", help="Process all raw Inbox entries")

    args = parser.parse_args(argv)

    if args.command == "create-project":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request)
        if not result.applicable:
            print(f"Not applicable: a Project titled '{args.title}' already exists.")
            return 1
        print(f"Captured Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    if args.command == "process-inbox":
        entries = list_inbox_entries()
        if not entries:
            print("Inbox is empty.")
            return 0

        for entry_path in entries:
            request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
            result = execute_processing(request)
            if not result.applicable:
                print(f"Not applicable: '{entry_path.name}' left untouched in Inbox.")
                continue
            print(f"Processed Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
