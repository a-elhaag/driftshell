from __future__ import annotations

import sqlite3

import pytest


@pytest.fixture(autouse=True)
def isolated_drift_dir(tmp_path, monkeypatch):
    """Redirect all ~/.drift paths to a temp dir and wire a fresh DB for every test."""
    import driftshell.utils.paths as paths_mod
    import driftshell.db as db_mod
    import driftshell.memory.store as store_mod
    import driftshell.core.limiter as limiter_mod
    import driftshell.db.audit as audit_mod
    import driftshell.snapshots.capture as capture_mod
    import driftshell.snapshots.restore as restore_mod
    from driftshell.db.migrations import run as run_migrations

    drift_dir = tmp_path / ".drift"
    drift_dir.mkdir()
    snapshots_dir = drift_dir / "snapshots"
    snapshots_dir.mkdir()

    monkeypatch.setattr(paths_mod, "DRIFT_DIR", drift_dir)
    monkeypatch.setattr(paths_mod, "DB_PATH", drift_dir / "drift.db")
    monkeypatch.setattr(paths_mod, "SNAPSHOTS_DIR", snapshots_dir)
    monkeypatch.setattr(paths_mod, "CONFIG_PATH", drift_dir / "config.toml")

    # Build a fresh in-memory-style connection and run migrations on it
    db_mod.get_connection.cache_clear()
    conn = sqlite3.connect(str(drift_dir / "drift.db"), check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    run_migrations(conn)

    # Patch get_connection everywhere it's imported
    getter = lambda: conn  # noqa: E731
    monkeypatch.setattr(db_mod, "get_connection", getter)
    monkeypatch.setattr(store_mod, "get_connection", getter)
    monkeypatch.setattr(limiter_mod, "get_connection", getter)
    monkeypatch.setattr(audit_mod, "get_connection", getter)
    monkeypatch.setattr(capture_mod, "get_connection", getter)
    monkeypatch.setattr(restore_mod, "get_connection", getter)

    yield drift_dir


@pytest.fixture(autouse=True)
def clear_config_cache():
    from driftshell.config.loader import get_config
    get_config.cache_clear()
    yield
    get_config.cache_clear()


@pytest.fixture(autouse=True)
def clear_hardware_cache():
    from driftshell.core.hardware import get_hardware_profile
    get_hardware_profile.cache_clear()
    yield
    get_hardware_profile.cache_clear()
