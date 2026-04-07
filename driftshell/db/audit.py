from __future__ import annotations

from driftshell.db import get_connection


def log_event(event_type: str, detail: str | None = None) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (event_type, detail) VALUES (?, ?)",
        (event_type, detail),
    )
