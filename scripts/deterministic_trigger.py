"""Example Deterministic-actor trigger.

Demonstrates that the exact same `execute_capture` function used by the
Human-facing CLI (ohtli/cli.py) also serves a Deterministic actor, with
no actor-specific branching anywhere in domain, workflow, or execution
code. This script could just as easily be invoked by a cron job or a
file-watcher instead of a human typing a command.
"""

from __future__ import annotations

import sys

from ohtli.execution.execution import Actor, ExecutionRequest, execute_capture


def main(title: str) -> int:
    request = ExecutionRequest(title=title, actor=Actor.DETERMINISTIC)
    result = execute_capture(request)
    if not result.applicable:
        print(f"Not applicable: a Project titled '{title}' already exists.")
        return 1
    print(f"Captured Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "Deterministically Captured Project"))
