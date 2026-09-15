from ohtli.domain.reference import Reference


def test_reference_has_stable_generated_identity():
    r1 = Reference(title="A Paper")
    r2 = Reference(title="A Paper")
    assert r1.id != r2.id, "two distinct instances must not share identity"


def test_reference_identity_is_independent_of_title_comparison():
    r = Reference(title="A Paper")
    assert r.id
    assert r.title == "A Paper"
