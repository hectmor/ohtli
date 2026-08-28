from ohtli.domain.project import Project


def test_project_has_stable_generated_identity():
    p1 = Project(title="Alpha")
    p2 = Project(title="Alpha")
    assert p1.id != p2.id, "two distinct instances must not share identity"


def test_project_identity_is_independent_of_title_comparison():
    p = Project(title="Alpha")
    assert p.id
    assert p.title == "Alpha"
