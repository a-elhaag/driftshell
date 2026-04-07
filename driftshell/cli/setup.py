"""
First-time setup and onboarding workflow.
"""
from __future__ import annotations

import typer
from rich.panel import Panel

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


@app.command()
def setup() -> None:
    """Run first-time setup and onboarding workflow.
    
    This guides you through:
    - Hardware detection and model selection
    - Safety settings (daily limits)
    - Optional features
    """
    # Show ASCII logo
    print_logo()
    console.print()
    
    console.print(
        Panel.fit(
            "[bold]Welcome to Drift[/bold]\n\n"
            "Plain English → shell commands, powered by local LLMs",
            border_style="cyan",
        )
    )
    console.print()

    # Step 1: Hardware Profile
    console.print("[bold]Step 1: Hardware Detection[/bold]")
    profile = get_hardware_profile()
    console.print(f"  RAM: {profile.ram_gb:.1f} GB")
    console.print(f"  VRAM: {profile.vram_gb:.1f} GB")
    console.print(f"  Auto-selected Model: {profile.selected_model}")
    console.print()

    cfg = get_config()

    # Step 2: Model Selection
    console.print("[bold]Step 2: Model Selection[/bold]")
    console.print("Available models:")
    for i, (short_name, full_name, description) in enumerate(AVAILABLE_MODELS, 1):
        console.print(f"  {i}. [cyan]{short_name}[/cyan] - {full_name}")
        console.print(f"     {description}")
    console.print()
    
    model_choice = console.input(
        "Select model (1-3) or press Enter to keep auto-detected: "
    ).strip()
    
    if model_choice in ("1", "2", "3"):
        selected_model = AVAILABLE_MODELS[int(model_choice) - 1][1]
        set_config_value("model_override", selected_model)
        print_success(f"Model set to {selected_model}")
        # Clear the cached hardware profile
        from driftshell.core.hardware import get_hardware_profile as ghp
        ghp.cache_clear()
    elif model_choice:
        print_warning(f"Invalid choice '{model_choice}', keeping auto-detection")
    
    console.print()

    # Step 3: Plan Selection
    console.print("[bold]Step 3: Plan Selection[/bold]")
    console.print("Choose your plan:")
    console.print("  [cyan]1. Free[/cyan] - Basic safety limits")
    console.print("     • 50 commands/day")
    console.print("     • Standard risk scoring")
    console.print("  [dim cyan]2. Premium[/dim cyan] [drift.amber](Coming Soon)[/drift.amber] - Advanced safety & customization")
    console.print("     [dim]• Unlimited commands[/dim]")
    console.print("     [dim]• Custom safety settings[/dim]")
    console.print("     [dim]• Risk threshold tuning[/dim]")
    console.print()
    
    plan_choice = console.input(
        "Select plan (1 - only Free available now, default: 1): "
    ).strip()
    
    is_premium = False
    if plan_choice == "2":
        print_warning("Premium plan is coming soon! Using Free plan for now.")
        is_premium = False
        set_config_value("plan", "free")
        set_config_value("daily_limit", 50)
    elif plan_choice == "1" or not plan_choice:
        is_premium = False
        print_success("Free plan selected")
        set_config_value("plan", "free")
        # Enforce free tier limits
        set_config_value("daily_limit", 50)
    else:
        print_warning(f"Invalid choice '{plan_choice}', using Free plan")
        set_config_value("plan", "free")
        set_config_value("daily_limit", 50)
    
    # Clear config cache
    from driftshell.config.loader import get_config as gc
    gc.cache_clear()
    cfg = get_config()
    
    console.print()

    # Step 4: Safety Settings (Premium only)
    if is_premium:
        console.print("[bold]Step 4: Safety Settings[/bold drift.blue] [drift.amber](Premium)[/drift.amber]")
        
        daily_limit = console.input(
            f"Daily command limit (default: {cfg.daily_limit}): "
        ).strip()
        if daily_limit:
            try:
                set_config_value("daily_limit", int(daily_limit))
                print_success(f"Set daily_limit to {daily_limit}")
            except ValueError:
                print_warning(f"Invalid value, keeping {cfg.daily_limit}")
        
        exec_limit = console.input(
            f"Daily auto-exec limit (default: {cfg.exec_limit}): "
        ).strip()
        if exec_limit:
            try:
                set_config_value("exec_limit", int(exec_limit))
                print_success(f"Set exec_limit to {exec_limit}")
            except ValueError:
                print_warning(f"Invalid value, keeping {cfg.exec_limit}")
        
        console.print()

        # Step 5: Features (Premium only)
        console.print("[bold]Step 5: Feature Configuration[/bold drift.blue] [drift.amber](Premium)[/drift.amber]")
    else:
        # Step 4: Features (Free tier)
        console.print("[bold]Step 4: Feature Configuration[/bold]")
    
    skip_scoring = console.input(
        f"Skip risk scoring for faster responses? (y/n, default: no): "
    ).strip().lower()
    if skip_scoring in ("y", "yes"):
        set_config_value("skip_scoring", True)
        print_success("Risk scoring disabled")
    elif skip_scoring in ("n", "no"):
        set_config_value("skip_scoring", False)
        print_success("Risk scoring enabled")
    
    console.print()

    # Completion
    plan_text = "[drift.green]Free[/drift.green]"
    premium_note = "\n\n[dim drift.amber]💡 Premium plan coming soon![/dim drift.amber]\n[dim]Try: [cyan]drift settings upgrade[/cyan] to join the waitlist[/dim]"
    console.print(
        Panel.fit(
            f"[bold green]✓ Setup Complete![/bold green]\n\n"
            f"Plan: {plan_text}{premium_note}\n\n"
            "You're ready to use Drift.\n\n"
            "Try: [bold cyan]drift[/bold cyan] to enter interactive mode\n"
            "Or:  [bold cyan]d 'list files'[/bold cyan] for quick queries\n"
            "Or:  [bold cyan]drift settings model[/bold cyan] to change models",
            border_style="green",
        )
    )
