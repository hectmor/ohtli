from ohtli.domain.meeting import Meeting


def test_meeting_has_stable_generated_identity():
    m1 = Meeting(title="Weekly Sync")
    m2 = Meeting(title="Weekly Sync")
    assert m1.id != m2.id, "two distinct instances must not share identity"


def test_meeting_identity_is_independent_of_title_comparison():
    m = Meeting(title="Weekly Sync")
    assert m.id
    assert m.title == "Weekly Sync"
