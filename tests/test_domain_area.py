from ohtli.domain.area import Area


def test_area_has_stable_generated_identity():
    a1 = Area(title="Health")
    a2 = Area(title="Health")
    assert a1.id != a2.id, "two distinct instances must not share identity"


def test_area_identity_is_independent_of_title_comparison():
    a = Area(title="Health")
    assert a.id
    assert a.title == "Health"
