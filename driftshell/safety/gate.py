from __future__ import annotations

import typer

from driftshell.models.schemas import GateDecision, RiskResult

# Commands that may auto-execute without confirmation (prefix match, score < 3)
AUTO_EXEC_WHITELIST = {
    "ls",
    "cat",
    "find",
    "grep",
    "pwd",
    "git status",
    "git log",
    "git diff",
    "echo",
    "which",
    "whoami",
    "date",
    "uname",
    "df",
    "du",
    "env",
    "printenv",
    "head",
    "tail",
    "wc",
    "sort",
    "uniq",
}


def _is_whitelisted(command: str) -> bool:
    cmd = command.strip()
    for entry in AUTO_EXEC_WHITELIST:
        if cmd == entry or cmd.startswith(entry + " "):
            return True
    return False


def evaluate(command: str, risk: RiskResult) -> GateDecision:
    if risk.score >= 7:
        confirmed = typer.confirm(
            f"⚠️  Risk score {risk.score}/10. This command may be destructive. Run anyway?",
            default=False,
        )
        return GateDecision.CONFIRMED if confirmed else GateDecision.ABORTED

    if _is_whitelisted(command) and risk.score < 3:
        return GateDecision.AUTO_EXEC

    # Mid-range risk or unwhitelisted: ask user
    confirmed = typer.confirm(
        f"Run: {command!r}  (risk {risk.score}/10)?",
        default=True,
    )
    return GateDecision.CONFIRMED if confirmed else GateDecision.ABORTED
