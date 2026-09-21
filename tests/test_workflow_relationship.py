from pathlib import Path

from ohtli.workflow import processing


def test_the_canonical_table_has_exactly_the_first_slice():
    (definition,) = processing.CANONICAL_RELATIONSHIPS

    assert definition.source_type == "Project"
    assert definition.relationship_type == "belongs to"
    assert definition.target_type == "Area"
    assert definition.max_targets == 1


def test_only_relationships_the_interaction_model_defines_are_known():
    assert processing.relationship_definition("Project", "belongs to") is not None
    assert processing.relationship_definition("Project", "contains") is None, "inverse not defined here"
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
