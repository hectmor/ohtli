"""The two example Deterministic-actor trigger scripts under `scripts/`.

They must write only into the vault they are explicitly given with
`--vault`. Without it they refuse and exit 2 before touching anything.

`scripts/` is not a package, so each script is loaded by path. Every
directory the real vault would use (`paths.PROJECTS_DIR`, `INBOX_DIR`,
`EVENTS_DIR`) is redirected to a "sentinel" folder in `tmp_path`, so a script
that forgot an override would write there, visibly, instead of into the real
vault. The regression tests then assert the sentinels stayed empty.
"""

import importlib.util
from pathlib import Path

import pytest

from ohtli.vault_io import events, paths

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def capture():
    return _load("deterministic_trigger")


@pytest.fixture
def inbox_trigger():
    return _load("deterministic_inbox_trigger")


@pytest.fixture(autouse=True)
def sentinel(tmp_path, monkeypatch):
    """Stand-in for the real vault's default folders, with the real names."""
    root = tmp_path / "sentinel"
    for name, folder in (("PROJECTS_DIR", "projects"), ("INBOX_DIR", "inbox"), ("EVENTS_DIR", ".ohtli")):
        (root / folder).mkdir(parents=True)
        monkeypatch.setattr(paths, name, root / folder)
    return root


@pytest.fixture
def vault(tmp_path):
    """The vault the scripts are told to use, distinct from the sentinels."""
    root = tmp_path / "vault"
    for folder in ("projects", "inbox"):
        (root / folder).mkdir(parents=True)
    return root


def _files(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


def _events(vault):
    return events.read_events(events_dir=vault / ".ohtli")


# ---- capture ------------------------------------------------------------------------


def test_capture_writes_the_note_and_a_deterministic_event_into_the_given_vault(capture, vault, capsys):
    code = capture.main(["--vault", str(vault), "Nightly Report"])

    assert code == 0
    assert (vault / "projects" / "nightly-report.md").exists()
    assert [e.actor for e in _events(vault)] == ["deterministic"]
    assert capsys.readouterr().out.startswith("Captured Project 'Nightly Report'")


def test_capture_without_a_title_uses_the_default_title(capture, vault):
    assert capture.main(["--vault", str(vault)]) == 0

    assert (vault / "projects" / "deterministically-captured-project.md").exists()


def test_capture_of_an_existing_title_exits_one_and_adds_no_event(capture, vault, capsys):
    capture.main(["--vault", str(vault), "Nightly Report"])
    capsys.readouterr()

    code = capture.main(["--vault", str(vault), "Nightly Report"])

    assert code == 1
    assert len(_events(vault)) == 1
    assert capsys.readouterr().out == "Not applicable: a Project titled 'Nightly Report' already exists.\n"


def test_capture_without_vault_is_refused_and_writes_nothing_anywhere(capture, sentinel, tmp_path, capsys):
    with pytest.raises(SystemExit) as raised:
        capture.main(["Nightly Report"])

    assert raised.value.code == 2
    assert "--vault" in capsys.readouterr().err
    assert _files(tmp_path) == []


def test_capture_into_a_missing_directory_is_refused(capture, tmp_path, capsys):
    with pytest.raises(SystemExit) as raised:
        capture.main(["--vault", str(tmp_path / "nowhere")])

    assert raised.value.code == 2
    assert not (tmp_path / "nowhere").exists()
    assert _files(tmp_path) == []


def test_capture_never_writes_into_the_default_folders(capture, vault, sentinel, tmp_path):
    capture.main(["--vault", str(vault), "Nightly Report"])

    assert _files(sentinel) == []


# ---- inbox processing ---------------------------------------------------------------


def test_an_empty_inbox_exits_zero(inbox_trigger, vault, capsys):
    assert inbox_trigger.main(["--vault", str(vault)]) == 0
    assert capsys.readouterr().out == "Inbox is empty.\n"


def test_a_valid_entry_becomes_a_note_in_the_given_vault_and_leaves_the_inbox(inbox_trigger, vault, capsys):
    entry = vault / "inbox" / "idea.md"
    entry.write_text("Rewrite the backup job\n", encoding="utf-8")

    code = inbox_trigger.main(["--vault", str(vault)])

    assert code == 0
    assert (vault / "projects" / "rewrite-the-backup-job.md").exists()
    assert not entry.exists()
    assert [e.actor for e in _events(vault)] == ["deterministic"]
    assert capsys.readouterr().out.startswith("Processed Project 'Rewrite the backup job'")


def test_an_entry_that_does_not_apply_is_left_untouched(inbox_trigger, vault, capsys):
    entry = vault / "inbox" / "blank.md"
    entry.write_text("   \n", encoding="utf-8")

    code = inbox_trigger.main(["--vault", str(vault)])

    assert code == 0
    assert entry.read_text(encoding="utf-8") == "   \n"
    assert _events(vault) == []
    assert "Not applicable: 'blank.md' left untouched in Inbox." in capsys.readouterr().out


def test_inbox_without_vault_is_refused_and_the_default_inbox_is_untouched(inbox_trigger, sentinel, capsys):
    entry = sentinel / "inbox" / "idea.md"
    entry.write_text("Rewrite the backup job\n", encoding="utf-8")

    with pytest.raises(SystemExit) as raised:
        inbox_trigger.main([])

    assert raised.value.code == 2
    assert "--vault" in capsys.readouterr().err
    assert entry.read_text(encoding="utf-8") == "Rewrite the backup job\n"
    assert _files(sentinel) == ["inbox/idea.md"]


def test_inbox_into_a_missing_directory_is_refused(inbox_trigger, tmp_path):
    with pytest.raises(SystemExit) as raised:
        inbox_trigger.main(["--vault", str(tmp_path / "nowhere")])

    assert raised.value.code == 2


def test_inbox_reads_only_the_given_vaults_inbox_and_never_the_default_one(inbox_trigger, vault, sentinel):
    other = sentinel / "inbox" / "other.md"
    other.write_text("Something else\n", encoding="utf-8")
    (vault / "inbox" / "idea.md").write_text("Rewrite the backup job\n", encoding="utf-8")

    inbox_trigger.main(["--vault", str(vault)])

    assert other.read_text(encoding="utf-8") == "Something else\n"
    assert _files(sentinel) == ["inbox/other.md"]
    assert not (vault / "projects" / "something-else.md").exists()
