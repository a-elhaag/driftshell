"""
The 'd' command: same as 'drift'.
Usage: d         (interactive mode, same as "drift")
       d "list files"  (one-shot query)
"""
from __future__ import annotations

import typer

from driftshell.cli.run import _handle_query
from driftshell.core.nlu import NLUError
from driftshell.core.limiter import LimitExceededError
from driftshell.utils.console import print_error, print_warning

app = typer.Typer(help="Same as 'drift': interactive mode or one-shot query")


@app.callback(invoke_without_command=True)
def d_command(
    ctx: typer.Context,
    args: list[str] = typer.Argument(None, help="Plain English command (words joined together)"),
    explain: bool = typer.Option(False, "--explain", "-e"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """Same as 'drift': enter interactive mode or run a one-shot query.

    Usage:
      d              → enter REPL mode (or run override if configured)
      d ls           → one-shot query (list files)
      d ls -la       → with flags

    Can be overridden with: drift settings set d_command_override "ls"
    """
    # Bootstrap Drift (same as drift)
    from driftshell.utils.paths import ensure_dirs
    from driftshell.db import get_connection
    from driftshell.db.migrations import run as run_migrations
    from driftshell.core.hardware import get_hardware_profile
    from driftshell.core.ollama_daemon import ensure_ollama
    from driftshell.config.loader import get_config

    ensure_dirs()
    conn = get_connection()
    run_migrations(conn)
    profile = get_hardware_profile()
    ensure_ollama(profile.selected_model)

    if args:
        # One-shot query: join args into a single query string
        query = " ".join(args)
        try:
            _handle_query(query, explain=explain, dry_run=dry_run)
        except NLUError as e:
            print_error(str(e))
            raise typer.Exit(1)
        except LimitExceededError as e:
            print_warning(str(e))
            raise typer.Exit(1)
    else:
        # No args provided: check for override, otherwise enter REPL
        cfg = get_config()
        if cfg.d_command_override:
            # Run the override command
            try:
                _handle_query(cfg.d_command_override, explain=explain, dry_run=dry_run)
            except NLUError as e:
                print_error(str(e))
                raise typer.Exit(1)
            except LimitExceededError as e:
                print_warning(str(e))
                raise typer.Exit(1)
        else:
            # No override, enter REPL mode (same as "drift")
            from driftshell.cli.repl import start_repl
            start_repl()


@app.command("model")
def d_switch_model(
    model: str = typer.Argument(None, help="Model to switch to (31b, 26b, e4b, or 'auto')"),
) -> None:
    """Quick model switching: d model 31b"""
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

