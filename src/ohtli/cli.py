from __future__ import annotations

import argparse
import sys

from ohtli.execution.execution import Actor, ExecutionRequest, execute_capture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ohtli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-project", help="Capture a new Project")
    create.add_argument("title")

    args = parser.parse_args(argv)

    if args.command == "create-project":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request)
        if not result.applicable:
            print(f"Not applicable: a Project titled '{args.title}' already exists.")
            return 1
        print(f"Captured Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
