from __future__ import annotations

from typing import Optional

import typer

from driftshell.cli import settings, history, status, undo, setup, license as license_cli

app = typer.Typer(
    name="drift",
    help="Plain English → shell commands, powered by local LLMs.",
    no_args_is_help=False,
)


def _bootstrap() -> None:
    from driftshell.utils.paths import ensure_dirs
    from driftshell.db import get_connection
    from driftshell.db.migrations import run as run_migrations
    from driftshell.core.hardware import get_hardware_profile
    from driftshell.core.ollama_daemon import ensure_ollama
    from driftshell.config.sealed import seal_config

    ensure_dirs()
    conn = get_connection()
    run_migrations(conn)

    profile = get_hardware_profile()
    ensure_ollama(profile.selected_model)

    # Seal config after bootstrap (prevents runtime limit edits)
    seal_config()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    args: list[str] = typer.Argument(None, help="Plain English command (words joined together)"),
    version: Optional[bool] = typer.Option(None, "--version", "-v", is_eager=True, help="Show version"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Show explanation without executing"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show command without executing"),
) -> None:
    if version:
        from driftshell import __version__
        from driftshell.utils.console import print_logo
        print_logo()
        typer.echo(f"drift {__version__}")
        raise typer.Exit()
    _bootstrap()

    # If args provided, run as one-shot query (e.g., "drift ls" → "ls")
    if args:
        query = " ".join(args)
        from driftshell.cli.run import _handle_query
        _handle_query(query, explain=explain, dry_run=dry_run)
        raise typer.Exit()

    # If no subcommand was invoked and no args, start the REPL
    if ctx.invoked_subcommand is None:
        from driftshell.cli.repl import start_repl
        start_repl()


@app.command("model")
def switch_model(
    model: str = typer.Argument(None, help="Model to switch to (31b, 26b, e4b, or 'auto')"),
) -> None:
    """Quick model switching: drift model 31b"""
    from driftshell.config.loader import set_config_value
    from driftshell.core.hardware import (
        MODEL_31B,
        MODEL_26B,
        MODEL_E4B,
        get_hardware_profile as ghp,
    )
    from driftshell.utils.console import console, print_error, print_success

    MODELS = {
        "31b": MODEL_31B,
        "26b": MODEL_26B,
        "e4b": MODEL_E4B,
    }

    if not model:
        # Show available models
        profile = ghp()
        console.print("[bold]Available Models:[/bold]")
        for short_name, full_name in MODELS.items():
            marker = "✓ " if full_name == profile.selected_model else "  "
            console.print(f"  {marker}[cyan]{short_name}[/cyan] - {full_name}")
        return

    model_lower = model.lower().strip()

    if model_lower == "auto":
        set_config_value("model_override", None)
        print_success("Model override cleared. Using auto-detection.")
        ghp.cache_clear()
    elif model_lower in MODELS:
        set_config_value("model_override", MODELS[model_lower])
        print_success(f"Model set to {MODELS[model_lower]}")
        ghp.cache_clear()
    else:
        print_error(f"Unknown model: {model_lower!r}")
        console.print("Available: 31b, 26b, e4b, auto")
        raise typer.Exit(1)


app.add_typer(undo.app, name="undo", help="Roll back the last destructive command(s).")
app.add_typer(history.app, name="history", help="Show command history.")
app.add_typer(settings.app, name="settings", help="View and manage settings & model selection.")
app.add_typer(status.app, name="status", help="Show system status.")
app.add_typer(setup.app, name="setup", help="Run first-time setup and onboarding.")
app.add_typer(license_cli.app, name="license", help="License and subscription management.")
