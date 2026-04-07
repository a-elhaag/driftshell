"""Plan tiers and feature flags tied to subscription level."""

from __future__ import annotations

import functools

from driftshell.licensing.license import License, validate_license_key, LicenseStatus
from driftshell.config.loader import get_config


# Plan limit definitions (immutable)
_PLAN_LIMITS = {
    "free": {
        "daily_limit": 20,
        "exec_limit": 3,
        "snapshot_limit": 1,
        "auto_exec": False,
        "explain_mode": True,
        "dry_run": True,
    },
    "pro": {
        "daily_limit": 100,
        "exec_limit": 30,
        "snapshot_limit": 10,
        "auto_exec": True,
        "explain_mode": True,
        "dry_run": True,
    },
    "enterprise": {
        "daily_limit": 1000,
        "exec_limit": 500,
        "snapshot_limit": 100,
        "auto_exec": True,
        "explain_mode": True,
        "dry_run": True,
    },
}


@functools.lru_cache(maxsize=1)
def get_active_license() -> License:
    """Retrieve and validate the active license from config.

    Returns:
        License object (defaults to "free" plan if no valid license)
    """
    cfg = get_config()
    if not cfg.license_key:
        # No license key configured; default to free tier
        return License(
            plan="free",
            issued_at="",
            expires_at=None,
            user_id="",
            key="",
            status=LicenseStatus.NOT_FOUND,
        )

    return validate_license_key(cfg.license_key)


def get_plan_limits(plan: str | None = None) -> dict[str, int | bool]:
    """Get immutable limits for a plan tier.

    Args:
        plan: Plan name ("free", "pro", "enterprise"). If None, uses active license.

    Returns:
        Immutable dict of limits for the plan.
    """
    if plan is None:
        license_obj = get_active_license()
        plan = license_obj.plan

    return _PLAN_LIMITS.get(plan, _PLAN_LIMITS["free"]).copy()


def is_feature_enabled(feature: str, license_obj: License | None = None) -> bool:
    """Check if a feature is enabled under the active license.

    Args:
        feature: Feature name (e.g., "auto_exec", "explain_mode", "dry_run")
        license_obj: Optional License object (uses active license if not provided)

    Returns:
        True if feature is enabled, False otherwise
    """
    if license_obj is None:
        license_obj = get_active_license()

    # Expired or invalid licenses fall back to free tier
    if license_obj.status != LicenseStatus.ACTIVE:
        license_obj = License(
            plan="free",
            issued_at="",
            expires_at=None,
            user_id="",
            key="",
            status=LicenseStatus.ACTIVE,
        )

    limits = _PLAN_LIMITS.get(license_obj.plan, _PLAN_LIMITS["free"])
    return limits.get(feature, False)


def clear_license_cache() -> None:
    """Clear the cached license (called after license activation/update)."""
    get_active_license.cache_clear()
