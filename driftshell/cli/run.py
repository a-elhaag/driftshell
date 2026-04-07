from __future__ import annotations

import typer

from driftshell.core import orchestrator
from driftshell.core.nlu import NLUError
from driftshell.core.limiter import LimitExceededError
from driftshell.models.schemas import GateDecision
from driftshell.utils.console import (
    console,
    print_blocked,
    print_command,
    print_error,
    print_explain,
    print_output,
    print_risk,
    print_success,
    print_warning,
)

app = typer.Typer(invoke_without_command=True)


def _handle_query(query: str, explain: bool = False, dry_run: bool = False) -> None:
    """Core query handler used by both Typer CLI and REPL."""
    try:
        result = orchestrator.run(query, explain_mode=explain, dry_run=dry_run)
    except NLUError as e:
        print_error(str(e))
        return
    except LimitExceededError as e:
        print_warning(str(e))
        return

    print_command(result.command)

    if result.risk:
        print_risk(result.risk.score)

    if result.decision == GateDecision.BLOCKED:
        print_blocked("destructive pattern")
        return

    if result.decision == GateDecision.ABORTED:
        console.print("[dim]Aborted.[/dim]")
        return

    if result.explanation:
        print_explain(result.explanation)
        return

    if dry_run:
        console.print("[dim]Dry run — not executed.[/dim]")
        return

    if result.execution:
        print_output(result.execution.stdout, result.execution.stderr, result.execution.exit_code)
        if result.execution.timed_out:
            print_warning("Command timed out.")
        elif result.execution.exit_code == 0:
            print_success("Done.")


@app.callback(invoke_without_command=True)
def run(
    query: str = typer.Argument(..., help="Plain English description of what you want to do"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Show explanation without executing"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show command without executing"),
) -> None:
    """Convert plain English to a shell command and run it."""
    _handle_query(query, explain=explain, dry_run=dry_run)
