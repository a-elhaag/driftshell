"""Drift licensing and subscription system.

This module provides:
- License key generation and validation (HMAC-based)
- Immutable plan tiers (Free, Pro, Enterprise)
- Sealed config to prevent runtime limit manipulation
- Feature flag system tied to subscription level
"""

from driftshell.licensing.license import (
    License,
    LicenseStatus,
    validate_license_key,
    generate_license_key,
)
from driftshell.licensing.features import get_plan_limits, is_feature_enabled

__all__ = [
    "License",
    "LicenseStatus",
    "validate_license_key",
    "generate_license_key",
    "get_plan_limits",
    "is_feature_enabled",
]
