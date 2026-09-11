from ohtli.workflow.evaluation import OperationalResult, is_applicable

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
