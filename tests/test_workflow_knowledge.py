from ohtli.workflow.knowledge import EXTERNALIZE_TARGETS, is_applicable, is_externalize_target


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
