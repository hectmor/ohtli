from pathlib import Path

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
    }


def test_only_relationships_the_interaction_model_defines_are_known():
    assert processing.relationship_definition("Project", "belongs to") is not None
    assert processing.relationship_definition("Project", "contains") is None, "Project contains Meeting is canonical but not implemented yet"
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
    assert processing.relationship_definition("Project", "references", "Journal Entry") is None, (
        "Project references Journal Entry is canonical but not implemented yet"
    )


def test_omitting_the_target_type_keeps_the_phase_22_lookup_working():
    assert processing.relationship_definition("Project", "belongs to").target_type == "Area"


def test_the_relationship_type_is_derived_from_the_ordered_pair():
    assert processing.relationship_for_pair("Project", "Area").relationship_type == "belongs to"
    assert processing.relationship_for_pair("Project", "Resource").relationship_type == "references"
    assert processing.relationship_for_pair("Project", "Reference").relationship_type == "references"
    assert processing.relationship_for_pair("Area", "Project") is None, "the inverse is not implemented"
    assert processing.relationship_for_pair("Project", "Meeting") is None


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
