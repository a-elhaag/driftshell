from __future__ import annotations

from datetime import datetime

from driftshell.db import get_connection
from driftshell.models.schemas import CommandRecord, GateDecision


def save(record: CommandRecord) -> int:
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO commands
            (nl_query, shell_command, risk_score, gate_decision, exit_code, stdout, stderr)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.nl_query,
            record.shell_command,
            record.risk_score,
            record.gate_decision.value if record.gate_decision else None,
            record.exit_code,
            record.stdout,
            record.stderr,
        ),
    )
    return cur.lastrowid


def get_recent(n: int) -> list[CommandRecord]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM commands ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    result = []
    for row in reversed(rows):
        result.append(
            CommandRecord(
                id=row["id"],
                nl_query=row["nl_query"],
                shell_command=row["shell_command"],
                risk_score=row["risk_score"],
                gate_decision=GateDecision(row["gate_decision"]) if row["gate_decision"] else None,
                exit_code=row["exit_code"],
                stdout=row["stdout"],
                stderr=row["stderr"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        )
    return result
