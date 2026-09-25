import pytest

from ohtli.domain.area import Area
from ohtli.workflow import capture


def test_capture_is_applicable_when_title_is_new():
    assert capture.is_applicable("New Project", existing_titles=set(), target_occupied=False)


def test_capture_is_not_applicable_when_title_already_exists():
    assert not capture.is_applicable("Existing", existing_titles={"Existing"}, target_occupied=False)


def test_capture_is_not_applicable_when_the_target_path_is_occupied():
    """A note is named by the slug of its title, so a new title can still land
    on a file that is already there: a hand-made note, or another title with
    the same slug. The title check alone cannot see that."""
    assert not capture.is_applicable("New Project", existing_titles=set(), target_occupied=True)


def test_an_occupied_target_refuses_regardless_of_the_title_check():
    assert not capture.is_applicable("Existing", existing_titles={"Existing"}, target_occupied=True)


def test_target_occupied_is_required_so_no_caller_can_forget_the_path_check():
    with pytest.raises(TypeError):
        capture.is_applicable("New Project", existing_titles=set())


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
