from __future__ import annotations

import typer
from rich.table import Table

from driftshell.utils.console import console

app = typer.Typer()


@app.command()
def status() -> None:
    """Show hardware profile, selected model, usage, and Ollama connectivity."""
    from driftshell.config.loader import get_config
    from driftshell.core.hardware import get_hardware_profile
    from driftshell.core.limiter import get_today_counts
    from driftshell.utils.paths import CONFIG_PATH

    cfg = get_config()
    profile = get_hardware_profile()
    counts = get_today_counts()

    # Ollama connectivity
    try:
        import ollama
        ollama.list()
        ollama_status = "[green]connected[/green]"
    except Exception:
        ollama_status = "[red]unreachable[/red]"

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan")
    table.add_column("Value")

    # Plan (show free, pro coming soon)
    plan_display = f"{cfg.plan} [dim drift.amber](upgrade to Pro)[/dim drift.amber]" if cfg.plan == "free" else cfg.plan
    table.add_row("Plan", plan_display)
    
    table.add_row("Ollama", ollama_status)
    table.add_row("Model", profile.selected_model)
    table.add_row("RAM", f"{profile.ram_gb:.1f} GB")
    table.add_row("VRAM", f"{profile.vram_gb:.1f} GB")
    table.add_row("Config", str(CONFIG_PATH))
    table.add_row("Commands today", f"{counts['command_count']} / {cfg.daily_limit}")
    table.add_row("Auto-execs today", f"{counts['exec_count']} / {cfg.exec_limit}")
    table.add_row("Active snapshots", f"{counts['snapshot_count']} / {cfg.snapshot_limit}")

    console.print(table)
