from ohtli.domain.area import Area
from ohtli.workflow import processing


def test_processing_is_applicable_when_title_is_derivable_and_new():
    assert processing.is_applicable("New Idea\n\nSome notes.", existing_titles=set())


def test_processing_is_not_applicable_when_derived_title_already_exists():
    assert not processing.is_applicable("Existing\n\nNotes.", existing_titles={"Existing"})


def test_processing_is_not_applicable_when_entry_has_no_content():
    assert not processing.is_applicable("\n   \n", existing_titles=set())


def test_processing_strips_markdown_heading_marks_from_derived_title():
    assert processing.is_applicable("# Website Relaunch\n\nNotes.", existing_titles=set())
    assert not processing.is_applicable(
        "# Website Relaunch\n\nNotes.", existing_titles={"Website Relaunch"}
    )


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
