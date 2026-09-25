"""The global `ohtli --actor <actor> <command>` option.

The actor is attribution only: it says who invoked the command and is recorded
on every Event it emits. It is not authentication or authorization (ADR-0006).
Default is `human`. The option belongs before the command; after it, argparse
refuses it, so a misplaced flag can never be recorded under the wrong actor.

Every vault directory is redirected to `tmp_path`, so nothing here can reach
the real vault.
"""

import ast
import re
from pathlib import Path

import pytest

from ohtli import cli
from ohtli.cli import main
from ohtli.execution.execution import Actor
from ohtli.vault_io import paths
from ohtli.vault_io.events import read_events

READ_ONLY = {"contains", "area-dashboard"}
KINDS = ["project", "area", "resource", "reference", "meeting", "journal-entry"]
REVIEWABLE = ["project", "area", "resource", "reference", "meeting"]


@pytest.fixture(autouse=True)
def _isolated_vault(tmp_path, monkeypatch):
    for name, sub in (
        ("PROJECTS_DIR", "projects"),
        ("AREAS_DIR", "areas"),
        ("RESOURCES_DIR", "resources"),
        ("REFERENCES_DIR", "references"),
        ("MEETINGS_DIR", "meetings"),
        ("JOURNAL_ENTRIES_DIR", "journal"),
        ("INBOX_DIR", "inbox"),
        ("EVENTS_DIR", ".ohtli"),
        ("AREA_DASHBOARDS_DIR", "dashboards/areas"),
    ):
        monkeypatch.setattr(paths, name, tmp_path / sub)


def _run(capsys, *argv):
    code = main(list(argv))
    return code, capsys.readouterr().out


def _events(tmp_path):
    return read_events(events_dir=tmp_path / ".ohtli")


def _files(tmp_path):
    return sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())


def _create(kind, title="X"):
    return [f"create-{kind}", title]


# (id, commands that prepare the vault, the command under test). Each command
# under test must emit at least one Event.
CASES = (
    [(f"create-{k}", [], _create(k)) for k in KINDS]
    + [(f"archive-{k}", [_create(k)], [f"archive-{k}", "X"]) for k in KINDS]
    + [
        (f"reactivate-{k}", [_create(k), [f"archive-{k}", "X"]], [f"reactivate-{k}", "X"])
        for k in KINDS
    ]
    + [(f"review-{k}", [_create(k)], [f"review-{k}", "X"]) for k in REVIEWABLE]
    + [
        # Each Domain Object accepts only its own results (`AREA.allowed_results`
        # has no `progress`), so the result differs per kind.
        (f"evaluate-{k}", [_create(k)], [f"evaluate-{k}", "X", "--result", result])
        for k, result in (("project", "progress"), ("area", "maintenance"))
    ]
    + [
        (
            f"enrich-{k}",
            [_create(k)],
            [f"enrich-{k}", "X", "--understanding-title", "T", "--understanding", "U", "--provenance", "p"],
        )
        for k in ("project", "area", "resource")
    ]
    + [
        (
            "link-project-to-area",
            [_create("project", "P"), _create("area", "A")],
            ["link-project-to-area", "P", "A"],
        ),
        (
            "unlink-project-from-area",
            [_create("project", "P"), _create("area", "A"), ["link-project-to-area", "P", "A"]],
            ["unlink-project-from-area", "P"],
        ),
        (
            "link",
            [_create("project", "P"), _create("area", "A")],
            ["link", "--from-type", "project", "--from", "P", "--to-type", "area", "--to", "A"],
        ),
        (
            "unlink",
            [
                _create("project", "P"),
                _create("area", "A"),
                ["link-project-to-area", "P", "A"],
            ],
            ["unlink", "--from-type", "project", "--from", "P", "--to-type", "area", "--to", "A"],
        ),
    ]
)
IDS = [case[0] for case in CASES]


def _prepare(capsys, setup):
    for argv in setup:
        assert _run(capsys, *argv)[0] == 0, argv


def _new_events(tmp_path, capsys, setup, command, flags):
    _prepare(capsys, setup)
    before = len(_events(tmp_path))
    code, _ = _run(capsys, *flags, *command)
    assert code == 0, command
    new = _events(tmp_path)[before:]
    assert new, f"{command} was expected to emit an Event"
    return new


# ---- every Event-emitting command records the declared actor ------------------------


@pytest.mark.parametrize(("case_id", "setup", "command"), CASES, ids=IDS)
def test_a_declared_actor_is_recorded_on_every_event_the_command_emits(
    capsys, tmp_path, case_id, setup, command
):
    new = _new_events(tmp_path, capsys, setup, command, ["--actor", "ai_assisted"])

    assert {e.actor for e in new} == {"ai_assisted"}


@pytest.mark.parametrize(("case_id", "setup", "command"), CASES, ids=IDS)
def test_without_the_option_every_event_is_still_recorded_as_human(capsys, tmp_path, case_id, setup, command):
    new = _new_events(tmp_path, capsys, setup, command, [])

    assert {e.actor for e in new} == {"human"}


def _subcommands(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])
    flat = " ".join(capsys.readouterr().out.split())
    return set(re.search(r"\{([a-z\-,]+)\}", flat).group(1).split(","))


def test_the_case_table_covers_every_subcommand_of_the_parser(capsys):
    covered = {case[2][0] for case in CASES} | READ_ONLY | {"process-inbox"}

    assert _subcommands(capsys) == covered


@pytest.mark.parametrize("actor", ["human", "deterministic", "ai_assisted", "hybrid"])
def test_each_of_the_four_actors_lands_verbatim(capsys, tmp_path, actor):
    assert _run(capsys, "--actor", actor, "create-project", "X")[0] == 0

    assert [e.actor for e in _events(tmp_path)] == [actor]


def test_the_choices_are_exactly_the_actor_enum_values():
    assert {a.value for a in Actor} == {"human", "deterministic", "ai_assisted", "hybrid"}


# ---- process-inbox: one Event per entry, all with the declared actor ----------------


@pytest.mark.parametrize(("flags", "expected"), [(["--actor", "hybrid"], "hybrid"), ([], "human")])
def test_process_inbox_records_the_actor_on_every_entry(capsys, tmp_path, flags, expected):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "a.md").write_text("Alpha idea\n", encoding="utf-8")
    (inbox / "b.md").write_text("Beta idea\n", encoding="utf-8")

    assert _run(capsys, *flags, "process-inbox")[0] == 0

    assert [e.actor for e in _events(tmp_path)] == [expected, expected]


# ---- refusing a wrong or misplaced option -------------------------------------------


@pytest.mark.parametrize("value", ["robot", "HUMAN", "", "ai-assisted"])
def test_an_unknown_actor_exits_two_and_writes_nothing(capsys, tmp_path, value):
    with pytest.raises(SystemExit) as raised:
        main(["--actor", value, "create-project", "X"])

    assert raised.value.code == 2
    assert _files(tmp_path) == []


def test_the_option_after_the_command_exits_two_and_writes_nothing(capsys, tmp_path):
    with pytest.raises(SystemExit) as raised:
        main(["create-project", "X", "--actor", "deterministic"])

    assert raised.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
    assert _files(tmp_path) == []


def test_the_option_without_a_value_exits_two(capsys, tmp_path):
    with pytest.raises(SystemExit) as raised:
        main(["create-project", "X", "--actor"])

    assert raised.value.code == 2
    assert _files(tmp_path) == []


def test_the_help_says_the_actor_is_attribution_only(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])
    out = " ".join(capsys.readouterr().out.split())

    assert "--actor" in out
    assert "not authentication or authorization" in out


# ---- commands that emit no Event ignore it ------------------------------------------


def test_read_only_commands_ignore_the_option_and_leave_the_log_untouched(capsys, tmp_path):
    for argv in (_create("area", "Health"), _create("project", "Alpha")):
        assert _run(capsys, *argv)[0] == 0
    assert _run(capsys, "link-project-to-area", "Alpha", "Health")[0] == 0
    log = tmp_path / ".ohtli" / "events.jsonl"
    before = log.read_bytes()

    for argv in (["contains", "Health"], ["area-dashboard", "Health"]):
        plain = _run(capsys, *argv)
        declared = _run(capsys, "--actor", "deterministic", *argv)
        assert declared == plain

    assert _run(capsys, "--actor", "deterministic", "area-dashboard", "Health", "--write")[0] == 0
    assert log.read_bytes() == before


# ---- no site left behind ------------------------------------------------------------


def _cli_tree():
    return ast.parse(Path(cli.__file__).read_text(encoding="utf-8"))


def test_the_human_actor_is_named_in_cli_only_as_the_default():
    human = [
        node
        for node in ast.walk(_cli_tree())
        if isinstance(node, ast.Attribute)
        and node.attr == "HUMAN"
        and isinstance(node.value, ast.Name)
        and node.value.id == "Actor"
    ]

    assert len(human) == 1, "Actor.HUMAN may appear only as the option's default"


def test_every_actor_keyword_argument_in_cli_uses_the_resolved_actor():
    wrong = [
        node.lineno
        for node in ast.walk(_cli_tree())
        if isinstance(node, ast.keyword)
        and node.arg == "actor"
        and not (isinstance(node.value, ast.Name) and node.value.id == "actor")
    ]

    assert wrong == []
