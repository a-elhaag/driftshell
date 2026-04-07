"""
Settings and configuration management with model switching.
"""
from __future__ import annotations

import typer
from rich.table import Table

from driftshell.config.loader import get_config, set_config_value
from driftshell.core.hardware import (
    get_hardware_profile,
    MODEL_31B,
    MODEL_26B,
    MODEL_E4B,
)
from driftshell.utils.console import console, print_error, print_success

app = typer.Typer()

AVAILABLE_MODELS = [
    ("31b", MODEL_31B, "Largest model, best accuracy (16+ GB VRAM)"),
    ("26b", MODEL_26B, "Balanced model, good accuracy & speed (8+ GB VRAM)"),
    ("e4b", MODEL_E4B, "Small model, fast & lightweight (4+ GB VRAM)"),
]


@app.command("view")
def view_settings() -> None:
    """View all current settings."""
    cfg = get_config()
    profile = get_hardware_profile()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Setting", style="bold cyan")
    table.add_column("Value")

    # Plan (show free, pro coming soon)
    plan_display = f"{cfg.plan} [dim drift.amber](upgrade to Pro)[/dim drift.amber]" if cfg.plan == "free" else cfg.plan
    table.add_row("Plan", plan_display)
    
    table.add_row("Current Model", profile.selected_model)
    table.add_row("Model Override", str(cfg.model_override) if cfg.model_override else "None (auto-detect)")
    table.add_row("Daily Command Limit", str(cfg.daily_limit))
    table.add_row("Daily Auto-Exec Limit", str(cfg.exec_limit))
    table.add_row("Command Execution Timeout", f"{cfg.exec_timeout}s")
    table.add_row("Memory Window", f"{cfg.memory_window} commands")
    table.add_row("Snapshot Limit", str(cfg.snapshot_limit))
    table.add_row("Risk Threshold", str(cfg.risk_threshold) if hasattr(cfg, 'risk_threshold') else "N/A")
    table.add_row("Skip Scoring", str(cfg.skip_scoring))

    console.print(table)


@app.command("model")
def switch_model(
    model: str = typer.Argument(None, help="Model to switch to (31b, 26b, e4b, or 'auto')"),
) -> None:
    """Switch between available models or enable auto-detection.
    
    Models:
    - 31b: Largest, best accuracy (requires 16+ GB VRAM)
    - 26b: Balanced, good accuracy & speed (requires 8+ GB VRAM)
    - e4b: Small, fast & lightweight (requires 4+ GB VRAM)
    - auto: Automatic detection based on hardware
    """
    if not model:
        # Show available models
        profile = get_hardware_profile()
        config = get_config()
        
        console.print("[bold]Available Models:[/bold]")
        for short_name, full_name, description in AVAILABLE_MODELS:
            marker = "✓ " if full_name == profile.selected_model else "  "
            console.print(f"  {marker}[cyan]{short_name}[/cyan] - {full_name}")
            console.print(f"     {description}")
        
        console.print()
        if config.model_override:
            console.print(f"[dim]Currently using: {config.model_override} (override)[/dim]")
        else:
            console.print(f"[dim]Currently using: {profile.selected_model} (auto-detected)[/dim]")
        console.print()
        console.print("Usage: [cyan]drift settings model 31b[/cyan]")
        return

    # Parse model selection
    model_lower = model.lower().strip()
    
    if model_lower == "auto":
        # Reset to auto-detection
        set_config_value("model_override", None)
        print_success("Model override cleared. Using auto-detection.")
        # Clear the cached hardware profile
        from driftshell.core.hardware import get_hardware_profile as ghp
        ghp.cache_clear()
        new_profile = get_hardware_profile()
        console.print(f"Selected model: {new_profile.selected_model}")
    else:
        # Find matching model
        matching_models = [
            (short, full) for short, full, _ in AVAILABLE_MODELS
            if short == model_lower
        ]
        
        if not matching_models:
            print_error(f"Unknown model: {model_lower!r}")
            console.print("Available: 31b, 26b, e4b, auto")
            raise typer.Exit(1)
        
        short_name, full_model_name = matching_models[0]
        set_config_value("model_override", full_model_name)
        print_success(f"Model set to {full_model_name}")
        # Clear the cached hardware profile
        from driftshell.core.hardware import get_hardware_profile as ghp
        ghp.cache_clear()


@app.command("set")
def set_setting(
    key: str = typer.Argument(..., help="Setting key to modify"),
    value: str = typer.Argument(..., help="Value to assign"),
) -> None:
    """Set a configuration value.
    
    Supported keys:
    - daily_limit (int): Max commands per day
    - exec_limit (int): Max auto-executed commands per day
    - exec_timeout (int): Command execution timeout in seconds
    - memory_window (int): Number of past commands to consider
    - snapshot_limit (int): Max active snapshots
    - skip_scoring (bool): Skip risk scoring
    """
    cfg = get_config()
    if not hasattr(cfg, key):
        print_error(f"Unknown setting: {key!r}")
        console.print("Use [cyan]drift settings view[/cyan] to see all settings")
        raise typer.Exit(1)

    # Coerce to appropriate type
    current = getattr(cfg, key)
    try:
        if isinstance(current, bool):
            coerced = value.lower() in ("true", "1", "yes")
        elif isinstance(current, int):
            coerced = int(value)
        elif isinstance(current, float):
            coerced = float(value)
        else:
            coerced = value if value != "null" else None
    except ValueError:
        print_error(f"Cannot convert {value!r} to {type(current).__name__}")
        raise typer.Exit(1)

    set_config_value(key, coerced)
    print_success(f"Set {key} = {coerced!r}")


@app.command("get")
def get_setting(
    key: str = typer.Argument(..., help="Setting key to retrieve"),
) -> None:
    """Get a configuration value."""
    cfg = get_config()
    if not hasattr(cfg, key):
        print_error(f"Unknown setting: {key!r}")
        console.print("Use [cyan]drift settings view[/cyan] to see all settings")
        raise typer.Exit(1)
    console.print(f"{key} = {getattr(cfg, key)!r}")


@app.command("upgrade")
def upgrade_plan() -> None:
    """Upgrade to Pro plan.

    Pro features:
    - Unlimited daily commands
    - Custom safety settings
    - Advanced risk management
    - Priority support
    """
    from rich.panel import Panel

    console.print(
        Panel.fit(
            "[bold drift.amber]Pro Plan[/bold drift.amber]\n\n"
            "[bold]Coming Soon![/bold]\n\n"
            "We're working on bringing Pro features to Drift.\n"
            "Join our waitlist to be notified when it launches.\n\n"
            "Features include:\n"
            "  • Unlimited daily commands\n"
            "  • Custom safety settings\n"
            "  • Advanced risk management\n"
            "  • Priority support\n\n"
            "Visit [cyan]https://driftshell.dev/pro[/cyan] to learn more",
            border_style="amber",
        )
    )

