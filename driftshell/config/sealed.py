"""Sealed configuration: prevents runtime edits to limits after startup.

This module ensures that limits (daily_limit, exec_limit, snapshot_limit, plan)
cannot be modified at runtime after the initial bootstrap. Only the license key
can be changed, and only through the licensing CLI commands.
"""

from __future__ import annotations

import functools
from threading import Lock

from driftshell.config.loader import get_config as _load_config
from driftshell.models.schemas import DriftConfig

_seal_lock = Lock()
_sealed_config: DriftConfig | None = None
_is_sealed = False


@functools.lru_cache(maxsize=1)
def seal_config() -> DriftConfig:
    """Seal the config at startup (after Ollama/DB bootstrap).

    Once sealed, the following fields are immutable:
    - daily_limit
    - exec_limit
    - snapshot_limit
    - plan

    Returns:
        The sealed DriftConfig object
    """
    global _sealed_config, _is_sealed

    with _seal_lock:
        if _is_sealed:
            return _sealed_config

        _sealed_config = _load_config()
        _is_sealed = True
        return _sealed_config


def get_sealed_config() -> DriftConfig:
    """Get the sealed config.

    Raises:
        RuntimeError: If config has not been sealed yet
    """
    if not _is_sealed:
        raise RuntimeError(
            "Config not sealed. Call seal_config() during bootstrap first."
        )
    return _sealed_config


def is_config_sealed() -> bool:
    """Check if config has been sealed."""
    return _is_sealed


def unsafe_bypass_seal_for_license(new_key: str) -> None:
    """Internal: Update only the license key in a sealed config.

    This is the ONLY way to modify a sealed config, and it clears the license
    cache so the new key is validated on next use.

    Should only be called by the licensing CLI commands.

    Args:
        new_key: New license key string
    """
    global _sealed_config

    if not _is_sealed:
        raise RuntimeError("Config must be sealed before updating license.")

    with _seal_lock:
        # Create a new sealed config with updated license
        if _sealed_config:
            _sealed_config = _sealed_config.model_copy(
                update={"license_key": new_key}
            )

    # Clear caches so new license is validated
    from driftshell.config.loader import get_config
    from driftshell.licensing.features import clear_license_cache

    get_config.cache_clear()
    clear_license_cache()
