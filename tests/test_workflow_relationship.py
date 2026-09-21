from pathlib import Path

from ohtli.execution import specs
from ohtli.workflow import processing


def test_the_canonical_table_holds_exactly_the_implemented_relationships():
    rows = {
        (d.source_type, d.relationship_type, d.target_type, d.max_targets)
        for d in processing.CANONICAL_RELATIONSHIPS
    }

    assert rows == {
        ("Project", "belongs to", "Area", 1),
        ("Project", "references", "Resource", None),
        ("Project", "references", "Reference", None),
        ("Project", "references", "JournalEntry", None),
        ("Resource", "references", "Reference", None),
        ("Meeting", "references", "Reference", None),
        ("Meeting", "references", "Resource", None),
        ("JournalEntry", "references", "Project", None),
        ("JournalEntry", "references", "Area", None),
        ("JournalEntry", "references", "Resource", None),
        ("Reference", "supports", "Project", None),
        ("Reference", "supports", "Resource", None),
        ("Resource", "supports", "Project", None),
        ("Meeting", "supports", "Project", 1),
        ("Project", "contains", "Meeting", None),
    }


def test_only_relationships_the_interaction_model_defines_are_known():
    assert processing.relationship_definition("Project", "belongs to") is not None
    assert processing.relationship_definition("Project", "contains") is not None
    assert processing.relationship_definition("Project", "supports") is None, "the Interaction Model defines no Project supports"
    assert processing.relationship_definition("Area", "belongs to") is None
    assert processing.relationship_definition("Project", "relates to") is None, "generic types are not allowed"


def test_relate_is_applicable_toward_the_defined_target_under_cardinality():
    definition = processing.relationship_definition("Project", "belongs to")

    assert processing.is_relate_applicable(definition, target_type="Area", existing_of_type=0)


def test_relate_is_refused_toward_any_other_target_type():
    definition = processing.relationship_definition("Project", "belongs to")

    assert not processing.is_relate_applicable(definition, target_type="Resource", existing_of_type=0)


def test_relate_is_refused_once_the_cardinality_is_reached():
    definition = processing.relationship_definition("Project", "belongs to")

    assert not processing.is_relate_applicable(definition, target_type="Area", existing_of_type=1)


def test_relate_is_refused_for_an_undefined_relationship():
    assert not processing.is_relate_applicable(None, target_type="Area", existing_of_type=0)


def test_unrelate_is_applicable_only_when_there_is_something_to_remove():
    definition = processing.relationship_definition("Project", "belongs to")

    assert processing.is_unrelate_applicable(definition, existing_of_type=1)
    assert not processing.is_unrelate_applicable(definition, existing_of_type=0)
    assert not processing.is_unrelate_applicable(None, existing_of_type=1)


def test_processing_still_imports_no_other_workflow():
    """Workflows are coordinated through system state, never by
    invoking each other (ADR / workflow-model)."""
    source = Path(processing.__file__).read_text(encoding="utf-8")

    for other in ("capture", "archive", "evaluation", "review", "knowledge"):
        assert f"workflow import {other}" not in source
        assert f"workflow.{other}" not in source


def test_a_relationship_type_with_several_targets_is_looked_up_by_target_type():
    resource = processing.relationship_definition("Project", "references", "Resource")
    reference = processing.relationship_definition("Project", "references", "Reference")

    assert resource.target_type == "Resource" and reference.target_type == "Reference"
    assert resource.max_targets is None and reference.max_targets is None
    assert processing.relationship_definition("Project", "references", "Meeting") is None, (
        "the Interaction Model defines no Project references Meeting (Project contains Meeting is a different relationship)"
    )


def test_omitting_the_target_type_keeps_the_phase_22_lookup_working():
    assert processing.relationship_definition("Project", "belongs to").target_type == "Area"


def test_the_relationship_type_is_derived_from_the_ordered_pair():
    assert processing.relationship_for_pair("Project", "Area").relationship_type == "belongs to"
    assert processing.relationship_for_pair("Project", "Resource").relationship_type == "references"
    assert processing.relationship_for_pair("Project", "Reference").relationship_type == "references"
    assert processing.relationship_for_pair("Area", "Project") is None, "Area contains Project is derived, never linkable"
    assert processing.relationship_for_pair("Project", "Meeting").relationship_type == "contains"
    assert processing.relationship_for_pair("Meeting", "Area") is None, "no relationship is defined between these types"


def test_every_ordered_pair_in_the_table_is_unique():
    """Deriving the type from the pair (and naming events "X Linked to Y")
    is only legitimate while each ordered pair has one relationship type.
    All 16 canonical relationships satisfy this today; a future row that
    breaks it must fail here rather than silently mislead."""
    pairs = [(d.source_type, d.target_type) for d in processing.CANONICAL_RELATIONSHIPS]

    assert len(pairs) == len(set(pairs))


def test_an_unbounded_relationship_accepts_many_targets():
    definition = processing.relationship_definition("Project", "references", "Resource")

    assert processing.is_relate_applicable(definition, target_type="Resource", existing_of_type=0)
    assert processing.is_relate_applicable(definition, target_type="Resource", existing_of_type=50)


def test_linking_the_same_target_twice_is_refused():
    definition = processing.relationship_definition("Project", "references", "Resource")

    assert not processing.is_relate_applicable(
        definition, target_type="Resource", existing_of_type=1, already_linked=True
    )


def test_unlinking_an_unbounded_relationship_requires_a_named_target():
    definition = processing.relationship_definition("Project", "references", "Resource")

    assert not processing.is_unrelate_applicable(definition, existing_of_type=2)
    assert processing.is_unrelate_applicable(
        definition, existing_of_type=2, target_named=True, target_linked=True
    )


def test_a_named_target_must_actually_be_linked():
    definition = processing.relationship_definition("Project", "references", "Resource")

    assert not processing.is_unrelate_applicable(
        definition, existing_of_type=2, target_named=True, target_linked=False
    )


def test_a_bounded_relationship_can_be_unlinked_with_or_without_naming_the_target():
    definition = processing.relationship_definition("Project", "belongs to", "Area")

    assert processing.is_unrelate_applicable(definition, existing_of_type=1)
    assert processing.is_unrelate_applicable(
        definition, existing_of_type=1, target_named=True, target_linked=True
    )


def test_every_implemented_references_relationship_is_unbounded():
    references = [d for d in processing.CANONICAL_RELATIONSHIPS if d.relationship_type == "references"]

    assert len(references) == 9
    assert all(d.max_targets is None for d in references)


def test_every_relationship_type_is_implemented():
    """All four relationship types the Interaction Model defines. `contains` is
    stored for `Project contains Meeting` and derived for `Area contains Project`."""
    implemented_types = {d.relationship_type for d in processing.CANONICAL_RELATIONSHIPS}
    implemented_types |= {d.relationship_type for d in processing.DERIVED_RELATIONSHIPS}

    assert implemented_types == {"belongs to", "references", "supports", "contains"}


def test_area_contains_project_is_derived_and_never_linkable():
    derived = processing.derived_relationship_for_pair("Area", "Project")

    assert derived is not None and derived.relationship_type == "contains"
    assert (derived.via.source_type, derived.via.relationship_type, derived.via.target_type) == (
        "Project",
        "belongs to",
        "Area",
    )
    assert processing.relationship_for_pair("Area", "Project") is None
    assert processing.relationship_definition("Area", "contains") is None


def test_project_contains_meeting_is_stored_not_derived():
    """The spec does not declare it complementary to `Meeting supports Project`."""
    assert processing.derived_relationship_for_pair("Project", "Meeting") is None
    definition = processing.relationship_for_pair("Project", "Meeting")
    assert (definition.relationship_type, definition.max_targets) == ("contains", None)


def test_a_derived_pair_is_never_also_a_stored_pair():
    stored = {(d.source_type, d.target_type) for d in processing.CANONICAL_RELATIONSHIPS}
    derived = {(d.source_type, d.target_type) for d in processing.DERIVED_RELATIONSHIPS}

    assert not stored & derived


def test_only_meeting_supports_project_is_bounded_to_one_target():
    supports = {
        (d.source_type, d.target_type): d.max_targets
        for d in processing.CANONICAL_RELATIONSHIPS
        if d.relationship_type == "supports"
    }

    assert supports == {
        ("Reference", "Project"): None,
        ("Reference", "Resource"): None,
        ("Resource", "Project"): None,
        ("Meeting", "Project"): 1,
    }


def test_a_bounded_supports_relationship_refuses_a_second_target():
    meeting = processing.relationship_definition("Meeting", "supports", "Project")

    assert processing.is_relate_applicable(meeting, target_type="Project", existing_of_type=0)
    assert not processing.is_relate_applicable(meeting, target_type="Project", existing_of_type=1)


def test_each_supports_pair_resolves_its_relationship_from_the_pair():
    for source, target in (
        ("Reference", "Project"),
        ("Reference", "Resource"),
        ("Resource", "Project"),
        ("Meeting", "Project"),
    ):
        definition = processing.relationship_for_pair(source, target)
        assert definition.relationship_type == "supports", f"{source} -> {target}"


def test_each_new_source_type_resolves_its_relationship_from_the_pair():
    for source, target in (
        ("Project", "JournalEntry"),
        ("Resource", "Reference"),
        ("Meeting", "Reference"),
        ("Meeting", "Resource"),
        ("JournalEntry", "Project"),
        ("JournalEntry", "Area"),
        ("JournalEntry", "Resource"),
    ):
        definition = processing.relationship_for_pair(source, target)
        assert (definition.relationship_type, definition.max_targets) == ("references", None), f"{source} -> {target}"


def test_every_type_name_in_the_table_is_a_real_domain_class_name():
    """Execution and the CLI look relationships up by `domain_type.__name__`
    (`JournalEntry`, not "Journal Entry"). A row spelled any other way is
    silently unreachable, so the table is checked against the real specs
    instead of against strings typed in the tests themselves."""
    real = {
        spec.domain_type.__name__
        for spec in (specs.PROJECT, specs.AREA, specs.RESOURCE, specs.REFERENCE, specs.MEETING, specs.JOURNAL_ENTRY)
    }
    used = {d.source_type for d in processing.CANONICAL_RELATIONSHIPS} | {
        d.target_type for d in processing.CANONICAL_RELATIONSHIPS
    }

    assert used <= real, f"not a Domain class name: {sorted(used - real)}"


_INTERACTION_MODEL = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "interaction-model"
_RELATIONSHIP_TYPES = {"belongs to", "references", "supports", "contains"}


def _spec_relationships():
    """Every relationship the Interaction Model documents define, read from the
    documents themselves (so this check cannot share a typo with the table).
    Returns {(source, type, target): max_targets}."""
    found = {}
    for path in sorted(_INTERACTION_MODEL.glob("*.md")):
        if path.name == "README.md":
            continue
        source = path.stem.title().replace("-", "")
        current = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line in _RELATIONSHIP_TYPES:
                current = line
            elif line.startswith("- ") and current is not None:
                name, _, cardinality = line[2:].partition(" (")
                found[(source, current, name.replace(" ", ""))] = 1 if cardinality.startswith("0..1") else None
            elif line.startswith("#"):
                current = None
    return found


def test_every_canonical_relationship_is_stored_or_derived():
    """Nothing the Interaction Model defines is left unimplemented, and the code
    defines nothing the Interaction Model does not."""
    spec = _spec_relationships()
    stored = {
        (d.source_type, d.relationship_type, d.target_type): d.max_targets
        for d in processing.CANONICAL_RELATIONSHIPS
    }
    derived = {(d.source_type, d.relationship_type, d.target_type) for d in processing.DERIVED_RELATIONSHIPS}

    assert len(spec) == 16, f"expected 16 canonical relationships in the Interaction Model, read {len(spec)}"
    assert set(stored) | derived == set(spec)
    assert not set(stored) & derived
    for key, max_targets in stored.items():
        assert spec[key] == max_targets, f"cardinality of {key} differs from the Interaction Model"
