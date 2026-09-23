"""`tests/conftest.py` keeps the real vault out of every test by default.

Deliberately no local fixture here: this file exercises the autouse fixture in
`conftest.py` itself, so it must not be able to hide a missing redirect.
"""

from ohtli.execution.execution import Actor, ExecutionRequest, execute_capture, write_area_dashboard
from ohtli.execution.specs import AREA
from ohtli.vault_io import paths

REAL_DASHBOARDS = paths.VAULT_DIR / "dashboards" / "areas"


def test_the_dashboards_folder_is_redirected_into_tmp_path(tmp_path):
    assert paths.AREA_DASHBOARDS_DIR != REAL_DASHBOARDS
    assert tmp_path in paths.AREA_DASHBOARDS_DIR.parents


def test_the_events_folder_is_redirected_into_tmp_path(tmp_path):
    assert tmp_path in paths.EVENTS_DIR.parents


def test_a_write_that_forgets_every_base_dir_but_the_areas_cannot_reach_the_real_vault(tmp_path):
    """The redirect is asserted BEFORE the write, so if `conftest.py` ever loses
    it this fails without having written anything to the real vault."""
    assert paths.AREA_DASHBOARDS_DIR != REAL_DASHBOARDS
    execute_capture(
        ExecutionRequest(title="Health", actor=Actor.HUMAN), spec=AREA, base_dir=tmp_path / "area", events_dir=tmp_path
    )

    result = write_area_dashboard(
        "Health", area_base_dir=tmp_path / "area", project_base_dir=tmp_path / "project"
    )

    assert result.outcome == "created"
    assert tmp_path in result.path.parents
    assert not REAL_DASHBOARDS.exists() or result.path.parent != REAL_DASHBOARDS
