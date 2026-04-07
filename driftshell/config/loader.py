from __future__ import annotations

import functools
import tomllib
from typing import Any

import tomli_w

from driftshell.config.defaults import (
    DEFAULT_DAILY_LIMIT,
    DEFAULT_EXEC_LIMIT,
    DEFAULT_EXEC_TIMEOUT,
    DEFAULT_MEMORY_WINDOW,
    DEFAULT_MODEL_OVERRIDE,
    DEFAULT_SKIP_SCORING,
    DEFAULT_SNAPSHOT_LIMIT,
    DEFAULT_VRAM_OVERRIDE,
    DEFAULT_PLAN,
    DEFAULT_D_COMMAND_OVERRIDE,
    DEFAULT_LICENSE_KEY,
)
from driftshell.models.schemas import DriftConfig
from driftshell.utils.paths import CONFIG_PATH


def _load_raw() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


@functools.lru_cache(maxsize=1)
def get_config() -> DriftConfig:
    raw = _load_raw()

    # Get license key from config
    license_key = raw.get("license_key", DEFAULT_LICENSE_KEY)

    # If a valid license is active, use its plan and limits
    if license_key:
        from driftshell.licensing import validate_license_key, LicenseStatus
        license_obj = validate_license_key(license_key)
        if license_obj.status == LicenseStatus.ACTIVE:
            limits = {
                "pro": {"daily": 100, "exec": 30, "snapshot": 10},
                "enterprise": {"daily": 1000, "exec": 500, "snapshot": 100},
            }.get(license_obj.plan, {"daily": 10, "exec": 3, "snapshot": 1})

            return DriftConfig(
                memory_window=raw.get("memory_window", DEFAULT_MEMORY_WINDOW),
                exec_timeout=raw.get("exec_timeout", DEFAULT_EXEC_TIMEOUT),
                daily_limit=raw.get("daily_limit", limits["daily"]),
                exec_limit=raw.get("exec_limit", limits["exec"]),
                snapshot_limit=raw.get("snapshot_limit", limits["snapshot"]),
                model_override=raw.get("model_override", DEFAULT_MODEL_OVERRIDE),
                skip_scoring=raw.get("skip_scoring", DEFAULT_SKIP_SCORING),
                vram_override=raw.get("vram_override", DEFAULT_VRAM_OVERRIDE),
                plan=license_obj.plan,
                d_command_override=raw.get("d_command_override", DEFAULT_D_COMMAND_OVERRIDE),
                license_key=license_key,
            )

    # No valid license; use free tier defaults
    return DriftConfig(
        memory_window=raw.get("memory_window", DEFAULT_MEMORY_WINDOW),
        exec_timeout=raw.get("exec_timeout", DEFAULT_EXEC_TIMEOUT),
        daily_limit=raw.get("daily_limit", DEFAULT_DAILY_LIMIT),
        exec_limit=raw.get("exec_limit", DEFAULT_EXEC_LIMIT),
        snapshot_limit=raw.get("snapshot_limit", DEFAULT_SNAPSHOT_LIMIT),
        model_override=raw.get("model_override", DEFAULT_MODEL_OVERRIDE),
        skip_scoring=raw.get("skip_scoring", DEFAULT_SKIP_SCORING),
        vram_override=raw.get("vram_override", DEFAULT_VRAM_OVERRIDE),
        plan=DEFAULT_PLAN,
        d_command_override=raw.get("d_command_override", DEFAULT_D_COMMAND_OVERRIDE),
        license_key=license_key,
    )


def set_config_value(key: str, value: Any) -> None:
    raw = _load_raw()
    if value is None:
        # Remove the key if value is None (TOML can't serialize None)
        raw.pop(key, None)
    else:
        raw[key] = value
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("wb") as f:
        tomli_w.dump(raw, f)
    get_config.cache_clear()
