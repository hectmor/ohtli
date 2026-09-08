from ohtli.domain.area import Area
from ohtli.workflow import capture


def test_capture_is_applicable_when_title_is_new():
    assert capture.is_applicable("New Project", existing_titles=set())


def test_capture_is_not_applicable_when_title_already_exists():
    assert not capture.is_applicable("Existing", existing_titles={"Existing"})


def test_capture_transform_produces_a_project_with_matching_title():
    project = capture.transform("New Project")
    assert project.title == "New Project"
    assert project.id


def test_capture_transform_generalizes_to_a_different_domain_object():
    """Capture is a class of transformation, not a per-object function:
    the same `transform()` preserves an Area exactly as it preserves a
    Project, by passing a different domain_factory."""
    area = capture.transform("New Area", domain_factory=Area)
    assert isinstance(area, Area)
    assert area.title == "New Area"
    assert area.id
