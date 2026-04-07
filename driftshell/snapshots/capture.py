from __future__ import annotations

import difflib
import hashlib
import re
import shlex
from pathlib import Path

from driftshell.config.loader import get_config
from driftshell.db import get_connection
from driftshell.models.schemas import SnapshotMeta


def _extract_file_paths(command: str) -> list[Path]:
    """Best-effort: extract existing file paths from command tokens."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    paths = []
    for token in tokens:
        # Skip flags
        if token.startswith("-"):
            continue
        p = Path(token).expanduser()
        if p.exists() and p.is_file():
            paths.append(p)
    return paths


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _is_write_touching(command: str) -> bool:
    write_verbs = re.compile(
        r"^(mv|cp|rm|touch|mkdir|rmdir|chmod|chown|sed|awk|tee|truncate|install|ln)\b",
        re.IGNORECASE,
    )
    redirect_re = re.compile(r">>?\s+\S+")
    stripped = command.strip()
    return bool(write_verbs.match(stripped) or redirect_re.search(stripped))


def capture(command: str, command_id: int | None = None) -> list[SnapshotMeta]:
    if not _is_write_touching(command):
        return []

    cfg = get_config()
    conn = get_connection()

    # Enforce max snapshot limit
    count = conn.execute("SELECT COUNT(*) FROM snapshots WHERE status = 'active'").fetchone()[0]
    if count >= cfg.snapshot_limit:
        # Delete the oldest active snapshot
        oldest = conn.execute(
            "SELECT id FROM snapshots WHERE status = 'active' ORDER BY created_at ASC LIMIT 1"
        ).fetchone()
        if oldest:
            conn.execute("DELETE FROM snapshots WHERE id = ?", (oldest["id"],))

    paths = _extract_file_paths(command)
    snapshots = []

    for path in paths:
        try:
            original_content = path.read_bytes()
            original_hash = hashlib.sha256(original_content).hexdigest()

            try:
                original_text = original_content.decode("utf-8")
                diff = "".join(
                    difflib.unified_diff(
                        original_text.splitlines(keepends=True),
                        [],
                        fromfile=str(path),
                        tofile="/dev/null",
                    )
                )
            except UnicodeDecodeError:
                diff = "<binary file>"

            cur = conn.execute(
                """
                INSERT INTO snapshots (command_id, file_path, original_hash, original_content, diff_content)
                VALUES (?, ?, ?, ?, ?)
                """,
                (command_id, str(path), original_hash, original_content, diff),
            )
            snapshots.append(
                SnapshotMeta(
                    id=cur.lastrowid,
                    command_id=command_id,
                    file_path=str(path),
                    original_hash=original_hash,
                    original_content=original_content,
                    diff_content=diff,
                )
            )
        except OSError:
            continue

    return snapshots
