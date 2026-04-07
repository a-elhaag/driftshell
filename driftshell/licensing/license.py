"""Immutable license system with HMAC-based key validation."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# Production master secret (DO NOT CHANGE in code—use environment variable)
_MASTER_SECRET = "drift-license-secret-v1"


class LicenseStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    NOT_FOUND = "not_found"


@dataclass(frozen=True)
class License:
    """Immutable license record."""
    plan: str  # "free", "pro", "enterprise"
    issued_at: str  # ISO 8601 datetime
    expires_at: str | None  # ISO 8601 or None for perpetual
    user_id: str  # Email or unique identifier
    key: str  # HMAC-signed key
    status: LicenseStatus

    def is_expired(self) -> bool:
        """Check if license has expired."""
        if self.expires_at is None:
            return False
        expire_dt = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expire_dt

    def days_until_expiry(self) -> int | None:
        """Days remaining until expiry (-1 if expired, None if perpetual)."""
        if self.expires_at is None:
            return None
        expire_dt = datetime.fromisoformat(self.expires_at)
        delta = (expire_dt - datetime.now()).days
        return max(delta, -1)


def _compute_signature(payload: str) -> str:
    """Compute HMAC-SHA256 signature over payload."""
    return hmac.new(
        _MASTER_SECRET.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def generate_license_key(
    plan: str,
    user_id: str,
    days_valid: int | None = None,
) -> str:
    """Generate a signed license key.

    Args:
        plan: "free", "pro", or "enterprise"
        user_id: Email or unique user identifier
        days_valid: Days until expiry. None = perpetual/lifetime.

    Returns:
        Signed license key string (format: payload.signature)
    """
    issued_at = datetime.now().isoformat()
    expires_at = None

    if days_valid is not None:
        expires_at = (datetime.now() + timedelta(days=days_valid)).isoformat()

    payload = json.dumps(
        {
            "plan": plan,
            "user_id": user_id,
            "issued_at": issued_at,
            "expires_at": expires_at,
        },
        separators=(",", ":"),
        sort_keys=True,
    )

    signature = _compute_signature(payload)
    return f"{payload}.{signature}"


def validate_license_key(key: str) -> License:
    """Validate and parse a license key.

    Args:
        key: License key string (format: payload.signature)

    Returns:
        License object with status information
    """
    if not key or not isinstance(key, str):
        return License(
            plan="free",
            issued_at="",
            expires_at=None,
            user_id="",
            key=key or "",
            status=LicenseStatus.INVALID,
        )

    # Split payload from signature
    parts = key.rsplit(".", 1)
    if len(parts) != 2:
        return License(
            plan="free",
            issued_at="",
            expires_at=None,
            user_id="",
            key=key,
            status=LicenseStatus.INVALID,
        )

    payload_str, signature = parts

    # Verify signature
    expected_sig = _compute_signature(payload_str)
    if not hmac.compare_digest(signature, expected_sig):
        return License(
            plan="free",
            issued_at="",
            expires_at=None,
            user_id="",
            key=key,
            status=LicenseStatus.INVALID,
        )

    # Parse payload
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError:
        return License(
            plan="free",
            issued_at="",
            expires_at=None,
            user_id="",
            key=key,
            status=LicenseStatus.INVALID,
        )

    plan = data.get("plan", "free")
    user_id = data.get("user_id", "")
    issued_at = data.get("issued_at", "")
    expires_at = data.get("expires_at")

    # Validate plan
    if plan not in ("free", "pro", "enterprise"):
        plan = "free"

    license_obj = License(
        plan=plan,
        user_id=user_id,
        issued_at=issued_at,
        expires_at=expires_at,
        key=key,
        status=LicenseStatus.ACTIVE,
    )

    # Check expiry
    if license_obj.is_expired():
        license_obj = License(
            plan=plan,
            user_id=user_id,
            issued_at=issued_at,
            expires_at=expires_at,
            key=key,
            status=LicenseStatus.EXPIRED,
        )

    return license_obj
