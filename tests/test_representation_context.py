from datetime import date

from ohtli.domain.area import Area
from ohtli.domain.project import Project
from ohtli.representation.area import to_representation as area_to_representation
from ohtli.representation.context import HISTORICAL, OPERATIONAL, archive, reactivate
from ohtli.representation.project import to_representation as project_to_representation


def test_new_representations_default_to_operational_context():
    project_rep = project_to_representation(Project(title="P"), today=date(2026, 8, 25))
    area_rep = area_to_representation(Area(title="A"), today=date(2026, 8, 25))

    assert project_rep["properties"]["context"] == OPERATIONAL
    assert area_rep["properties"]["context"] == OPERATIONAL


def test_archive_changes_only_context_and_updated():
    rep = project_to_representation(Project(title="P"), today=date(2026, 8, 25))
    archived = archive(rep, today=date(2026, 9, 8))

    assert archived["properties"]["context"] == HISTORICAL
    assert archived["properties"]["updated"] == "2026-09-08"
    assert archived["properties"]["status"] == rep["properties"]["status"]
    assert archived["properties"]["id"] == rep["properties"]["id"]
    assert archived["title"] == rep["title"]
    assert archived["body"] == rep["body"]


def test_reactivate_is_the_inverse_of_archive():
    rep = project_to_representation(Project(title="P"), today=date(2026, 8, 25))
    archived = archive(rep, today=date(2026, 9, 8))
    reactivated = reactivate(archived, today=date(2026, 9, 9))

    assert reactivated["properties"]["context"] == OPERATIONAL
    assert reactivated["properties"]["status"] == rep["properties"]["status"]
    assert reactivated["properties"]["id"] == rep["properties"]["id"]


def test_archive_does_not_mutate_the_original_representation():
    rep = project_to_representation(Project(title="P"), today=date(2026, 8, 25))
    archive(rep, today=date(2026, 9, 8))

    assert rep["properties"]["context"] == OPERATIONAL, "archive() must not mutate its input"


def test_archive_works_identically_for_area():
    rep = area_to_representation(Area(title="A"), today=date(2026, 8, 25))
    archived = archive(rep, today=date(2026, 9, 8))

    assert archived["properties"]["context"] == HISTORICAL
    assert archived["properties"]["status"] == rep["properties"]["status"]
