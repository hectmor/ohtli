"""`ohtli area-dashboard <area> [--write]`, through the real `main`, with every
vault directory (including the dashboards folder) redirected to `tmp_path`.

Default mode prints the Markdown and writes nothing. `--write` also writes it,
prints a single status line, and refuses to overwrite a file ohtli did not
generate.
"""

import hashlib

import pytest

from ohtli.cli import main
from ohtli.representation.area_dashboard import GENERATED_MARKER
from ohtli.vault_io import paths


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


@pytest.fixture
def vault(tmp_path, capsys):
    """Health holds Alpha (operational) and Zeta (archived)."""
    for kind, title in (("area", "Health"), ("area", "Finance"), ("project", "Alpha"), ("project", "Zeta")):
        assert _run(capsys, f"create-{kind}", title)[0] == 0
    for project in ("Alpha", "Zeta"):
        code, _ = _run(
            capsys, "link", "--from-type", "project", "--from", project, "--to-type", "area", "--to", "Health"
        )
        assert code == 0
    assert _run(capsys, "archive-project", "Zeta")[0] == 0
    return tmp_path


def _files(tmp_path):
    return sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())


def _events(tmp_path):
    log = tmp_path / ".ohtli" / "events.jsonl"
    return log.read_bytes() if log.exists() else b""


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dashboard(tmp_path, slug="health"):
    return tmp_path / "dashboards" / "areas" / f"{slug}-dashboard.md"


# ---- default mode: print, write nothing ---------------------------------------------


def test_the_default_mode_prints_the_dashboard_and_exits_zero(capsys, vault):
    code, out = _run(capsys, "area-dashboard", "Health")

    assert code == 0
    assert out.splitlines()[0] == GENERATED_MARKER
    assert "# Health: Area Dashboard" in out.splitlines()
    assert "- [[projects/alpha|Alpha]] (status: planned)" in out.splitlines()
    assert "- [[projects/zeta|Zeta]] (status: planned)" in out.splitlines()


def test_the_default_mode_writes_nothing(capsys, vault):
    files, events = _files(vault), _events(vault)

    _run(capsys, "area-dashboard", "Health")
    _run(capsys, "area-dashboard", "Nope")

    assert _files(vault) == files
    assert _events(vault) == events
    assert not (vault / "dashboards").exists()


def test_the_argument_may_be_spelled_differently_from_the_areas_title(capsys, vault):
    assert _run(capsys, "area-dashboard", "health") == _run(capsys, "area-dashboard", "Health")


def test_the_projects_are_split_into_operational_and_historical(capsys, vault):
    _, out = _run(capsys, "area-dashboard", "Health")

    operational, historical = out.split("### Historical")
    assert "[[projects/alpha|Alpha]]" in operational and "[[projects/zeta|Zeta]]" not in operational
    assert "[[projects/zeta|Zeta]]" in historical and "[[projects/alpha|Alpha]]" not in historical


# ---- an unknown Area, in both modes -------------------------------------------------


@pytest.mark.parametrize("flags", [[], ["--write"]], ids=["default", "write"])
def test_an_unknown_area_exits_one_with_the_contains_message_and_writes_nothing(capsys, vault, flags):
    files = _files(vault)

    code, out = _run(capsys, "area-dashboard", "Nope", *flags)

    assert code == 1
    assert out == "Not applicable: no Area titled 'Nope'.\n"
    assert _files(vault) == files
    assert not (vault / "dashboards").exists()


def test_the_message_is_the_same_as_the_one_contains_prints(capsys, vault):
    assert _run(capsys, "area-dashboard", "Nope") == _run(capsys, "contains", "Nope")


# ---- --write ------------------------------------------------------------------------


def test_write_creates_exactly_one_file_and_prints_one_status_line(capsys, vault):
    before = set(_files(vault))

    code, out = _run(capsys, "area-dashboard", "Health", "--write")

    assert code == 0
    assert out == f"Wrote Area Dashboard for 'Health' -> {_dashboard(vault)}\n"
    assert set(_files(vault)) - before == {"dashboards/areas/health-dashboard.md"}


def test_write_puts_the_same_text_in_the_file_that_the_default_mode_prints(capsys, vault):
    _run(capsys, "area-dashboard", "Health", "--write")

    _, printed = _run(capsys, "area-dashboard", "Health")

    assert _dashboard(vault).read_text(encoding="utf-8") == printed


def test_writing_again_says_it_is_up_to_date_and_changes_nothing(capsys, vault):
    _run(capsys, "area-dashboard", "Health", "--write")
    digest = _sha(_dashboard(vault))

    code, out = _run(capsys, "area-dashboard", "Health", "--write")

    assert code == 0
    assert out == f"Area Dashboard for 'Health' is already up to date -> {_dashboard(vault)}\n"
    assert _sha(_dashboard(vault)) == digest


def test_after_the_vault_changes_write_regenerates_and_says_updated(capsys, vault):
    _run(capsys, "area-dashboard", "Health", "--write")
    assert _run(capsys, "archive-project", "Alpha")[0] == 0

    code, out = _run(capsys, "area-dashboard", "Health", "--write")

    assert code == 0
    assert out == f"Updated Area Dashboard for 'Health' -> {_dashboard(vault)}\n"
    assert "[[projects/alpha|Alpha]]" in _dashboard(vault).read_text(encoding="utf-8").split("### Historical")[1]


def test_the_status_line_uses_the_areas_real_title_not_the_argument(capsys, vault):
    code, out = _run(capsys, "area-dashboard", "health", "--write")

    assert code == 0 and out.startswith("Wrote Area Dashboard for 'Health' ->")


def test_a_hand_made_file_at_the_dashboards_path_is_refused_and_untouched(capsys, vault):
    decoy = _dashboard(vault, "finance")
    decoy.parent.mkdir(parents=True)
    decoy.write_text("# mine\n", encoding="utf-8")
    digest = _sha(decoy)

    code, out = _run(capsys, "area-dashboard", "Finance", "--write")

    assert code == 1
    assert out == (
        f"Not written: {decoy} already exists and was not generated by ohtli; "
        f"it was left untouched. Move or rename it, then re-run.\n"
    )
    assert _sha(decoy) == digest


def test_no_mode_emits_an_event_or_touches_a_note(capsys, vault):
    events = _events(vault)
    notes = {p.name: _sha(p) for d in ("areas", "projects") for p in (vault / d).glob("*.md")}

    for argv in (["Health"], ["Health", "--write"], ["Health", "--write"], ["Nope"], ["Nope", "--write"]):
        _run(capsys, "area-dashboard", *argv)

    assert _events(vault) == events
    assert {p.name: _sha(p) for d in ("areas", "projects") for p in (vault / d).glob("*.md")} == notes


def test_the_dashboard_lands_in_the_dashboards_folder_not_next_to_the_area(capsys, vault):
    _run(capsys, "area-dashboard", "Health", "--write")

    assert _dashboard(vault).exists()
    assert not (vault / "areas" / "health-dashboard.md").exists()


# ---- the command line itself --------------------------------------------------------


def test_the_area_argument_is_required(capsys):
    with pytest.raises(SystemExit) as raised:
        main(["area-dashboard"])

    assert raised.value.code == 2


def _flat(text):
    """argparse wraps help text; compare it with the line breaks collapsed."""
    return " ".join(text.split())


def test_the_commands_own_help_documents_write_and_the_refusal(capsys):
    with pytest.raises(SystemExit) as raised:
        main(["area-dashboard", "--help"])
    out = _flat(capsys.readouterr().out)

    assert raised.value.code == 0
    assert "--write" in out
    assert "Also write it to the vault's dashboards folder" in out
    assert "Refuses to overwrite any file that ohtli did not generate" in out


def test_the_top_level_help_says_nothing_is_written_unless_write_is_given(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])
    out = _flat(capsys.readouterr().out)

    assert "Writes nothing unless --write is given" in out
