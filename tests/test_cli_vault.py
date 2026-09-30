"""`ohtli --vault DIR <command>`: point the whole CLI at a chosen vault.

Declared only on the top-level parser, the same rule `--actor` follows (a
subparser default would silently overwrite it, since a shared parent parser
resolves options before the subcommand). Optional: omitted, every command
keeps writing to the real vault by default, unchanged. `DIR` must already
exist; its layout (`projects/`, `journal/entries/`, `.ohtli/`, ...) mirrors
the real vault's own folder names exactly.

Every default `paths.*_DIR` is redirected to a SENTINEL location distinct
from the vault any given test passes to `--vault`. A write landing in the
sentinel instead of under `--vault` proves `--vault` was not what redirected
it — `tests/conftest.py`'s autouse isolation only ever patches two of the
nine folders (`EVENTS_DIR`, `AREA_DASHBOARDS_DIR`), so it alone cannot make
these tests pass.
"""

import pytest

from ohtli.cli import main
from ohtli.vault_io import paths

LAYOUT = {
    "VAULT_DIR": "",
    "PROJECTS_DIR": "projects",
    "AREAS_DIR": "areas",
    "RESOURCES_DIR": "resources",
    "REFERENCES_DIR": "references",
    "MEETINGS_DIR": "meetings",
    "JOURNAL_ENTRIES_DIR": "journal/entries",
    "INBOX_DIR": "inbox",
    "EVENTS_DIR": ".ohtli",
    "AREA_DASHBOARDS_DIR": "dashboards/areas",
}

KINDS = [
    ("create-project", "projects", "Project"),
    ("create-area", "areas", "Area"),
    ("create-resource", "resources", "Resource"),
    ("create-reference", "references", "Reference"),
    ("create-meeting", "meetings", "Meeting"),
    ("create-journal-entry", "journal/entries", "Journal Entry"),
]
IDS = [k[0] for k in KINDS]


@pytest.fixture(autouse=True)
def sentinel(tmp_path, monkeypatch):
    root = tmp_path / "sentinel"
    for name, sub in LAYOUT.items():
        monkeypatch.setattr(paths, name, (root / sub) if sub else root)
    return root


@pytest.fixture
def chosen(tmp_path):
    root = tmp_path / "chosen"
    root.mkdir()
    return root


def _run(capsys, *argv):
    code = main(list(argv))
    return code, capsys.readouterr().out


def _files(root):
    if not root.exists():
        return []
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


# ---- the help text --------------------------------------------------------------------


def test_the_help_mentions_vault(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])
    out = " ".join(capsys.readouterr().out.split())

    assert "--vault" in out


# ---- every create-* lands under the chosen vault, never the sentinel ----------------


@pytest.mark.parametrize(("command", "folder", "label"), KINDS, ids=IDS)
def test_a_note_lands_under_the_chosen_vault_not_the_sentinel(capsys, chosen, sentinel, command, folder, label):
    code, out = _run(capsys, "--vault", str(chosen), command, "Test Title")

    assert code == 0
    assert (chosen / folder / "test-title.md").exists()
    assert _files(sentinel) == []


@pytest.mark.parametrize(("command", "folder", "label"), KINDS, ids=IDS)
def test_the_event_lands_under_the_chosen_vaults_ohtli_folder(capsys, chosen, sentinel, command, folder, label):
    _run(capsys, "--vault", str(chosen), command, "Test Title")

    assert (chosen / ".ohtli" / "events.jsonl").exists()
    assert not (sentinel / ".ohtli").exists()


# ---- process-inbox reads from the chosen vault's own inbox --------------------------


def test_process_inbox_reads_from_the_chosen_vaults_inbox(capsys, chosen, sentinel):
    (chosen / "inbox").mkdir(parents=True)
    (chosen / "inbox" / "idea.md").write_text("A Good Idea\n\nworth pursuing.\n", encoding="utf-8")

    code, out = _run(capsys, "--vault", str(chosen), "process-inbox", "--entry", "idea")

    assert code == 0
    assert (chosen / "projects" / "a-good-idea.md").exists()
    assert _files(sentinel) == []


# ---- area-dashboard --write lands in its own folder, not next to the Area notes -----


def test_area_dashboard_write_lands_in_dashboards_not_areas(capsys, chosen, sentinel):
    _run(capsys, "--vault", str(chosen), "create-area", "Health")

    code, out = _run(capsys, "--vault", str(chosen), "area-dashboard", "Health", "--write")

    assert code == 0
    assert (chosen / "dashboards" / "areas" / "health-dashboard.md").exists()
    assert not (chosen / "areas" / "health-dashboard.md").exists()
    assert _files(sentinel) == []


# ---- read_operational_dependents (Archive's guard) is called with base_dir=None -----
# and so relies entirely on --vault having redirected the *_DIR constants, not on an
# explicit override passed by the caller. This is the regression the module-patching
# design is FOR.


def test_an_operational_dependent_is_named_correctly_under_a_chosen_vault(capsys, chosen, sentinel):
    _run(capsys, "--vault", str(chosen), "create-project", "Fitness Plan")
    _run(capsys, "--vault", str(chosen), "create-resource", "Fitness Gear")
    _run(
        capsys,
        "--vault",
        str(chosen),
        "link",
        "--from-type",
        "resource",
        "--from",
        "Fitness Gear",
        "--to-type",
        "project",
        "--to",
        "Fitness Plan",
    )

    code, out = _run(capsys, "--vault", str(chosen), "archive-resource", "Fitness Gear")

    assert code == 1
    assert "'Fitness Plan'" in out


# ---- a wikilink into a NESTED folder (journal/entries) proves VAULT_DIR itself is ----
# patched, not just the flat folders: `_link_display`'s fallback (`<parent name>/<stem>`)
# would be indistinguishable from the correct value for a single-level folder, but not
# for a two-level one.


def test_a_links_wikilink_into_a_nested_folder_resolves_under_the_chosen_vault(capsys, chosen, sentinel):
    _run(capsys, "--vault", str(chosen), "create-project", "Fitness Plan")
    _run(capsys, "--vault", str(chosen), "create-journal-entry", "Kickoff")

    code, out = _run(
        capsys,
        "--vault",
        str(chosen),
        "link",
        "--from-type",
        "project",
        "--from",
        "Fitness Plan",
        "--to-type",
        "journal-entry",
        "--to",
        "Kickoff",
    )

    assert code == 0
    note = (chosen / "projects" / "fitness-plan.md").read_text(encoding="utf-8")
    assert "journal/entries/kickoff" in note, "the fallback (entries/kickoff) would be wrong, not just different"


# ---- --vault is optional: today's behaviour is unchanged when it is left out --------


def test_without_vault_writes_still_go_to_the_default_location(capsys, sentinel):
    code, out = _run(capsys, "create-project", "Test Title")

    assert code == 0
    assert (sentinel / "projects" / "test-title.md").exists()


# ---- every patched constant is restored afterwards, success or failure --------------


def test_every_path_constant_is_restored_after_main_returns(capsys, chosen, sentinel):
    before = {name: getattr(paths, name) for name in LAYOUT}

    _run(capsys, "--vault", str(chosen), "create-project", "Test Title")

    after = {name: getattr(paths, name) for name in LAYOUT}
    assert after == before


def test_every_path_constant_is_restored_even_if_the_command_raises(capsys, chosen, sentinel, monkeypatch):
    from ohtli import cli as cli_module

    before = {name: getattr(paths, name) for name in LAYOUT}

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "execute_capture", boom)

    with pytest.raises(RuntimeError):
        main(["--vault", str(chosen), "create-project", "Test Title"])

    after = {name: getattr(paths, name) for name in LAYOUT}
    assert after == before


# ---- refusing a bad --vault -----------------------------------------------------------


def test_a_missing_vault_directory_is_refused_and_writes_nothing(capsys, tmp_path, sentinel):
    missing = tmp_path / "nowhere"

    with pytest.raises(SystemExit) as raised:
        main(["--vault", str(missing), "create-project", "Test Title"])

    assert raised.value.code == 2
    assert not missing.exists()
    assert _files(sentinel) == []


def test_vault_placed_after_the_command_is_refused(capsys, chosen, sentinel):
    with pytest.raises(SystemExit) as raised:
        main(["create-project", "Test Title", "--vault", str(chosen)])

    assert raised.value.code == 2
    assert _files(chosen) == []
    assert _files(sentinel) == []
