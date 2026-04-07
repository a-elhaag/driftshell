COMMANDS_TABLE = """
CREATE TABLE IF NOT EXISTS commands (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    nl_query     TEXT NOT NULL,
    shell_command TEXT NOT NULL,
    risk_score   INTEGER,
    gate_decision TEXT,
    exit_code    INTEGER,
    stdout       TEXT,
    stderr       TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

SNAPSHOTS_TABLE = """
CREATE TABLE IF NOT EXISTS snapshots (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id       INTEGER REFERENCES commands(id),
    file_path        TEXT NOT NULL,
    original_hash    TEXT NOT NULL,
    original_content BLOB NOT NULL,
    diff_content     TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'active',
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

AUDIT_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS audit_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    detail     TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

USAGE_COUNTERS_TABLE = """
CREATE TABLE IF NOT EXISTS usage_counters (
    date           TEXT PRIMARY KEY,
    command_count  INTEGER NOT NULL DEFAULT 0,
    exec_count     INTEGER NOT NULL DEFAULT 0,
    snapshot_count INTEGER NOT NULL DEFAULT 0
)
"""

SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS _schema_version (
    version INTEGER PRIMARY KEY
)
"""

ALL_TABLES = [
    SCHEMA_VERSION_TABLE,
    COMMANDS_TABLE,
    SNAPSHOTS_TABLE,
    AUDIT_LOG_TABLE,
    USAGE_COUNTERS_TABLE,
]
