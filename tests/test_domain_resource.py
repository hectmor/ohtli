from ohtli.domain.resource import Resource


def test_resource_has_stable_generated_identity():
    r1 = Resource(title="Guide")
    r2 = Resource(title="Guide")
    assert r1.id != r2.id, "two distinct instances must not share identity"


def test_resource_identity_is_independent_of_title_comparison():
    r = Resource(title="Guide")
    assert r.id
    assert r.title == "Guide"
