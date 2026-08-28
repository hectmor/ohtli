"""End-to-end integration test for the full vertical slice.

Domain Object -> Workflow -> Applicability -> Execution -> Transformation
-> Representation -> Filesystem -> Reloaded Object

Exercised twice with different Actor kinds (Human via a CLI-equivalent
call, Deterministic via a plain script-equivalent call) to demonstrate
actor-neutrality: identical code path, different actor.
"""

from ohtli.execution.execution import Actor, ExecutionRequest, execute_capture
from ohtli.vault_io.markdown import read_project


def test_full_slice_human_actor(tmp_path):
    request = ExecutionRequest(title="Website Relaunch", actor=Actor.HUMAN)
    result = execute_capture(request, base_dir=tmp_path)

    assert result.applicable
    reloaded = read_project(result.path)
    assert reloaded["title"] == "Website Relaunch"
    assert reloaded["properties"]["id"] == result.project.id
    assert reloaded["properties"]["status"] == "planned"


def test_full_slice_deterministic_actor_same_code_path(tmp_path):
    request = ExecutionRequest(title="Scheduled Backup Audit", actor=Actor.DETERMINISTIC)
    result = execute_capture(request, base_dir=tmp_path)

    assert result.applicable
    reloaded = read_project(result.path)
    assert reloaded["title"] == "Scheduled Backup Audit"
    assert reloaded["properties"]["id"] == result.project.id


def test_human_and_deterministic_actors_produce_the_same_kind_of_result(tmp_path):
    human_result = execute_capture(
        ExecutionRequest(title="Actor Parity A", actor=Actor.HUMAN), base_dir=tmp_path
    )
    deterministic_result = execute_capture(
        ExecutionRequest(title="Actor Parity B", actor=Actor.DETERMINISTIC), base_dir=tmp_path
    )

    assert human_result.applicable == deterministic_result.applicable is True
    assert type(human_result.project) is type(deterministic_result.project)
