from __future__ import annotations

from driftshell.config.sealed import is_config_sealed, get_sealed_config
from driftshell.config.loader import get_config
from driftshell.db import get_connection


class LimitExceededError(Exception):
    pass


def _today() -> str:
    from datetime import date
    return date.today().isoformat()


def _ensure_row(conn, today: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO usage_counters (date) VALUES (?)", (today,)
    )


def get_today_counts() -> dict[str, int]:
    conn = get_connection()
    today = _today()
    _ensure_row(conn, today)
    row = conn.execute(
        "SELECT command_count, exec_count, snapshot_count FROM usage_counters WHERE date = ?",
        (today,),
    ).fetchone()
    return {
        "command_count": row["command_count"],
        "exec_count": row["exec_count"],
        "snapshot_count": row["snapshot_count"],
    }


def _get_config():
    """Get config (sealed if available, otherwise unsealed)."""
    if is_config_sealed():
        return get_sealed_config()
    return get_config()


def check_command_limit() -> None:
    cfg = _get_config()
    counts = get_today_counts()
    if counts["command_count"] >= cfg.daily_limit:
        raise LimitExceededError(
            f"Daily command limit reached ({cfg.daily_limit}/day). Resets at midnight."
        )


def check_exec_limit() -> None:
    cfg = _get_config()
    counts = get_today_counts()
    if counts["exec_count"] >= cfg.exec_limit:
        raise LimitExceededError(
            f"Daily auto-exec limit reached ({cfg.exec_limit}/day). Use --explain or confirm manually."
        )


def increment_command() -> None:
    conn = get_connection()
    today = _today()
    _ensure_row(conn, today)
    conn.execute(
        "UPDATE usage_counters SET command_count = command_count + 1 WHERE date = ?", (today,)
    )


def increment_exec() -> None:
    conn = get_connection()
    today = _today()
    _ensure_row(conn, today)
    conn.execute(
        "UPDATE usage_counters SET exec_count = exec_count + 1 WHERE date = ?", (today,)
    )


def increment_snapshot() -> None:
    conn = get_connection()
    today = _today()
    _ensure_row(conn, today)
    conn.execute(
        "UPDATE usage_counters SET snapshot_count = snapshot_count + 1 WHERE date = ?", (today,)
    )
