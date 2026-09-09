from ohtli.workflow import archive


def test_archive_is_applicable_when_operational():
    assert archive.is_applicable("operational")


def test_archive_is_not_applicable_when_historical():
    assert not archive.is_applicable("historical")


def test_reactivate_is_applicable_when_historical():
    assert archive.is_reactivate_applicable("historical")


def test_reactivate_is_not_applicable_when_operational():
    assert not archive.is_reactivate_applicable("operational")
