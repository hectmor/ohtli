from __future__ import annotations

import pytest

from ohtli.vault_io import paths


@pytest.fixture(autouse=True)
def _isolate_events_dir(tmp_path, monkeypatch):
    """Never let a test's default `events_dir` touch the real vault's
    event log.

    Mirrors the `base_dir` isolation every test already uses, applied
    automatically so Phase 10-13 tests (which predate `events_dir` and
    don't pass it explicitly) don't need per-call-site edits.
    """
    monkeypatch.setattr(paths, "EVENTS_DIR", tmp_path / "events")
