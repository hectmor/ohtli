from ohtli.domain.area import Area
from ohtli.workflow import processing


def test_processing_is_applicable_when_title_is_derivable_and_new():
    assert processing.is_applicable("New Idea\n\nSome notes.")


def test_processing_is_still_applicable_when_the_derived_title_already_exists():
    """A title collision no longer refuses Processing: it means Update
    instead of Create (`is_update`), not "not applicable"."""
    assert processing.is_applicable("Existing\n\nNotes.")


def test_processing_is_not_applicable_when_entry_has_no_content():
    assert not processing.is_applicable("\n   \n")


def test_processing_strips_markdown_heading_marks_from_derived_title():
    assert processing.is_applicable("# Website Relaunch\n\nNotes.")


def test_is_update_is_false_when_the_derived_title_is_new():
    assert not processing.is_update("New Idea\n\nSome notes.", existing_titles=set())


def test_is_update_is_true_when_the_derived_title_already_exists():
    assert processing.is_update("Existing\n\nNotes.", existing_titles={"Existing"})


def test_is_update_strips_markdown_heading_marks_from_the_derived_title_too():
    assert processing.is_update(
        "# Website Relaunch\n\nNotes.", existing_titles={"Website Relaunch"}
    )
    assert not processing.is_update("# Website Relaunch\n\nNotes.", existing_titles=set())


def test_is_update_is_false_for_a_blank_entry_even_if_the_title_would_collide():
    """A blank entry has no derivable title, so it cannot match anything in
    `existing_titles` — is_update is false, and is_applicable is false too,
    so it is refused rather than silently treated as an update."""
    assert not processing.is_update("\n   \n", existing_titles={"Anything"})


def test_processing_transform_produces_a_project_with_derived_title():
    project = processing.transform("Book Recommendation\n\nRead this.")
    assert project.title == "Book Recommendation"
    assert project.id


def test_processing_transform_uses_first_non_empty_line():
    project = processing.transform("\n\n  Meeting Notes  \nBody text.")
    assert project.title == "Meeting Notes"


def test_derive_notes_returns_everything_after_the_title():
    raw = "Redesign Onboarding\n\nUsers drop at step 3.\nWorth a project.\n"
    assert processing.derive_notes(raw) == "Users drop at step 3.\nWorth a project."


def test_derive_notes_is_none_when_entry_is_title_only():
    assert processing.derive_notes("Just A Title\n") is None
    assert processing.derive_notes("Just A Title\n\n   \n") is None


def test_derive_notes_is_none_when_entry_has_no_content():
    assert processing.derive_notes("\n   \n") is None


def test_derive_notes_skips_the_heading_line_it_took_the_title_from():
    raw = "# Heading Title\n\nBody after the heading.\n"
    assert processing.derive_notes(raw) == "Body after the heading."


def test_processing_transform_generalizes_to_a_different_domain_object():
    """Processing is a class of transformation, not a per-object
    function: the same `transform()` interprets an Inbox entry as an
    Area exactly as it does a Project, by passing a different
    domain_factory."""
    area = processing.transform("New Area\n\nOngoing responsibility.", domain_factory=Area)
    assert isinstance(area, Area)
    assert area.title == "New Area"
    assert area.id
