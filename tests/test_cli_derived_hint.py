"""The hint printed when a derived relationship is asked to be established.

`Area contains Project` is the only derived relationship today, so the hint is
correct for the types involved. The hint is built from Domain class names, and
`JournalEntry` is not a valid CLI kind (`journal-entry`) nor a display name
("Journal Entry"). These tests give every type a turn in a simulated derived
relationship, so the hint is checked for the cases that cannot happen yet.
"""

import itertools
import re

import pytest

from ohtli.cli import main
from ohtli.execution.specs import ALL_SPECS, display_name_of
from ohtli.vault_io import paths
from ohtli.workflow import processing

# CLI kind (the --from-type / --to-type value) for each Domain class name
KIND_OF = {
    "Project": "project",
    "Area": "area",
    "Resource": "resource",
    "Reference": "reference",
    "Meeting": "meeting",
    "JournalEntry": "journal-entry",
}
CLASS_NAMES = [spec.domain_type.__name__ for spec in ALL_SPECS]
PAIRS = list(itertools.permutations(CLASS_NAMES, 2))


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
    ):
        monkeypatch.setattr(paths, name, tmp_path / sub)


def _simulate_derived(monkeypatch, source, target):
    """`source contains target`, derived from `target belongs to source` (the
    shape of `Area contains Project`), for any pair of types."""
    derived = processing.DerivedRelationshipDefinition(
        source, "contains", target, via=processing.RelationshipDefinition(target, "belongs to", source, 1)
    )
    monkeypatch.setattr(processing, "DERIVED_RELATIONSHIPS", (derived,))


def _run(capsys, *argv):
    code = main(list(argv))
    return code, capsys.readouterr().out


def _kinds_in(out, command):
    match = re.search(rf"Use: ohtli {command} --from-type (\S+) --from <\S+> --to-type (\S+) --to <\S+>", out)
    assert match, f"no suggested command in: {out}"
    return match.group(1), match.group(2)


def test_the_real_message_for_area_contains_project_is_unchanged(capsys):
    """No simulation: the only derived relationship that exists, letter for letter."""
    code, out = _run(capsys, "link", "--from-type", "area", "--from", "a", "--to-type", "project", "--to", "p")

    assert code == 1
    assert out.strip() == (
        "'Area contains Project' is derived from 'Project belongs to Area' and is never established "
        "directly. Use: ohtli link --from-type project --from <project> --to-type area --to <area>; "
        "read it with: ohtli contains <area>."
    )


@pytest.mark.parametrize("command", ["link", "unlink"])
@pytest.mark.parametrize("source,target", PAIRS, ids=[f"{s}-{t}" for s, t in PAIRS])
def test_the_hint_suggests_the_cli_kinds_of_the_types_involved(capsys, monkeypatch, command, source, target):
    _simulate_derived(monkeypatch, source, target)

    code, out = _run(
        capsys, command, "--from-type", KIND_OF[source], "--from", "a", "--to-type", KIND_OF[target], "--to", "b"
    )

    assert code == 1
    # the suggested command goes the other way: from the `via` source (the target here) to the `via` target
    assert _kinds_in(out, command) == (KIND_OF[target], KIND_OF[source])


@pytest.mark.parametrize("command", ["link", "unlink"])
@pytest.mark.parametrize("source,target", PAIRS, ids=[f"{s}-{t}" for s, t in PAIRS])
def test_the_suggested_command_is_a_valid_invocation(capsys, monkeypatch, command, source, target):
    """What the message recommends must at least be accepted by the parser; a
    rejected `--from-type` would make `main` raise SystemExit (argparse exits 2)."""
    _simulate_derived(monkeypatch, source, target)
    _, out = _run(
        capsys, command, "--from-type", KIND_OF[source], "--from", "a", "--to-type", KIND_OF[target], "--to", "b"
    )
    from_kind, to_kind = _kinds_in(out, command)

    argv = [command, "--from-type", from_kind, "--from", "a", "--to-type", to_kind]
    argv += ["--to", "b"]
    code = main(argv)  # SystemExit here would be an argparse rejection

    assert isinstance(code, int)
    capsys.readouterr()


@pytest.mark.parametrize("source,target", PAIRS, ids=[f"{s}-{t}" for s, t in PAIRS])
def test_the_prose_uses_display_names_never_a_class_name(capsys, monkeypatch, source, target):
    _simulate_derived(monkeypatch, source, target)

    _, out = _run(
        capsys, "link", "--from-type", KIND_OF[source], "--from", "a", "--to-type", KIND_OF[target], "--to", "b"
    )

    assert "JournalEntry" not in out and "journalentry" not in out
    assert f"'{display_name_of(source)} contains {display_name_of(target)}' is derived from" in out
    assert f"'{display_name_of(target)} belongs to {display_name_of(source)}'" in out
