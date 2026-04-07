"""License and subscription management commands."""

from __future__ import annotations

import typer

from driftshell.config.sealed import unsafe_bypass_seal_for_license
from driftshell.config.loader import set_config_value
from driftshell.licensing import (
    validate_license_key,
    LicenseStatus,
    get_plan_limits,
)
from driftshell.licensing.features import get_active_license, clear_license_cache
from driftshell.utils.console import (
    console,
    print_error,
    print_success,
    print_warning,
)

app = typer.Typer(help="License and subscription management")


@app.command("activate")
def activate_license(
    key: str = typer.Argument(..., help="License key (provided by Drift team)"),
) -> None:
    """Activate a license key.

    Usage:
        drift license activate "payload.signature"
    """
    # Validate the key first
    license_obj = validate_license_key(key)

    if license_obj.status == LicenseStatus.INVALID:
        print_error("Invalid license key. Please check and try again.")
        raise typer.Exit(1)

    if license_obj.status == LicenseStatus.EXPIRED:
        print_warning(
            f"License expired on {license_obj.expires_at}. "
            "Please contact support for renewal."
        )
        raise typer.Exit(1)

    # Save the license key
    set_config_value("license_key", key)

    # Update sealed config if initialized
    try:
        unsafe_bypass_seal_for_license(key)
    except RuntimeError:
        # Config not yet sealed (early init phase), that's OK
        pass

    limits = get_plan_limits(license_obj.plan)
    print_success(f"License activated for {license_obj.plan.upper()} plan")
    console.print(f"  User: {license_obj.user_id}")
    console.print(f"  Daily queries: {limits['daily_limit']}")
    console.print(f"  Auto-exec per day: {limits['exec_limit']}")
    console.print(f"  Snapshots: {limits['snapshot_limit']}")
    if license_obj.expires_at:
        days_left = license_obj.days_until_expiry()
        if days_left is not None and days_left > 0:
            console.print(f"  Expires in: {days_left} days")


@app.command("status")
def license_status() -> None:
    """Show current license and plan information.

    Usage:
        drift license status
    """
    license_obj = get_active_license()

    if license_obj.status == LicenseStatus.NOT_FOUND:
        console.print("[dim]No license activated.[/dim]")
        console.print("\nRunning on FREE plan:")
        limits = get_plan_limits("free")
        _print_limits(limits)
        return

    if license_obj.status == LicenseStatus.INVALID:
        print_warning("License key is invalid or corrupted.")
        console.print("\nRunning on FREE plan:")
        limits = get_plan_limits("free")
        _print_limits(limits)
        return

    if license_obj.status == LicenseStatus.EXPIRED:
        console.print(f"[bold #f85149]License EXPIRED[/bold #f85149]")
        console.print(f"  Expired on: {license_obj.expires_at}")
        console.print("\nRunning on FREE plan:")
        limits = get_plan_limits("free")
        _print_limits(limits)
        return

    # Active license
    console.print(f"[bold #58a6ff]Active License[/bold #58a6ff]")
    console.print(f"  Plan: {license_obj.plan.upper()}")
    console.print(f"  User: {license_obj.user_id}")
    console.print(f"  Issued: {license_obj.issued_at}")

    if license_obj.expires_at:
        days_left = license_obj.days_until_expiry()
        console.print(f"  Expires: {license_obj.expires_at}")
        if days_left is not None:
            if days_left > 0:
                console.print(f"  [bold #3fb950]Days remaining: {days_left}[/bold #3fb950]")
            else:
                console.print(f"  [bold #f85149]EXPIRED[/bold #f85149]")
    else:
        console.print(f"  Expires: [bold #3fb950]Never (perpetual)[/bold #3fb950]")

    limits = get_plan_limits(license_obj.plan)
    console.print("\nLimits:")
    _print_limits(limits)


@app.command("remove")
def remove_license() -> None:
    """Remove the active license (revert to FREE plan).

    Usage:
        drift license remove
    """
    confirm = typer.confirm(
        "Remove active license and revert to FREE plan?",
        default=False,
    )
    if not confirm:
        raise typer.Exit(0)

    set_config_value("license_key", None)

    # Update sealed config if initialized
    try:
        unsafe_bypass_seal_for_license("")
    except RuntimeError:
        pass

    print_success("License removed. Running on FREE plan.")


def _print_limits(limits: dict[str, int | bool]) -> None:
    """Helper to print limit info."""
    console.print(f"  Daily queries: [bold]{limits['daily_limit']}[/bold]")
    console.print(f"  Auto-exec per day: [bold]{limits['exec_limit']}[/bold]")
    console.print(f"  Snapshots: [bold]{limits['snapshot_limit']}[/bold]")
    console.print(f"  Explain mode: {'✓' if limits['explain_mode'] else '✗'}")
    console.print(f"  Dry-run mode: {'✓' if limits['dry_run'] else '✗'}")
