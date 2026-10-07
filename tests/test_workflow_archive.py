import pytest

from ohtli.workflow import archive


def test_archive_is_applicable_when_operational():
    assert archive.is_applicable("operational")


def test_archive_is_not_applicable_when_historical():
    assert not archive.is_applicable("historical")


def test_reactivate_is_applicable_when_historical():
    assert archive.is_reactivate_applicable("historical")


def test_reactivate_is_not_applicable_when_operational():
    assert not archive.is_reactivate_applicable("operational")


def test_the_target_is_located_when_exactly_one_note_carries_the_title():
    assert archive.is_target_located(matches=1)


def test_the_target_is_not_located_when_no_note_carries_the_title():
    """The title exists only in name: a hand-made file, or a note of a
    different type. Nothing of the right kind to archive or reactivate."""
    assert not archive.is_target_located(matches=0)


def test_the_target_is_not_located_when_more_than_one_note_carries_the_title():
    """Ambiguous: Archive/Reactivate must not guess which note to transition."""
    assert not archive.is_target_located(matches=2)


def test_matches_is_required_to_locate_the_target():
    with pytest.raises(TypeError):
        archive.is_target_located()
