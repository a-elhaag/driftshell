"""
First-time setup — auto-detects hardware and writes sane defaults.

  drift setup            → silent, no prompts (default)
  drift setup --interactive  → step-by-step wizard
"""
from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table

from driftshell.config.loader import get_config, set_config_value
from driftshell.core.hardware import (
    get_hardware_profile,
    MODEL_31B,
    MODEL_26B,
    MODEL_E4B,
)
from driftshell.utils.console import console, print_success, print_warning, print_logo

app = typer.Typer()

AVAILABLE_MODELS = [
    ("31b", MODEL_31B, "Largest model, best accuracy (16+ GB VRAM)"),
    ("26b", MODEL_26B, "Balanced model, good accuracy & speed (8+ GB VRAM)"),
    ("e4b", MODEL_E4B, "Small model, fast & lightweight (4+ GB VRAM)"),
]


def _apply_defaults(profile) -> None:
    """Write auto-detected defaults to config without any prompts."""
    set_config_value("plan", "free")
    set_config_value("daily_limit", 50)
    set_config_value("skip_scoring", False)
    # Only write model_override if user hasn't already set one
    cfg = get_config()
    if not cfg.model_override:
        set_config_value("model_override", None)  # keep auto-detection


@app.command()
def setup(
    interactive: bool = typer.Option(
        False, "--interactive", "-i",
        help="Run the step-by-step wizard instead of auto-configuring",
    ),
) -> None:
    """Configure Drift.

    By default runs silently — detects hardware and applies defaults.
    Pass --interactive for the step-by-step wizard.
    """
    print_logo()
    console.print()

    profile = get_hardware_profile()

    if not interactive:
        _apply_defaults(profile)

        # Show a compact summary table
        table = Table.grid(padding=(0, 2))
        table.add_column(style="dim")
        table.add_column()
        table.add_row("RAM",   f"{profile.ram_gb:.1f} GB")
        table.add_row("VRAM",  f"{profile.vram_gb:.1f} GB")
        table.add_row("Model", profile.selected_model)
        table.add_row("Plan",  "Free")
        table.add_row("Limits", "50 commands/day")

        console.print(
            Panel(
                table,
                title="[bold green]✓ Drift configured[/bold green]",
                border_style="green",
            )
        )
        console.print(
            "[dim]All settings stored in [cyan]~/.drift/config.toml[/cyan].\n"
            "Drift does not modify .bashrc, .zshrc, or any shell profile.\n"
            "Run [cyan]drift setup --interactive[/cyan] to customise.[/dim]\n"
        )
        return

    # ── Interactive wizard ────────────────────────────────────────────────────
    console.print(
        Panel.fit(
            "[bold]Welcome to Drift[/bold]\n\n"
            "Plain English → shell commands, powered by local LLMs",
            border_style="cyan",
        )
    )
    console.print()

    # Step 1: Hardware
    console.print("[bold]Step 1: Hardware Detection[/bold]")
    console.print(f"  RAM:   {profile.ram_gb:.1f} GB")
    console.print(f"  VRAM:  {profile.vram_gb:.1f} GB")
    console.print(f"  Auto-selected model: {profile.selected_model}")
    console.print()

    cfg = get_config()

    # Step 2: Model
    console.print("[bold]Step 2: Model Selection[/bold]")
    for i, (short_name, full_name, description) in enumerate(AVAILABLE_MODELS, 1):
        console.print(f"  {i}. [cyan]{short_name}[/cyan] — {full_name}")
        console.print(f"     {description}")
    console.print()

    model_choice = console.input(
        "Select model (1-3) or press Enter to keep auto-detected: "
    ).strip()

    if model_choice in ("1", "2", "3"):
        selected_model = AVAILABLE_MODELS[int(model_choice) - 1][1]
        set_config_value("model_override", selected_model)
        print_success(f"Model set to {selected_model}")
        get_hardware_profile.cache_clear()
    elif model_choice:
        print_warning(f"Invalid choice '{model_choice}', keeping auto-detection")

    console.print()

    # Step 3: Plan
    console.print("[bold]Step 3: Plan Selection[/bold]")
    console.print("  [cyan]1. Free[/cyan]  — 50 commands/day, standard risk scoring")
    console.print("  [dim cyan]2. Pro[/dim cyan]  [drift.amber](Coming Soon)[/drift.amber] — unlimited commands, custom safety settings")
    console.print()

    plan_choice = console.input(
        "Select plan (1, default: 1): "
    ).strip()

    if plan_choice == "2":
        print_warning("Pro plan is coming soon! Using Free for now.")

    set_config_value("plan", "free")
    set_config_value("daily_limit", 50)
    print_success("Free plan selected")

    get_config.cache_clear()
    console.print()

    # Step 4: Risk scoring
    console.print("[bold]Step 4: Feature Configuration[/bold]")
    skip_scoring = console.input(
        "Skip risk scoring for faster responses? (y/n, default: n): "
    ).strip().lower()

    if skip_scoring in ("y", "yes"):
        set_config_value("skip_scoring", True)
        print_success("Risk scoring disabled")
    else:
        set_config_value("skip_scoring", False)
        print_success("Risk scoring enabled")

    console.print()

    console.print(
        Panel.fit(
            "[bold green]✓ Setup Complete![/bold green]\n\n"
            "All settings saved to [cyan]~/.drift/config.toml[/cyan]\n"
            "[dim]Drift does not modify .bashrc, .zshrc, or any shell profile.[/dim]\n\n"
            "  [cyan]drift[/cyan]            — interactive REPL\n"
            "  [cyan]d 'list files'[/cyan]   — one-shot query\n"
            "  [cyan]drift settings[/cyan]   — change settings anytime\n"
            "  [cyan]drift uninstall[/cyan]  — remove all Drift data",
            border_style="green",
        )
    )
