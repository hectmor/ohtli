from ohtli.workflow.knowledge import is_applicable


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
