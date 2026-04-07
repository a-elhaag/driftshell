from __future__ import annotations

import typer
from rich.table import Table

from driftshell.snapshots import restore as restore_mod
from driftshell.utils.console import console, print_error, print_success, print_warning

app = typer.Typer()


@app.command()
def undo(
    index: int = typer.Option(None, "--index", "-i", help="Index of snapshot to undo (1-based)"),
) -> None:
    """Roll back the last destructive command(s) using stored snapshots.
    
    If no index is provided, shows an interactive menu to choose which snapshot to restore.
    """
    groups = restore_mod.get_latest_snapshots(limit=20)

    if not groups:
        print_warning("No snapshots available to undo.")
        raise typer.Exit(0)

    # If index provided, use it directly
    if index is not None:
        if index < 1 or index > len(groups):
            print_error(f"Invalid index. Choose between 1 and {len(groups)}")
            raise typer.Exit(1)
        selected_group = groups[index - 1]
    else:
        # Show interactive menu
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Command", min_width=40)
        table.add_column("When", width=20)
        
        for i, group in enumerate(groups, 1):
            # Assuming group has some metadata, adjust based on actual structure
            when_str = getattr(group, 'created_at', 'unknown')
            cmd_str = getattr(group, 'shell_command', 'snapshot')
            table.add_row(str(i), cmd_str[:40], str(when_str)[:20])
        
        console.print(table)
        console.print()
        
        try:
            choice = console.input("[bold cyan]Enter snapshot number to undo[/bold cyan] (or 'q' to cancel): ").strip()
            if choice.lower() in ('q', 'quit', 'exit'):
                console.print("[dim]Cancelled.[/dim]")
                raise typer.Exit(0)
            
            index = int(choice)
            if index < 1 or index > len(groups):
                print_error(f"Invalid choice. Choose between 1 and {len(groups)}")
                raise typer.Exit(1)
            selected_group = groups[index - 1]
        except ValueError:
            print_error("Please enter a valid number")
            raise typer.Exit(1)

    # Restore the selected snapshot
    try:
        restored = restore_mod.restore(selected_group)
        for path in restored:
            print_success(f"Restored: {path}")
    except restore_mod.RestoreError as e:
        print_error(str(e))
        raise typer.Exit(1)
