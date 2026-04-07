from __future__ import annotations

from pathlib import Path

from driftshell.db import get_connection
from driftshell.models.schemas import SnapshotMeta


class RestoreError(Exception):
    pass


def get_latest_snapshots(steps: int = 1) -> list[list[SnapshotMeta]]:
    """Return snapshots grouped by command_id, most recent first."""
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT DISTINCT command_id FROM snapshots
        WHERE status = 'active'
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (steps,),
    ).fetchall()

    groups = []
    for row in rows:
        cmd_id = row["command_id"]
        snap_rows = conn.execute(
            "SELECT * FROM snapshots WHERE command_id = ? AND status = 'active'",
            (cmd_id,),
        ).fetchall()
        group = [
            SnapshotMeta(
                id=r["id"],
                command_id=r["command_id"],
                file_path=r["file_path"],
                original_hash=r["original_hash"],
                original_content=r["original_content"],
                diff_content=r["diff_content"],
                status=r["status"],
            )
            for r in snap_rows
        ]
        groups.append(group)
    return groups


def restore(snapshots: list[SnapshotMeta]) -> list[str]:
    """Restore files from snapshots. Returns list of restored file paths."""
    conn = get_connection()
    restored = []

    for snap in snapshots:
        path = Path(snap.file_path)
        try:
            path.write_bytes(snap.original_content)
            conn.execute(
                "UPDATE snapshots SET status = 'restored' WHERE id = ?", (snap.id,)
            )
            restored.append(snap.file_path)
        except OSError as e:
            raise RestoreError(f"Failed to restore {snap.file_path}: {e}") from e

    return restored
