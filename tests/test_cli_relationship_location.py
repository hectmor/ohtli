"""What the CLI tells the user when `link`/`unlink` (and the legacy
`link-project-to-area`/`unlink-project-from-area`) cannot find the source or
target note, or finds more than one that could be it (#162).

The prefix (`Not applicable: cannot {link,unlink} ...`) is unchanged for a
refusal with no reason -- the pre-existing Interaction Model refusals (both
must exist, cardinality, already/not linked). `ambiguous_title` and
`not_an_ohtli_note` add a sentence after it, the same shape as Processing
Update's `_inbox_reason` (#156), Knowledge's `_enrich_reason` (#160) and
Archive/Reactivate's `_archive_reason` (#161) -- each with its own wording,
and naming whichever end (`source`/`target`) was the problem.
"""

import pytest

from ohtli.cli import main
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


LINK_ARGS = ["--from-type", "project", "--from", "Source", "--to-type", "area", "--to", "Target"]
UNLINK_ARGS = ["--from-type", "project", "--from", "Source", "--to-type", "area", "--to", "Target"]


def test_an_ordinary_link_refusal_keeps_its_original_message(capsys, tmp_path):
    code, out = _run(capsys, "link", *LINK_ARGS)

    assert code == 1
    assert out == (
        "Not applicable: cannot link project 'Source' to area 'Target' (both must exist, "
        "it must not already be linked, and the cardinality must allow it).\n"
    )


def test_an_ordinary_unlink_refusal_keeps_its_original_message(capsys, tmp_path):
    code, out = _run(capsys, "unlink", *UNLINK_ARGS)

    assert code == 1
    assert out == (
        "Not applicable: cannot unlink project 'Source'. It must exist and be linked; "
        "a 0..* relationship also needs --to.\n"
    )


def test_legacy_link_project_to_area_refusal_keeps_its_original_message(capsys, tmp_path):
    code, out = _run(capsys, "link-project-to-area", "Source", "Target")

    assert code == 1
    assert out == (
        "Not applicable: cannot link Project 'Source' to Area 'Target' "
        "(both must exist, and a Project belongs to at most one Area).\n"
    )


def test_legacy_unlink_project_from_area_refusal_keeps_its_original_message(capsys, tmp_path):
    code, out = _run(capsys, "unlink-project-from-area", "Source")

    assert code == 1
    assert out == "Not applicable: Project 'Source' does not exist or belongs to no Area.\n"


def test_a_hand_made_source_is_refused_and_named_not_half_written(capsys, tmp_path):
    path = tmp_path / "projects" / "source.md"
    path.parent.mkdir(parents=True)
    before = b"---\ncontext: operational\n---\n\n# Source\n\nmine\n"
    path.write_bytes(before)
    assert _run(capsys, "create-area", "Target")[0] == 0

    code, out = _run(capsys, "link", *LINK_ARGS)

    assert code == 1
    assert out == (
        "Not applicable: cannot link project 'Source' to area 'Target' (both must exist, "
        f"it must not already be linked, and the cardinality must allow it). {path} is titled "
        "'Source' but is not an Ohtli Project note; it was left untouched.\n"
    )
    assert path.read_bytes() == before


def test_a_hand_made_target_is_refused_and_named(capsys, tmp_path):
    assert _run(capsys, "create-project", "Source")[0] == 0
    path = tmp_path / "areas" / "target.md"
    path.parent.mkdir(parents=True)
    before = b"---\ncontext: operational\n---\n\n# Target\n\nmine\n"
    path.write_bytes(before)

    code, out = _run(capsys, "link", *LINK_ARGS)

    assert code == 1
    assert out == (
        "Not applicable: cannot link project 'Source' to area 'Target' (both must exist, "
        f"it must not already be linked, and the cardinality must allow it). {path} is titled "
        "'Target' but is not an Ohtli Area note; it was left untouched.\n"
    )


def test_two_notes_with_the_source_title_refuse_as_ambiguous(capsys, tmp_path):
    directory = tmp_path / "projects"
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("---\nid: aaa\nnote_type: project\n---\n\n# Source\n\nfirst\n", encoding="utf-8")
    b.write_text("---\nid: bbb\nnote_type: project\n---\n\n# Source\n\nsecond\n", encoding="utf-8")
    assert _run(capsys, "create-area", "Target")[0] == 0

    code, out = _run(capsys, "link", *LINK_ARGS)

    assert code == 1
    assert out == (
        "Not applicable: cannot link project 'Source' to area 'Target' (both must exist, "
        "it must not already be linked, and the cardinality must allow it). 2 Project notes are "
        "titled 'Source' (a.md, b.md); rename all but one, then link again.\n"
    )
    assert a.read_text(encoding="utf-8").endswith("first\n")
    assert b.read_text(encoding="utf-8").endswith("second\n")


def test_two_notes_with_the_target_title_refuse_as_ambiguous_naming_the_area(capsys, tmp_path):
    assert _run(capsys, "create-project", "Source")[0] == 0
    directory = tmp_path / "areas"
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("---\nid: aaa\nnote_type: area\n---\n\n# Target\n\nfirst\n", encoding="utf-8")
    b.write_text("---\nid: bbb\nnote_type: area\n---\n\n# Target\n\nsecond\n", encoding="utf-8")

    code, out = _run(capsys, "link", *LINK_ARGS)

    assert code == 1
    assert out == (
        "Not applicable: cannot link project 'Source' to area 'Target' (both must exist, "
        "it must not already be linked, and the cardinality must allow it). 2 Area notes are "
        "titled 'Target' (a.md, b.md); rename all but one, then link again.\n"
    )


def test_an_ambiguous_unlink_source_says_unlink_again(capsys, tmp_path):
    directory = tmp_path / "projects"
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("---\nid: aaa\nnote_type: project\n---\n\n# Source\n\nfirst\n", encoding="utf-8")
    b.write_text("---\nid: bbb\nnote_type: project\n---\n\n# Source\n\nsecond\n", encoding="utf-8")
    assert _run(capsys, "create-area", "Target")[0] == 0

    code, out = _run(capsys, "unlink", *UNLINK_ARGS)

    assert code == 1
    assert "rename all but one, then unlink again." in out


def test_a_renamed_source_can_be_linked_then_unlinked_through_the_cli(capsys, tmp_path):
    assert _run(capsys, "create-project", "Source")[0] == 0
    assert _run(capsys, "create-area", "Target")[0] == 0
    (tmp_path / "projects" / "source.md").rename(tmp_path / "projects" / "renamed-source.md")

    code, out = _run(capsys, "link", *LINK_ARGS)
    assert code == 0 and out.startswith("Project Linked to Area")

    code, out = _run(capsys, "unlink", *UNLINK_ARGS)
    assert code == 0 and out.startswith("Project Unlinked from Area")


def test_a_renamed_target_can_be_linked_through_the_cli(capsys, tmp_path):
    assert _run(capsys, "create-project", "Source")[0] == 0
    assert _run(capsys, "create-area", "Target")[0] == 0
    (tmp_path / "areas" / "target.md").rename(tmp_path / "areas" / "renamed-target.md")

    code, out = _run(capsys, "link", *LINK_ARGS)

    assert code == 0 and out.startswith("Project Linked to Area")


def test_legacy_link_project_to_area_names_an_ambiguous_project(capsys, tmp_path):
    directory = tmp_path / "projects"
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("---\nid: aaa\nnote_type: project\n---\n\n# Source\n\nfirst\n", encoding="utf-8")
    b.write_text("---\nid: bbb\nnote_type: project\n---\n\n# Source\n\nsecond\n", encoding="utf-8")
    assert _run(capsys, "create-area", "Target")[0] == 0

    code, out = _run(capsys, "link-project-to-area", "Source", "Target")

    assert code == 1
    assert "2 Project notes are titled 'Source'" in out
