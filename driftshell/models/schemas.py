from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class GateDecision(str, Enum):
    AUTO_EXEC = "auto_exec"
    CONFIRMED = "confirmed"
    ABORTED = "aborted"
    BLOCKED = "blocked"


class HardwareProfile(BaseModel):
    vram_gb: float
    ram_gb: float
    selected_model: str


class CommandRecord(BaseModel):
    id: int | None = None
    nl_query: str
    shell_command: str
    risk_score: int | None = None
    gate_decision: GateDecision | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    created_at: datetime | None = None


class SnapshotMeta(BaseModel):
    id: int | None = None
    command_id: int | None = None
    file_path: str
    original_hash: str
    original_content: bytes
    diff_content: str
    status: str = "active"
    created_at: datetime | None = None


class RiskResult(BaseModel):
    score: int
    raw_response: str


class ExecutionResult(BaseModel):
    command: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class DriftConfig(BaseModel):
    memory_window: int = 10
    exec_timeout: int = 30
    daily_limit: int = 20
    exec_limit: int = 3
    snapshot_limit: int = 1
    model_override: str | None = None
    skip_scoring: bool = False
    vram_override: float | None = None
    plan: str = "free"  # "free", "pro", or "enterprise" (set by valid license)
    d_command_override: str | None = None  # Custom command for "d"
    license_key: str | None = None  # HMAC-signed license key (immutable)
