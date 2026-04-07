from __future__ import annotations

import typer
from rich.table import Table

from driftshell.memory.store import get_recent
from driftshell.utils.console import console

app = typer.Typer()


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of commands to show"),
    search: str = typer.Option("", "--search", "-s", help="Fuzzy search term"),
) -> None:
    """Show command history."""
    records = get_recent(limit)

    if search:
        from thefuzz import process
        queries = [r.nl_query for r in records]
        matches = process.extract(search, queries, limit=limit)
        matched_queries = {m[0] for m in matches if m[1] >= 50}
        records = [r for r in records if r.nl_query in matched_queries]

    if not records:
        console.print("[dim]No history found.[/dim]")
        raise typer.Exit(0)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("Query", min_width=20)
    table.add_column("Command", min_width=30)
    table.add_column("Risk", width=5)
    table.add_column("Exit", width=5)
    table.add_column("When", width=20)

    for i, rec in enumerate(reversed(records), 1):
        risk_str = str(rec.risk_score) if rec.risk_score is not None else "-"
        exit_str = str(rec.exit_code) if rec.exit_code is not None else "-"
        when_str = rec.created_at.strftime("%Y-%m-%d %H:%M") if rec.created_at else "-"
        table.add_row(str(i), rec.nl_query, rec.shell_command, risk_str, exit_str, when_str)

    console.print(table)
