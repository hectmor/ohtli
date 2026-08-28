from ohtli.workflow import capture


def test_capture_is_applicable_when_title_is_new():
    assert capture.is_applicable("New Project", existing_titles=set())


def test_capture_is_not_applicable_when_title_already_exists():
    assert not capture.is_applicable("Existing", existing_titles={"Existing"})


def test_capture_transform_produces_a_project_with_matching_title():
    project = capture.transform("New Project")
    assert project.title == "New Project"
    assert project.id
