"""Example Deterministic-actor trigger for Processing.

Demonstrates that the exact same `execute_processing` function used by
the Human-facing CLI (`ohtli process-inbox`) also serves a Deterministic
actor, with no actor-specific branching anywhere in domain, workflow, or
execution code. This script could just as easily be invoked by a cron
job or a file-watcher instead of a human typing a command.
"""

from __future__ import annotations

import sys

from ohtli.execution.execution import Actor, ProcessingRequest, execute_processing
from ohtli.vault_io.markdown import list_inbox_entries


def main() -> int:
    entries = list_inbox_entries()
    if not entries:
        print("Inbox is empty.")
        return 0

    for entry_path in entries:
        request = ProcessingRequest(entry_path=entry_path, actor=Actor.DETERMINISTIC)
        result = execute_processing(request)
        if not result.applicable:
            print(f"Not applicable: '{entry_path.name}' left untouched in Inbox.")
            continue
        print(f"Processed Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
