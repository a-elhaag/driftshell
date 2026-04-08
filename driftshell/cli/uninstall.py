"""
Uninstall command — removes all Drift data from ~/.drift/ and prints
the package-manager command to remove the binary.

Nothing is written to shell profiles (.bashrc / .zshrc / etc.) by Drift.
This command only removes data that Drift itself created.
"""
from __future__ import annotations

import shutil
import typer

from driftshell.utils.console import console, print_success, print_warning
from driftshell.utils.paths import DRIFT_DIR

app = typer.Typer()


@app.command()
def uninstall(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Remove all Drift data and show how to uninstall the package."""
    console.print(
        "\n[bold]Drift Uninstall[/bold]\n\n"
        "This will permanently delete:\n"
        f"  • [cyan]{DRIFT_DIR}[/cyan]  (config, database, snapshots, audit log)\n"
    )

    if not yes:
        confirmed = typer.confirm("Continue?", default=False)
        if not confirmed:
            console.print("[dim]Aborted.[/dim]")
            raise typer.Exit()

    if DRIFT_DIR.exists():
        shutil.rmtree(DRIFT_DIR)
        print_success(f"Removed {DRIFT_DIR}")
    else:
        print_warning(f"{DRIFT_DIR} does not exist — nothing to remove.")

    console.print(
        "\nTo remove the [bold]drift[/bold] binary, run one of:\n\n"
        "  [cyan]pip uninstall driftshell[/cyan]          (if installed via pip)\n"
        "  [cyan]brew uninstall drift[/cyan]               (if installed via Homebrew)\n"
        "  [cyan]winget uninstall a-elhaag.driftshell[/cyan] (if installed via WinGet)\n\n"
        "[dim]Drift never modifies .bashrc, .zshrc, or any shell profile.[/dim]\n"
    )
