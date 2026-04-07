from __future__ import annotations

import sqlite3
from functools import lru_cache

from driftshell.utils.paths import DB_PATH


@lru_cache(maxsize=1)
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
