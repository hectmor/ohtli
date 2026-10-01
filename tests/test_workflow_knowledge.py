import pytest

from ohtli.workflow.knowledge import EXTERNALIZE_TARGETS, is_applicable, is_externalize_target, is_target_located


def test_is_applicable_when_understanding_and_provenance_are_non_empty():
    assert is_applicable("Something learned.", ("Reference A",))


def test_is_not_applicable_when_understanding_is_empty():
    assert not is_applicable("", ("Reference A",))


def test_is_not_applicable_when_understanding_is_only_whitespace():
    assert not is_applicable("   ", ("Reference A",))


def test_is_not_applicable_when_provenance_is_empty():
    assert not is_applicable("Something learned.", ())


def test_is_not_applicable_when_provenance_contains_only_blank_entries():
    assert not is_applicable("Something learned.", ("   ",))


def test_externalize_targets_are_exactly_project_area_and_resource():
    """`knowledge-workflow.md` names these three, each time without exception
    (Output, Domain Enrichment, Externalize). Reference, Meeting and Journal
    Entry are Knowledge inputs, never enrichment targets."""
    assert set(EXTERNALIZE_TARGETS) == {"Project", "Area", "Resource"}


def test_the_named_domain_objects_are_externalize_targets():
    assert all(is_externalize_target(name) for name in ("Project", "Area", "Resource"))


def test_the_other_domain_objects_are_not_externalize_targets():
    assert not any(is_externalize_target(name) for name in ("Reference", "Meeting", "JournalEntry"))


def test_an_unknown_type_name_is_not_an_externalize_target():
    assert not is_externalize_target("")
    assert not is_externalize_target("project"), "matching is on the Domain type name, case-sensitive"


def test_the_target_is_located_when_exactly_one_note_carries_the_title():
    assert is_target_located(matches=1)


def test_the_target_is_not_located_when_no_note_carries_the_title():
    """The title exists only in name: a hand-made file, or a note of a
    different type. Nothing of the right kind to enrich."""
    assert not is_target_located(matches=0)


def test_the_target_is_not_located_when_more_than_one_note_carries_the_title():
    """Ambiguous: Knowledge must not guess which note to enrich."""
    assert not is_target_located(matches=2)


def test_matches_is_required_to_locate_the_target():
    with pytest.raises(TypeError):
        is_target_located()
