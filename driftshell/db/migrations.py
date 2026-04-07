from __future__ import annotations

import sqlite3

from driftshell.db.schema import ALL_TABLES


def run(conn: sqlite3.Connection) -> None:
    for ddl in ALL_TABLES:
        conn.execute(ddl)

    current = conn.execute("SELECT version FROM _schema_version").fetchone()
    version = current["version"] if current else 0

    for migration_version, migration_fn in _MIGRATIONS:
        if migration_version > version:
            migration_fn(conn)
            if current:
                conn.execute("UPDATE _schema_version SET version = ?", (migration_version,))
            else:
                conn.execute("INSERT INTO _schema_version (version) VALUES (?)", (migration_version,))
            version = migration_version


def _migration_1(conn: sqlite3.Connection) -> None:
    """Initial schema — tables already created by ALL_TABLES above."""
    pass


_MIGRATIONS: list[tuple[int, object]] = [
    (1, _migration_1),
]
