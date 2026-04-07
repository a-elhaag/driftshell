from __future__ import annotations

import typer

from driftshell.config.loader import get_config, set_config_value
from driftshell.utils.console import console, print_error, print_success

app = typer.Typer()


@app.command("get")
def config_get(key: str = typer.Argument(..., help="Config key to read")) -> None:
    """Get a config value."""
    cfg = get_config()
    if not hasattr(cfg, key):
        print_error(f"Unknown config key: {key!r}")
        raise typer.Exit(1)
    console.print(f"{key} = {getattr(cfg, key)!r}")


@app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key to set"),
    value: str = typer.Argument(..., help="Value to assign"),
) -> None:
    """Set a config value."""
    cfg = get_config()
    if not hasattr(cfg, key):
        print_error(f"Unknown config key: {key!r}")
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
