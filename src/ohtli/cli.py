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
    RelateRequest,
    ReviewRequest,
    UnrelateRequest,
    execute_archive,
    execute_capture,
    execute_evaluation,
    execute_knowledge,
    execute_processing,
    execute_reactivate,
    execute_relate,
    execute_review,
    execute_unrelate,
    read_contained_projects,
    read_operational_dependents,
)
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE, display_name_of
from ohtli.vault_io.markdown import find_inbox_entry, list_inbox_entries
from ohtli.workflow.evaluation import OperationalResult
from ohtli.workflow.processing import derived_relationship_for_pair, relationship_for_pair


def main(argv: list[str] | None = None) -> int:
    spec_by_kind = {
        "project": PROJECT,
        "area": AREA,
        "resource": RESOURCE,
        "reference": REFERENCE,
        "meeting": MEETING,
        "journal-entry": JOURNAL_ENTRY,
    }
    # The CLI kind (the `--from-type` / `--to-type` value) of a Domain class name.
    # Never derive it with `.lower()`: `JournalEntry` is `journal-entry`.
    kind_of_type = {spec.domain_type.__name__: kind for kind, spec in spec_by_kind.items()}

    parser = argparse.ArgumentParser(prog="ohtli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-project", help="Capture a new Project")
    create.add_argument("title")

    create_area = subparsers.add_parser("create-area", help="Capture a new Area")
    create_area.add_argument("title")

    create_resource = subparsers.add_parser("create-resource", help="Capture a new Resource")
    create_resource.add_argument("title")

    create_reference = subparsers.add_parser("create-reference", help="Capture a new Reference")
    create_reference.add_argument("title")

    create_meeting = subparsers.add_parser("create-meeting", help="Capture a new Meeting")
    create_meeting.add_argument("title")

    create_journal_entry = subparsers.add_parser(
        "create-journal-entry", help="Capture a new Journal Entry (title conventionally its moment)"
    )
    create_journal_entry.add_argument("title")

    process_inbox = subparsers.add_parser("process-inbox", help="Process all raw Inbox entries")
    process_inbox.add_argument(
        "--as",
        dest="kind",
        choices=list(spec_by_kind),
        default="project",
        help="Domain Object every entry in this run becomes (default: project)",
    )
    process_inbox.add_argument(
        "--entry",
        action="append",
        default=None,
        metavar="NAME",
        help=(
            "Process only this Inbox entry, given as its file name (with or without .md, never a "
            "path); repeat to name several. Without it, every Inbox entry is processed."
        ),
    )

    archive_project = subparsers.add_parser("archive-project", help="Archive a Project")
    archive_project.add_argument("title")

    archive_area = subparsers.add_parser("archive-area", help="Archive an Area")
    archive_area.add_argument("title")

    archive_resource = subparsers.add_parser("archive-resource", help="Archive a Resource")
    archive_resource.add_argument("title")

    archive_reference = subparsers.add_parser("archive-reference", help="Archive a Reference")
    archive_reference.add_argument("title")

    archive_meeting = subparsers.add_parser("archive-meeting", help="Archive a Meeting")
    archive_meeting.add_argument("title")

    archive_journal_entry = subparsers.add_parser(
        "archive-journal-entry", help="Archive a Journal Entry"
    )
    archive_journal_entry.add_argument("title")

    reactivate_project = subparsers.add_parser("reactivate-project", help="Reactivate a Project")
    reactivate_project.add_argument("title")

    reactivate_area = subparsers.add_parser("reactivate-area", help="Reactivate an Area")
    reactivate_area.add_argument("title")

    reactivate_resource = subparsers.add_parser("reactivate-resource", help="Reactivate a Resource")
    reactivate_resource.add_argument("title")

    reactivate_reference = subparsers.add_parser("reactivate-reference", help="Reactivate a Reference")
    reactivate_reference.add_argument("title")

    reactivate_meeting = subparsers.add_parser("reactivate-meeting", help="Reactivate a Meeting")
    reactivate_meeting.add_argument("title")

    reactivate_journal_entry = subparsers.add_parser(
        "reactivate-journal-entry", help="Reactivate a Journal Entry"
    )
    reactivate_journal_entry.add_argument("title")

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

    review_reference = subparsers.add_parser("review-reference", help="Review a Reference")
    review_reference.add_argument("title")
    review_reference.add_argument("--since", default=None)

    review_meeting = subparsers.add_parser("review-meeting", help="Review a Meeting")
    review_meeting.add_argument("title")
    review_meeting.add_argument("--since", default=None)

    link_project_to_area = subparsers.add_parser(
        "link-project-to-area", help="Relate a Project to an Area (Project belongs to Area)"
    )
    link_project_to_area.add_argument("project")
    link_project_to_area.add_argument("area")

    unlink_project_from_area = subparsers.add_parser(
        "unlink-project-from-area", help="Remove a Project's 'belongs to' relationship to its Area"
    )
    unlink_project_from_area.add_argument("project")

    link = subparsers.add_parser(
        "link",
        help="Relate two objects; the relationship type is derived from the pair of kinds",
    )
    link.add_argument("--from-type", required=True, choices=list(spec_by_kind))
    link.add_argument("--from", dest="from_title", required=True)
    link.add_argument("--to-type", required=True, choices=list(spec_by_kind))
    link.add_argument("--to", dest="to_title", required=True)

    unlink = subparsers.add_parser(
        "unlink",
        help="Remove a relationship; --to is required for a 0..* relationship, optional for 0..1",
    )
    unlink.add_argument("--from-type", required=True, choices=list(spec_by_kind))
    unlink.add_argument("--from", dest="from_title", required=True)
    unlink.add_argument("--to-type", required=True, choices=list(spec_by_kind))
    unlink.add_argument("--to", dest="to_title", default=None)

    contains = subparsers.add_parser(
        "contains",
        help="List the Projects an Area contains (derived from each Project's 'belongs to'; nothing is stored)",
    )
    contains.add_argument("area")

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

    if args.command == "create-reference":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request, spec=REFERENCE)
        if not result.applicable:
            print(f"Not applicable: a Reference titled '{args.title}' already exists.")
            return 1
        print(f"Captured Reference '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    if args.command == "contains":
        result = read_contained_projects(args.area)
        if not result.applicable:
            print(f"Not applicable: no Area titled '{args.area}'.")
            return 1
        if not result.projects:
            print(f"Area '{args.area}' contains no Projects.")
            return 0
        print(f"Area '{args.area}' contains {len(result.projects)} Project(s):")
        for project in result.projects:
            historical = " [historical]" if project["context"] == "historical" else ""
            print(f"  {project['title']}{historical} (status={project['status']}, id={project['id']})")
        return 0

    if args.command in ("link", "unlink"):
        source_spec = spec_by_kind[args.from_type]
        target_spec = spec_by_kind[args.to_type]
        source_type = source_spec.domain_type.__name__
        target_type = target_spec.domain_type.__name__
        derived = derived_relationship_for_pair(source_type, target_type)
        if derived is not None:
            via = derived.via
            via_source_kind = kind_of_type[via.source_type]
            via_target_kind = kind_of_type[via.target_type]
            print(
                f"'{display_name_of(source_type)} {derived.relationship_type} {display_name_of(target_type)}' "
                f"is derived from '{display_name_of(via.source_type)} {via.relationship_type} "
                f"{display_name_of(via.target_type)}' and is never established directly. "
                f"Use: ohtli {args.command} --from-type {via_source_kind} --from <{via_source_kind}> "
                f"--to-type {via_target_kind} --to <{via_target_kind}>; read it with: ohtli contains <area>."
            )
            return 1
        definition = relationship_for_pair(source_type, target_type)
        if definition is None:
            print(
                f"No canonical relationship is implemented from '{args.from_type}' "
                f"to '{args.to_type}'."
            )
            return 1

        if args.command == "link":
            result = execute_relate(
                RelateRequest(
                    source_title=args.from_title,
                    target_title=args.to_title,
                    actor=Actor.HUMAN,
                    relationship_type=definition.relationship_type,
                ),
                source_spec=source_spec,
                target_spec=target_spec,
            )
            if not result.applicable:
                print(
                    f"Not applicable: cannot link {args.from_type} '{args.from_title}' "
                    f"to {args.to_type} '{args.to_title}' (both must exist, it must not "
                    "already be linked, and the cardinality must allow it)."
                )
                return 1
            print(f"{result.event.event_type}: '{args.from_title}' {definition.relationship_type} '{args.to_title}'")
            return 0

        result = execute_unrelate(
            UnrelateRequest(
                source_title=args.from_title,
                actor=Actor.HUMAN,
                relationship_type=definition.relationship_type,
                target_title=args.to_title,
            ),
            spec=source_spec,
            target_spec=target_spec if args.to_title is not None else None,
        )
        if not result.applicable:
            print(
                f"Not applicable: cannot unlink {args.from_type} '{args.from_title}'. "
                "It must exist and be linked; a 0..* relationship also needs --to."
            )
            return 1
        print(f"{result.event.event_type}: '{args.from_title}'")
        return 0

    if args.command == "link-project-to-area":
        request = RelateRequest(
            source_title=args.project, target_title=args.area, actor=Actor.HUMAN
        )
        result = execute_relate(request)
        if not result.applicable:
            print(
                f"Not applicable: cannot link Project '{args.project}' to Area '{args.area}' "
                "(both must exist, and a Project belongs to at most one Area)."
            )
            return 1
        print(f"{result.event.event_type}: '{args.project}' belongs to '{args.area}'")
        return 0

    if args.command == "unlink-project-from-area":
        request = UnrelateRequest(source_title=args.project, actor=Actor.HUMAN)
        result = execute_unrelate(request)
        if not result.applicable:
            print(f"Not applicable: Project '{args.project}' does not exist or belongs to no Area.")
            return 1
        print(f"{result.event.event_type}: '{args.project}'")
        return 0

    if args.command == "create-journal-entry":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request, spec=JOURNAL_ENTRY)
        if not result.applicable:
            print(f"Not applicable: a Journal Entry titled '{args.title}' already exists.")
            return 1
        print(f"Captured Journal Entry '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    if args.command == "create-meeting":
        request = ExecutionRequest(title=args.title, actor=Actor.HUMAN)
        result = execute_capture(request, spec=MEETING)
        if not result.applicable:
            print(f"Not applicable: a Meeting titled '{args.title}' already exists.")
            return 1
        print(f"Captured Meeting '{result.project.title}' (id={result.project.id}) -> {result.path}")
        return 0

    if args.command == "process-inbox":
        named = args.entry is not None
        if named:
            # Resolve every name before processing anything: an unknown name
            # must not leave a half-done run, because processing deletes the entry.
            entries = []
            unresolved = []
            for name in args.entry:
                found = find_inbox_entry(name)
                if found is None:
                    unresolved.append(name)
                elif found not in entries:
                    entries.append(found)
            if unresolved:
                for name in unresolved:
                    print(f"Not applicable: no Inbox entry named '{name}'.")
                print("Nothing was processed.")
                return 1
        else:
            entries = list_inbox_entries()
            if not entries:
                print("Inbox is empty.")
                return 0

        refused = 0
        for entry_path in entries:
            request = ProcessingRequest(entry_path=entry_path, actor=Actor.HUMAN)
            result = execute_processing(request, spec=spec_by_kind[args.kind])
            if not result.applicable:
                refused += 1
                print(f"Not applicable: '{entry_path.name}' left untouched in Inbox.")
                continue
            label = args.kind.replace("-", " ").title()
            if result.operation == "update":
                # No new text to add (blank remainder) still resolves the
                # entry, but writes and emits nothing: say so honestly
                # instead of claiming an update that did not happen.
                verb = "Updated" if result.event is not None else "Resolved"
            else:
                verb = "Processed"
            print(f"{verb} {label} '{result.project.title}' (id={result.project.id}) -> {result.path}")
        # Batch mode keeps exiting 0 when it refuses entries; an entry the user
        # asked for by name that could not be processed is a failure.
        return 1 if (named and refused) else 0

    if args.command in (
        "archive-project",
        "archive-area",
        "archive-resource",
        "archive-reference",
        "archive-meeting",
        "archive-journal-entry",
        "reactivate-project",
        "reactivate-area",
        "reactivate-resource",
        "reactivate-reference",
        "reactivate-meeting",
        "reactivate-journal-entry",
    ):
        operation, _, kind = args.command.partition("-")
        spec = spec_by_kind[kind]
        execute = execute_archive if operation == "archive" else execute_reactivate

        request = ArchiveRequest(title=args.title, actor=Actor.HUMAN)
        result = execute(request, spec=spec)
        if not result.applicable:
            if result.reason == "operational_dependents":
                dependents = read_operational_dependents(args.title, spec)
                names = ", ".join(f"'{d['title']}'" for d in dependents)
                print(
                    f"Not applicable: '{args.title}' cannot be archived. It is still required "
                    f"operationally by {names}. Archive does not resolve this: unlink it, or "
                    f"archive the object(s) requiring it, first."
                )
            else:
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

    if args.command in (
        "review-project",
        "review-area",
        "review-resource",
        "review-reference",
        "review-meeting",
    ):
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
