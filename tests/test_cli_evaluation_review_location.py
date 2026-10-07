"""What the CLI tells the user when `evaluate-*`/`review-*` cannot find the
note, or finds more than one that could be it (#163).

The prefix is unchanged for a refusal with no location reason: Evaluate's
`cannot be evaluated as '<result>'.` and Review's `does not exist.` (no
existing test pins the exact Review wording as "correct" for every case --
it is actively false for `ambiguous_title`/`not_an_ohtli_note`, which is
exactly what this fix corrects). `ambiguous_title` and `not_an_ohtli_note`
add a sentence after it, the same shape as Processing Update's
`_inbox_reason` (#156), Knowledge's `_enrich_reason` (#160),
Archive/Reactivate's `_archive_reason` (#161) and Relate/Unrelate's
`_relationship_reason` (#162) -- each with its own wording.
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


def test_an_ordinary_evaluate_refusal_keeps_its_original_message(capsys, tmp_path):
    code, out = _run(capsys, "evaluate-project", "Subject", "--result", "progress")

    assert code == 1
    assert out == "Not applicable: 'Subject' cannot be evaluated as 'progress'.\n"


def test_an_ordinary_review_refusal_keeps_its_original_message(capsys, tmp_path):
    code, out = _run(capsys, "review-project", "Subject")

    assert code == 1
    assert out == "Not applicable: 'Subject' does not exist.\n"


def test_a_hand_made_file_is_refused_and_named_for_evaluate(capsys, tmp_path):
    path = tmp_path / "projects" / "subject.md"
    path.parent.mkdir(parents=True)
    before = b"---\ncontext: operational\n---\n\n# Subject\n\nmine\n"
    path.write_bytes(before)

    code, out = _run(capsys, "evaluate-project", "Subject", "--result", "progress")

    assert code == 1
    assert out == (
        f"Not applicable: 'Subject' cannot be evaluated as 'progress'. {path} is titled "
        "'Subject' but is not an Ohtli Project note; it was left untouched.\n"
    )
    assert path.read_bytes() == before


def test_a_hand_made_file_is_refused_and_named_for_review(capsys, tmp_path):
    path = tmp_path / "projects" / "subject.md"
    path.parent.mkdir(parents=True)
    before = b"---\ncontext: operational\n---\n\n# Subject\n\nmine\n"
    path.write_bytes(before)

    code, out = _run(capsys, "review-project", "Subject")

    assert code == 1
    assert out == (
        f"Not applicable: 'Subject' cannot be reviewed. {path} is titled "
        "'Subject' but is not an Ohtli Project note; it was left untouched.\n"
    )
    assert path.read_bytes() == before


def test_two_notes_with_the_same_title_refuse_as_ambiguous_for_evaluate(capsys, tmp_path):
    directory = tmp_path / "projects"
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("---\nid: aaa\nnote_type: project\n---\n\n# Subject\n\nfirst\n", encoding="utf-8")
    b.write_text("---\nid: bbb\nnote_type: project\n---\n\n# Subject\n\nsecond\n", encoding="utf-8")

    code, out = _run(capsys, "evaluate-project", "Subject", "--result", "progress")

    assert code == 1
    assert out == (
        "Not applicable: 'Subject' cannot be evaluated as 'progress'. 2 Project notes are "
        "titled 'Subject' (a.md, b.md); rename all but one, then evaluate again.\n"
    )
    assert a.read_text(encoding="utf-8").endswith("first\n")
    assert b.read_text(encoding="utf-8").endswith("second\n")


def test_two_notes_with_the_same_title_refuse_as_ambiguous_for_review(capsys, tmp_path):
    directory = tmp_path / "projects"
    directory.mkdir(parents=True)
    a = directory / "a.md"
    b = directory / "b.md"
    a.write_text("---\nid: aaa\nnote_type: project\n---\n\n# Subject\n\nfirst\n", encoding="utf-8")
    b.write_text("---\nid: bbb\nnote_type: project\n---\n\n# Subject\n\nsecond\n", encoding="utf-8")

    code, out = _run(capsys, "review-project", "Subject")

    assert code == 1
    assert out == (
        "Not applicable: 'Subject' cannot be reviewed. 2 Project notes are "
        "titled 'Subject' (a.md, b.md); rename all but one, then review again.\n"
    )


def test_a_renamed_note_can_still_be_evaluated_through_the_cli(capsys, tmp_path):
    assert _run(capsys, "create-project", "Subject")[0] == 0
    renamed = tmp_path / "projects" / "renamed.md"
    (tmp_path / "projects" / "subject.md").rename(renamed)

    code, out = _run(capsys, "evaluate-project", "Subject", "--result", "progress")

    assert code == 0
    assert out.startswith("Evaluated 'Subject'")


def test_a_renamed_note_can_still_be_reviewed_through_the_cli(capsys, tmp_path):
    assert _run(capsys, "create-project", "Subject")[0] == 0
    renamed = tmp_path / "projects" / "renamed.md"
    (tmp_path / "projects" / "subject.md").rename(renamed)

    code, out = _run(capsys, "review-project", "Subject")

    assert code == 0
    assert out.startswith("Reviewed 'Subject'")
