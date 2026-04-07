from __future__ import annotations

import subprocess

from driftshell.config.loader import get_config
from driftshell.models.schemas import ExecutionResult


def run(command: str) -> ExecutionResult:
    cfg = get_config()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=cfg.exec_timeout,
        )
        return ExecutionResult(
            command=command,
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            command=command,
            exit_code=-1,
            stdout="",
            stderr=f"Command timed out after {cfg.exec_timeout}s",
            timed_out=True,
        )
