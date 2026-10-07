from __future__ import annotations

import argparse
import contextlib
import sys
from pathlib import Path

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
    read_area_dashboard,
    read_contained_projects,
    write_area_dashboard,
)
from ohtli.execution.specs import AREA, JOURNAL_ENTRY, MEETING, PROJECT, REFERENCE, RESOURCE, display_name_of
from ohtli.vault_io import paths
from ohtli.vault_io.markdown import find_inbox_entry, list_inbox_entries
from ohtli.workflow.evaluation import OperationalResult
from ohtli.workflow.processing import derived_relationship_for_pair, relationship_for_pair


def refusal_message(result, title: str, label: str) -> str:
    """Why a create was refused, for a person reading a terminal.

    `title exists` keeps the wording every create-* always had. The other
    reasons say what is in the way of the file the title would be written to.
    Shared by the CLI and the deterministic trigger script, so both explain a
    refusal the same way.
    """
    article = "an" if label[0] in "AEIOU" else "a"
    if result.reason == "title_exists":
        return f"Not applicable: {article} {label} titled '{title}' already exists."
    return f"Not applicable: {article} {label} titled '{title}' cannot be created: {_blocked_detail(result, label)}"


def _blocked_detail(result, label: str) -> str:
    path = result.blocked_path
    if result.reason == "same_file_name":
        return f"{path} already holds {label} '{result.occupant_title}' (same file name). Choose a different title."
    if result.reason == "reserved_name":
        return f"the file name '{path.name}' is reserved. Choose a different title."
    return (
        f"{path} already exists and is not an Ohtli note; it was left untouched. "
        f"Move or rename it, or choose a different title."
    )


def _inbox_reason(result, label: str) -> str:
    """The sentence that follows "left untouched in Inbox." when a Create or
    an Update was refused; nothing for a refusal without a reason (a blank
    entry), which keeps its original message.

    `same_file_name`, `reserved_name` and `path_occupied` are Create refusing
    to overwrite. `ambiguous_title` and `not_an_ohtli_note` are Update unable
    to tell which note, if any, to rewrite: `existing_titles` only asks
    whether some file in the folder carries the title, never which one."""
    path = result.blocked_path
    if result.reason == "same_file_name":
        return f" {path} already holds {label} '{result.occupant_title}' (same file name); choose a different title."
    if result.reason == "reserved_name":
        return f" The file name '{path.name}' is reserved; choose a different title."
    if result.reason == "path_occupied":
        return (
            f" {path} already exists and is not an Ohtli note; it was left untouched. "
            f"Move or rename it, or choose a different title."
        )
    if result.reason == "ambiguous_title":
        names = ", ".join(p.name for p in result.candidates)
        return (
            f" {len(result.candidates)} {label} notes are titled '{result.search_title}' "
            f"({names}); rename all but one, then process again."
        )
    if result.reason == "not_an_ohtli_note" and path is not None:
        return f" {path} is titled '{result.search_title}' but is not an Ohtli {label} note; it was left untouched."
    if result.reason == "not_an_ohtli_note":
        return f" No {label} note titled '{result.search_title}' could be found to update."
    if result.reason == "unreadable_entry":
        return f" {path} is not a readable UTF-8 text file; convert or remove it."
    return ""


def _enrich_reason(result, label: str) -> str:
    """The sentence that follows "cannot be enriched." when Knowledge's
    Externalize could not locate the note to enrich: nothing for a refusal
    without a reason (blank understanding or provenance), which keeps its
    original message.

    Not `_inbox_reason`: this is never an Inbox entry, so "process again" /
    "update" would be the wrong verbs here. Knowledge always enriches an
    existing note (#160) — there is no Create-shaped refusal to cover."""
    if result.reason == "ambiguous_title":
        names = ", ".join(p.name for p in result.candidates)
        return (
            f" {len(result.candidates)} {label} notes are titled '{result.search_title}' "
            f"({names}); rename all but one, then enrich again."
        )
    if result.reason == "not_an_ohtli_note" and result.blocked_path is not None:
        return f" {result.blocked_path} is titled '{result.search_title}' but is not an Ohtli {label} note; it was left untouched."
    return ""


def _archive_reason(result, label: str, operation: str) -> str:
    """The sentence that follows "cannot be {archive,reactivate}d." when
    Archive/Reactivate could not locate the note to transition, or Archive's
    Operational Integrity refused it; nothing for a refusal without one of
    these reasons (`missing`, `wrong_context`), which keeps its original
    message.

    `operational_dependents` reads the dependents off `result.dependents` --
    gathered once, by the execution layer, while locating the note by title
    (#161) -- never a second, independent lookup here."""
    if result.reason == "operational_dependents":
        names = ", ".join(f"'{d['title']}'" for d in result.dependents)
        return (
            f" It is still required operationally by {names}. Archive does not "
            f"resolve this: unlink it, or archive the object(s) requiring it, first."
        )
    if result.reason == "ambiguous_title":
        names = ", ".join(p.name for p in result.candidates)
        return (
            f" {len(result.candidates)} {label} notes are titled '{result.search_title}' "
            f"({names}); rename all but one, then {operation} again."
        )
    if result.reason == "not_an_ohtli_note" and result.blocked_path is not None:
        return f" {result.blocked_path} is titled '{result.search_title}' but is not an Ohtli {label} note; it was left untouched."
    return ""


def _relationship_reason(result, *, source_label: str, target_label: str, operation: str) -> str:
    """The sentence appended to a link/unlink refusal when an end -- the
    source, or a named target -- could not be located (#162); nothing for
    `missing` or the Interaction Model's own refusals (undefined
    relationship, cardinality reached, already/not linked), which keep
    their original message.

    Not `_archive_reason`/`_enrich_reason`/`_inbox_reason`: a relationship
    has two ends, so the label to use (`source_label`/`target_label`)
    depends on `result.end` -- the two can share a title, so naming the
    right one matters."""
    label = source_label if result.end == "source" else target_label
    if result.reason == "ambiguous_title":
        names = ", ".join(p.name for p in result.candidates)
        return (
            f" {len(result.candidates)} {label} notes are titled '{result.search_title}' "
            f"({names}); rename all but one, then {operation} again."
        )
    if result.reason == "not_an_ohtli_note" and result.blocked_path is not None:
        return f" {result.blocked_path} is titled '{result.search_title}' but is not an Ohtli {label} note; it was left untouched."
    return ""


def _evaluation_reason(result, label: str) -> str:
    """The sentence that follows "cannot be evaluated as '<result>'." when
    Evaluate could not locate the note; nothing for a refusal without a
    location reason (wrong context, or a result this type cannot produce),
    which keeps its original message.

    Evaluate's Event is permanent (#163), so this gets the same treatment
    as the write-path helpers (`_archive_reason`/`_relationship_reason`),
    not `read_operational_dependents`'s bare `applicable` (#161)."""
    if result.reason == "ambiguous_title":
        names = ", ".join(p.name for p in result.candidates)
        return (
            f" {len(result.candidates)} {label} notes are titled '{result.search_title}' "
            f"({names}); rename all but one, then evaluate again."
        )
    if result.reason == "not_an_ohtli_note" and result.blocked_path is not None:
        return f" {result.blocked_path} is titled '{result.search_title}' but is not an Ohtli {label} note; it was left untouched."
    return ""


def _review_reason(result, label: str) -> str:
    """Same shape as `_evaluation_reason`, for Review; kept separate (own
    wording), per the precedent every workflow's CLI helper is its own."""
    if result.reason == "ambiguous_title":
        names = ", ".join(p.name for p in result.candidates)
        return (
            f" {len(result.candidates)} {label} notes are titled '{result.search_title}' "
            f"({names}); rename all but one, then review again."
        )
    if result.reason == "not_an_ohtli_note" and result.blocked_path is not None:
        return f" {result.blocked_path} is titled '{result.search_title}' but is not an Ohtli {label} note; it was left untouched."
    return ""


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

    parser = argparse.ArgumentParser(
        prog="ohtli",
        epilog=(
            "Global options such as --actor and --vault go before the command: "
            "ohtli --actor deterministic --vault /path/to/vault create-project X"
        ),
    )
    # Both declared only here, never on a subparser: a subparser default would
    # silently overwrite a value parsed before the command (--actor recording
    # `human`, --vault the real vault), with no error either way.
    parser.add_argument(
        "--actor",
        choices=[a.value for a in Actor],
        default=Actor.HUMAN.value,
        help=(
            "Who is invoking this command (default: human). Recorded as the actor of every "
            "Event it emits, for attribution only: it is not authentication or authorization "
            "and grants no permission. Commands that emit no Event ignore it"
        ),
    )
    parser.add_argument(
        "--vault",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "Vault root directory to use instead of the real vault (default: the real vault, "
            "today's behavior unchanged). DIR must already exist; its subfolders "
            "(projects/, journal/entries/, .ohtli/, ...) are created on demand, as in the real "
            "vault"
        ),
    )
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

    area_dashboard = subparsers.add_parser(
        "area-dashboard",
        help=(
            "Print an Area's dashboard: a read-only Markdown projection of the Area and its "
            "Projects. Writes nothing unless --write is given"
        ),
    )
    area_dashboard.add_argument("area")
    area_dashboard.add_argument(
        "--write",
        action="store_true",
        help=(
            "Also write it to the vault's dashboards folder, regenerating a previous one in "
            "full. Refuses to overwrite any file that ohtli did not generate"
        ),
    )

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
    actor = Actor(args.actor)

    if args.vault is not None and not args.vault.is_dir():
        parser.error(f"--vault {args.vault} is not an existing directory")

    vault = paths.vault_root(args.vault) if args.vault is not None else contextlib.nullcontext()
    with vault:
        if args.command == "create-project":
            request = ExecutionRequest(title=args.title, actor=actor)
            result = execute_capture(request)
            if not result.applicable:
                print(refusal_message(result, args.title, "Project"))
                return 1
            print(f"Captured Project '{result.project.title}' (id={result.project.id}) -> {result.path}")
            return 0

        if args.command == "create-area":
            request = ExecutionRequest(title=args.title, actor=actor)
            result = execute_capture(request, spec=AREA)
            if not result.applicable:
                print(refusal_message(result, args.title, "Area"))
                return 1
            print(f"Captured Area '{result.project.title}' (id={result.project.id}) -> {result.path}")
            return 0

        if args.command == "create-resource":
            request = ExecutionRequest(title=args.title, actor=actor)
            result = execute_capture(request, spec=RESOURCE)
            if not result.applicable:
                print(refusal_message(result, args.title, "Resource"))
                return 1
            print(f"Captured Resource '{result.project.title}' (id={result.project.id}) -> {result.path}")
            return 0

        if args.command == "create-reference":
            request = ExecutionRequest(title=args.title, actor=actor)
            result = execute_capture(request, spec=REFERENCE)
            if not result.applicable:
                print(refusal_message(result, args.title, "Reference"))
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

        if args.command == "area-dashboard":
            if not args.write:
                dashboard = read_area_dashboard(args.area)
                if not dashboard.applicable:
                    print(f"Not applicable: no Area titled '{args.area}'.")
                    return 1
                print(dashboard.markdown, end="")
                return 0

            written = write_area_dashboard(args.area)
            if not written.applicable:
                print(f"Not applicable: no Area titled '{args.area}'.")
                return 1
            if written.outcome == "refused":
                print(
                    f"Not written: {written.path} already exists and was not generated by ohtli; "
                    f"it was left untouched. Move or rename it, then re-run."
                )
                return 1
            if written.outcome == "unchanged":
                print(f"Area Dashboard for '{written.area_title}' is already up to date -> {written.path}")
            else:
                verb = "Wrote" if written.outcome == "created" else "Updated"
                print(f"{verb} Area Dashboard for '{written.area_title}' -> {written.path}")
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
                        actor=actor,
                        relationship_type=definition.relationship_type,
                    ),
                    source_spec=source_spec,
                    target_spec=target_spec,
                )
                if not result.applicable:
                    reason = _relationship_reason(
                        result,
                        source_label=source_spec.display_name,
                        target_label=target_spec.display_name,
                        operation="link",
                    )
                    print(
                        f"Not applicable: cannot link {args.from_type} '{args.from_title}' "
                        f"to {args.to_type} '{args.to_title}' (both must exist, it must not "
                        f"already be linked, and the cardinality must allow it).{reason}"
                    )
                    return 1
                print(f"{result.event.event_type}: '{args.from_title}' {definition.relationship_type} '{args.to_title}'")
                return 0

            result = execute_unrelate(
                UnrelateRequest(
                    source_title=args.from_title,
                    actor=actor,
                    relationship_type=definition.relationship_type,
                    target_title=args.to_title,
                ),
                spec=source_spec,
                target_spec=target_spec if args.to_title is not None else None,
            )
            if not result.applicable:
                reason = _relationship_reason(
                    result,
                    source_label=source_spec.display_name,
                    target_label=target_spec.display_name,
                    operation="unlink",
                )
                print(
                    f"Not applicable: cannot unlink {args.from_type} '{args.from_title}'. "
                    f"It must exist and be linked; a 0..* relationship also needs --to.{reason}"
                )
                return 1
            print(f"{result.event.event_type}: '{args.from_title}'")
            return 0

        if args.command == "link-project-to-area":
            request = RelateRequest(
                source_title=args.project, target_title=args.area, actor=actor
            )
            result = execute_relate(request)
            if not result.applicable:
                reason = _relationship_reason(
                    result, source_label="Project", target_label="Area", operation="link"
                )
                print(
                    f"Not applicable: cannot link Project '{args.project}' to Area '{args.area}' "
                    f"(both must exist, and a Project belongs to at most one Area).{reason}"
                )
                return 1
            print(f"{result.event.event_type}: '{args.project}' belongs to '{args.area}'")
            return 0

        if args.command == "unlink-project-from-area":
            request = UnrelateRequest(source_title=args.project, actor=actor)
            result = execute_unrelate(request)
            if not result.applicable:
                reason = _relationship_reason(
                    result, source_label="Project", target_label="Area", operation="unlink"
                )
                print(f"Not applicable: Project '{args.project}' does not exist or belongs to no Area.{reason}")
                return 1
            print(f"{result.event.event_type}: '{args.project}'")
            return 0

        if args.command == "create-journal-entry":
            request = ExecutionRequest(title=args.title, actor=actor)
            result = execute_capture(request, spec=JOURNAL_ENTRY)
            if not result.applicable:
                print(refusal_message(result, args.title, "Journal Entry"))
                return 1
            print(f"Captured Journal Entry '{result.project.title}' (id={result.project.id}) -> {result.path}")
            return 0

        if args.command == "create-meeting":
            request = ExecutionRequest(title=args.title, actor=actor)
            result = execute_capture(request, spec=MEETING)
            if not result.applicable:
                print(refusal_message(result, args.title, "Meeting"))
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
                request = ProcessingRequest(entry_path=entry_path, actor=actor)
                result = execute_processing(request, spec=spec_by_kind[args.kind])
                label = args.kind.replace("-", " ").title()
                if not result.applicable:
                    refused += 1
                    print(f"Not applicable: '{entry_path.name}' left untouched in Inbox.{_inbox_reason(result, label)}")
                    continue
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
            label = kind.replace("-", " ").title()
            execute = execute_archive if operation == "archive" else execute_reactivate

            request = ArchiveRequest(title=args.title, actor=actor)
            result = execute(request, spec=spec)
            if not result.applicable:
                print(f"Not applicable: '{args.title}' cannot be {operation}d.{_archive_reason(result, label, operation)}")
                return 1
            print(f"{operation.capitalize()}d '{result.project.title}' -> {result.path}")
            return 0

        if args.command in ("evaluate-project", "evaluate-area"):
            spec = PROJECT if args.command == "evaluate-project" else AREA
            request = EvaluationRequest(
                title=args.title, result=OperationalResult(args.result), actor=actor
            )
            result = execute_evaluation(request, spec=spec)
            if not result.applicable:
                reason = _evaluation_reason(result, spec.display_name)
                print(f"Not applicable: '{args.title}' cannot be evaluated as '{args.result}'.{reason}")
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
            request = ReviewRequest(title=args.title, actor=actor, since=args.since)
            result = execute_review(request, spec=spec)
            if not result.applicable:
                if result.reason in ("ambiguous_title", "not_an_ohtli_note"):
                    print(f"Not applicable: '{args.title}' cannot be reviewed.{_review_reason(result, spec.display_name)}")
                else:
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
                actor=actor,
            )
            result = execute_knowledge(request, spec=spec)
            if not result.applicable:
                label = kind.title()
                print(f"Not applicable: '{args.title}' cannot be enriched.{_enrich_reason(result, label)}")
                return 1
            print(f"Enriched '{result.project.title}' -> {result.event.event_type}")
            return 0

        return 1


if __name__ == "__main__":
    sys.exit(main())
