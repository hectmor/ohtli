import re
from datetime import date

from ohtli.domain.project import Project
from ohtli.representation.project import to_representation
from ohtli.representation.understanding import enrich

_UNDERSTANDING_HEADING_RE = re.compile(r"^## Understanding\s*$", re.MULTILINE)


def _rep():
    return to_representation(Project(title="Knowledge Target"), today=date(2026, 8, 25))


def test_enrich_creates_the_understanding_section():
    rep = enrich(
        _rep(),
        understanding_title="Why it was slow",
        understanding="The index was missing.",
        provenance=("Reference A",),
        today=date(2026, 9, 14),
    )

    assert "## Understanding" in rep["body"]
    assert "### Why it was slow" in rep["body"]
    assert "The index was missing." in rep["body"]
    assert "Developed from: Reference A" in rep["body"]


def test_enrich_appends_a_second_entry_without_removing_the_first():
    once = enrich(
        _rep(),
        understanding_title="First Finding",
        understanding="First understanding.",
        provenance=("Source A",),
        today=date(2026, 9, 14),
    )
    twice = enrich(
        once,
        understanding_title="Second Finding",
        understanding="Second understanding.",
        provenance=("Source B",),
        today=date(2026, 9, 15),
    )

    assert twice["body"].count("## Understanding") == 1, "the section heading must not be duplicated"
    assert "First understanding." in twice["body"]
    assert "Second understanding." in twice["body"]
    assert "### First Finding" in twice["body"]
    assert "### Second Finding" in twice["body"]


def test_enrich_does_not_disturb_existing_sections():
    rep = _rep()
    enriched = enrich(
        rep,
        understanding_title="Finding",
        understanding="Text.",
        provenance=("Source",),
        today=date(2026, 9, 14),
    )

    assert "## Objective" in enriched["body"]
    assert "## References" in enriched["body"]


def test_enrich_only_changes_body_and_updated():
    rep = _rep()
    enriched = enrich(
        rep,
        understanding_title="Finding",
        understanding="Text.",
        provenance=("Source",),
        today=date(2026, 9, 14),
    )

    assert enriched["properties"]["updated"] == "2026-09-14"
    assert enriched["properties"]["status"] == rep["properties"]["status"]
    assert enriched["properties"]["context"] == rep["properties"]["context"]
    assert enriched["properties"]["id"] == rep["properties"]["id"]
    assert enriched["title"] == rep["title"]


def test_enrich_does_not_mutate_the_original_representation():
    rep = _rep()
    enrich(rep, understanding_title="F", understanding="T", provenance=("S",), today=date(2026, 9, 14))

    assert "## Understanding" not in rep["body"], "enrich() must not mutate its input"


def test_enrich_nests_headings_inside_the_understanding_text():
    rep = enrich(
        _rep(),
        understanding_title="Finding",
        understanding="## A heading inside the understanding",
        provenance=("Source",),
        today=date(2026, 9, 14),
    )

    assert "#### A heading inside the understanding" in rep["body"]


def test_enrich_creates_the_heading_even_when_notes_carries_a_similar_word():
    """A deeper heading like `### Understanding of the domain` (e.g.
    carried in from an Inbox entry under `## Notes`) must not be
    mistaken for the real `## Understanding` section — a naive
    substring check on "## Understanding" would match inside it.
    """
    rep = _rep()
    rep["body"] = rep["body"].replace(
        "## Notes\n", "## Notes\n### Understanding of the domain\nSome carried-in notes.\n"
    )

    enriched = enrich(
        rep,
        understanding_title="Real Finding",
        understanding="Actual developed understanding.",
        provenance=("Source",),
        today=date(2026, 9, 14),
    )

    assert len(_UNDERSTANDING_HEADING_RE.findall(enriched["body"])) == 1, (
        "exactly one real '## Understanding' heading must exist; the carried-in "
        "'### Understanding of the domain' heading must not be mistaken for it"
    )
    assert "Actual developed understanding." in enriched["body"]
