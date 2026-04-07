from __future__ import annotations

import os

from driftshell.utils.console import console, print_repl_banner
from driftshell.cli.run import _handle_query


def start_repl() -> None:
    """Drop into interactive REPL loop with D > prompt."""
    print_repl_banner()

    while True:
        cwd = os.getcwd()
        try:
            # Prompt: d [~/current/dir] >
            query = console.input(
                f"[bold drift.blue]d[/bold drift.blue] [{cwd}] [bold drift.blue]>[/bold drift.blue] "
            )
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        query = query.strip()
        if not query or query.lower() in ("exit", "quit", "q"):
            console.print("[dim]Goodbye.[/dim]")
            break

        # Run through the normal pipeline
        _handle_query(query, explain=False, dry_run=False)
        console.print()  # blank line between commands
