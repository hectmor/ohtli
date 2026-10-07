import pytest

from ohtli.workflow.evaluation import OperationalResult, is_applicable, is_target_located

_PROJECT_RESULTS = frozenset(
    {
        OperationalResult.PROGRESS,
        OperationalResult.OUTCOME_REACHED,
        OperationalResult.NO_EFFECTIVE_CHANGE,
        OperationalResult.DEGRADATION,
    }
)


def test_is_applicable_when_operational_and_result_allowed():
    assert is_applicable("operational", OperationalResult.PROGRESS, _PROJECT_RESULTS)


def test_is_not_applicable_when_historical():
    assert not is_applicable("historical", OperationalResult.PROGRESS, _PROJECT_RESULTS)


def test_is_not_applicable_when_result_not_allowed():
    area_results = frozenset({OperationalResult.MAINTENANCE, OperationalResult.DEGRADATION})
    assert not is_applicable("operational", OperationalResult.OUTCOME_REACHED, area_results)


def test_the_target_is_located_when_exactly_one_note_carries_the_title():
    assert is_target_located(matches=1)


def test_the_target_is_not_located_when_no_note_carries_the_title():
    assert not is_target_located(matches=0)


def test_the_target_is_not_located_when_more_than_one_note_carries_the_title():
    assert not is_target_located(matches=2)


def test_matches_is_required_to_locate_the_target():
    with pytest.raises(TypeError):
        is_target_located()
