from __future__ import annotations

import argparse
import sys

from ohtli.execution.execution import (
    Actor,
    ArchiveRequest,
    EvaluationRequest,
    ExecutionRequest,
    KnowledgeRequest,
    ProcessingRequest,
    ReviewRequest,
    execute_archive,
    execute_capture,
    execute_evaluation,
    execute_knowledge,
    execute_processing,
    execute_reactivate,
    execute_review,
)
from ohtli.execution.specs import AREA, PROJECT, RESOURCE
from ohtli.vault_io.markdown import list_inbox_entries
from ohtli.workflow.evaluation import OperationalResult


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ohtli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-project", help="Capture a new Project")
    create.add_argument("title")

    create_area = subparsers.add_parser("create-area", help="Capture a new Area")
    create_area.add_argument("title")

    create_resource = subparsers.add_parser("create-resource", help="Capture a new Resource")
    create_resource.add_argument("title")

    subparsers.add_parser("process-inbox", help="Process all raw Inbox entries")

    archive_project = subparsers.add_parser("archive-project", help="Archive a Project")
    archive_project.add_argument("title")

    archive_area = subparsers.add_parser("archive-area", help="Archive an Area")
    archive_area.add_argument("title")

    archive_resource = subparsers.add_parser("archive-resource", help="Archive a Resource")
    archive_resource.add_argument("title")

    reactivate_project = subparsers.add_parser("reactivate-project", help="Reactivate a Project")
    reactivate_project.add_argument("title")

    reactivate_area = subparsers.add_parser("reactivate-area", help="Reactivate an Area")
    reactivate_area.add_argument("title")

    reactivate_resource = subparsers.add_parser("reactivate-resource", help="Reactivate a Resource")
    reactivate_resource.add_argument("title")

    evaluate_project = subparsers.add_parser(
        "evaluate-project", help="Record the operational result of work performed on a Project"
    )
    evaluate_project.add_argument("title")
    evaluate_project.add_argument("--result", required=True, choices=[r.value for r in OperationalResult])

    evaluate_area = subparsers.add_parser(
        "evaluate-area", help="Record the operational result of work performed on an Area"
    )
    evaluate_area.add_argument("title")
    evaluate_area.add_argument("--result", required=True, choices=[r.value for r in OperationalResult])

    review_project = subparsers.add_parser("review-project", help="Review a Project")
    review_project.add_argument("title")
    review_project.add_argument("--since", default=None)

    review_area = subparsers.add_parser("review-area", help="Review an Area")
    review_area.add_argument("title")
    review_area.add_argument("--since", default=None)

    review_resource = subparsers.add_parser("review-resource", help="Review a Resource")
    review_resource.add_argument("title")
    review_resource.add_argument("--since", default=None)

    enrich_project = subparsers.add_parser(
        "enrich-project", help="Enrich a Project with Developed Understanding"
    )
    enrich_project.add_argument("title")
    enrich_project.add_argument("--understanding-title", required=True)
    enrich_project.add_argument("--understanding", required=True)
    enrich_project.add_argument("--provenance", required=True, nargs="+")

    enrich_area = subparsers.add_parser(
        "enrich-area", help="Enrich an Area with Developed Understanding"
    )
    enrich_area.add_argument("title")
    enrich_area.add_argument("--understanding-title", required=True)
    enrich_area.add_argument("--understanding", required=True)
    enrich_area.add_argument("--provenance", required=True, nargs="+")

    enrich_resource = subparsers.add_parser(
        "enrich-resource", help="Enrich a Resource with Developed Understanding"
    )
    enrich_resource.add_argument("title")
    enrich_resource.add_argument("--understanding-title", required=True)
    enrich_resource.add_argument("--understanding", required=True)
    enrich_resource.add_argument("--provenance", required=True, nargs="+")

    args = parser.parse_args(argv)

    spec_by_kind = {"project": PROJECT, "area": AREA, "resource": RESOURCE}

    if args.command == "create-project":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request)
        if not result.applicable:
            print(f"Not applicable: a Project titled '{args.title}' already exists.")
            return 1
        print(f"Captured Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    if args.command == "create-area":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request, spec=AREA)
        if not result.applicable:
            print(f"Not applicable: an Area titled '{args.title}' already exists.")
            return 1
        print(f"Captured Area '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    if args.command == "create-resource":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request, spec=RESOURCE)
        if not result.applicable:
            print(f"Not applicable: a Resource titled '{args.title}' already exists.")
            return 1
        print(f"Captured Resource '{result.project.title}' (id={result.project.id}) -> {result.path}")
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

    if args.command in (
        "archive-project",
        "archive-area",
        "archive-resource",
        "reactivate-project",
        "reactivate-area",
        "reactivate-resource",
    ):
        operation, _, kind = args.command.partition("-")
        spec = spec_by_kind[kind]
        execute = execute_archive if operation == "archive" else execute_reactivate

        request = ArchiveRequest(title=args.title, actor=Actor.HUMAN)
        result = execute(request, spec=spec)
        if not result.applicable:
            print(f"Not applicable: '{args.title}' cannot be {operation}d.")
            return 1
        print(f"{operation.capitalize()}d '{result.project.title}' -> {result.path}")
        return 0

    if args.command in ("evaluate-project", "evaluate-area"):
        spec = PROJECT if args.command == "evaluate-project" else AREA
        request = EvaluationRequest(
            title=args.title, result=OperationalResult(args.result), actor=Actor.HUMAN
        )
        result = execute_evaluation(request, spec=spec)
        if not result.applicable:
            print(f"Not applicable: '{args.title}' cannot be evaluated as '{args.result}'.")
            return 1
        print(f"Evaluated '{result.project.title}' as '{args.result}' -> {result.event.event_type}")
        return 0

    if args.command in ("review-project", "review-area", "review-resource"):
        _, _, kind = args.command.partition("-")
        spec = spec_by_kind[kind]
        request = ReviewRequest(title=args.title, actor=Actor.HUMAN, since=args.since)
        result = execute_review(request, spec=spec)
        if not result.applicable:
            print(f"Not applicable: '{args.title}' does not exist.")
            return 1
        print(
            f"Reviewed '{result.project.title}': {result.assessment.conclusion.value} "
            f"({'; '.join(result.assessment.basis)})"
        )
        return 0

    if args.command in ("enrich-project", "enrich-area", "enrich-resource"):
        _, _, kind = args.command.partition("-")
        spec = spec_by_kind[kind]
        request = KnowledgeRequest(
            title=args.title,
            understanding_title=args.understanding_title,
            understanding=args.understanding,
            provenance=tuple(args.provenance),
            actor=Actor.HUMAN,
        )
        result = execute_knowledge(request, spec=spec)
        if not result.applicable:
            print(f"Not applicable: '{args.title}' cannot be enriched.")
            return 1
        print(f"Enriched '{result.project.title}' -> {result.event.event_type}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
