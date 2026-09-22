"""`append_under_heading`: adding text to an existing section of a note's body
without disturbing the sections around it.

Used by Processing's Update to add an Inbox entry's text to an existing
object's landing section (`## Notes`, `## Discussion` for Meeting).
"""

import re

import pytest

from ohtli.execution.specs import ALL_SPECS
from ohtli.representation.notes import append_under_heading

# (spec, the landing heading Update writes under) for all six types
CASES = [
    pytest.param(spec, "## Discussion" if spec.note_type == "meeting" else "## Notes", id=spec.note_type)
    for spec in ALL_SPECS
]


def _section(body, heading):
    """The exact text of one `## ` section: from its heading up to (not
    including) the next `## ` heading, or the end of the body."""
    start = body.index(heading)
    rest = body[start + len(heading) :]
    following = re.search(r"\n#{1,2} ", rest)
    end = start + len(heading) + (following.start() if following else len(rest))
    return body[start:end]


def _blank_body(spec):
    return spec.to_representation(spec.domain_type(title="Demo"))["body"]


@pytest.mark.parametrize("spec,heading", CASES)
def test_the_text_lands_inside_the_named_section_only(spec, heading):
    body = _blank_body(spec)
    other_headings = [h for h in re.findall(r"^## .+", body, re.MULTILINE) if h != heading]

    result = append_under_heading(body, heading, "New text.")

    assert "New text." in _section(result, heading)
    for other in other_headings:
        assert "New text." not in _section(result, other), f"leaked into {other}"


@pytest.mark.parametrize("spec,heading", CASES)
def test_every_other_heading_is_preserved_in_order(spec, heading):
    body = _blank_body(spec)
    before = re.findall(r"^## .+", body, re.MULTILINE)

    result = append_under_heading(body, heading, "New text.")

    assert re.findall(r"^## .+", result, re.MULTILINE) == before


@pytest.mark.parametrize("spec,heading", CASES)
def test_two_appends_both_land_in_order_without_clobbering_each_other(spec, heading):
    body = _blank_body(spec)

    once = append_under_heading(body, heading, "First.")
    twice = append_under_heading(once, heading, "Second.")

    section = _section(twice, heading)
    assert "First." in section and "Second." in section
    assert section.index("First.") < section.index("Second.")


@pytest.mark.parametrize("spec,heading", CASES)
def test_the_entrys_own_headings_are_nested_below_the_section(spec, heading):
    body = _blank_body(spec)

    result = append_under_heading(body, heading, "Text.\n# Carried\nmore.")

    assert "### Carried" in _section(result, heading)
    assert not re.search(r"^# Carried$", result, re.MULTILINE), (
        "an un-nested top-level heading would collide with the template"
    )


def test_a_missing_heading_is_added_at_the_end_with_the_text_instead_of_dropping_it():
    legacy = "# Legacy\n\n## Objective\nsomething.\n"

    result = append_under_heading(legacy, "## Notes", "Recovered.")

    assert "## Objective\nsomething." in result, "existing content must survive"
    assert "Recovered." in _section(result, "## Notes")


def test_repeated_calls_accumulate_even_when_the_heading_had_to_be_created():
    legacy = "# Legacy\n\n## Objective\n"

    once = append_under_heading(legacy, "## Notes", "First.")
    twice = append_under_heading(once, "## Notes", "Second.")

    section = _section(twice, "## Notes")
    assert "First." in section and "Second." in section
    assert section.index("First.") < section.index("Second.")


# ---- apply_update: append_under_heading composed with the `updated` bump ----------


def test_apply_update_bumps_updated_and_preserves_identity_and_everything_else():
    from datetime import date

    from ohtli.execution.specs import PROJECT
    from ohtli.representation.notes import apply_update

    rep = PROJECT.to_representation(PROJECT.domain_type(title="Demo"), today=date(2026, 1, 1))

    updated = apply_update(rep, heading="## Notes", entry_text="new info", today=date(2026, 3, 3))

    assert updated["properties"]["updated"] == "2026-03-03"
    for key in ("id", "status", "context", "created", "note_type"):
        assert updated["properties"][key] == rep["properties"][key], key
    assert updated["title"] == rep["title"]


def test_apply_update_defaults_today_when_not_given():
    from datetime import date

    from ohtli.execution.specs import PROJECT
    from ohtli.representation.notes import apply_update

    rep = PROJECT.to_representation(PROJECT.domain_type(title="Demo"), today=date(2026, 1, 1))

    updated = apply_update(rep, heading="## Notes", entry_text="new info")

    assert updated["properties"]["updated"] == date.today().isoformat()


def test_apply_update_places_the_text_under_the_named_heading_only():
    from datetime import date

    from ohtli.execution.specs import PROJECT
    from ohtli.representation.notes import apply_update

    rep = PROJECT.to_representation(PROJECT.domain_type(title="Demo"), today=date(2026, 1, 1))

    updated = apply_update(rep, heading="## Notes", entry_text="new info", today=date(2026, 3, 3))

    assert "new info" in _section(updated["body"], "## Notes")
    assert "new info" not in _section(updated["body"], "## References")


def test_apply_update_does_not_mutate_its_input():
    from datetime import date

    from ohtli.execution.specs import PROJECT
    from ohtli.representation.notes import apply_update

    rep = PROJECT.to_representation(PROJECT.domain_type(title="Demo"), today=date(2026, 1, 1))
    before = dict(rep["properties"])

    apply_update(rep, heading="## Notes", entry_text="new info", today=date(2026, 3, 3))

    assert rep["properties"] == before
