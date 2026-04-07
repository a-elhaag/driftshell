#!/usr/bin/env python
"""Command-line tool for generating signed license keys (admin only).

This tool is used internally by the Drift team to generate license keys
that can be distributed to customers.

Usage:
    python -m driftshell.tools.license_generator pro user@example.com 365

This generates a signed license key valid for 365 days on the PRO plan.
"""

from __future__ import annotations

import sys

from driftshell.licensing.license import generate_license_key


def main() -> None:
    """Generate a signed license key."""
    if len(sys.argv) < 3:
        print("Usage: license_generator <plan> <user_id> [days_valid]")
        print("")
        print("  plan: free, pro, or enterprise")
        print("  user_id: Email or unique identifier")
        print("  days_valid: Days until expiry (default: perpetual/None)")
        print("")
        print("Example:")
        print("  license_generator pro user@example.com 365")
        print("  license_generator enterprise acme@corp.com")
        sys.exit(1)

    plan = sys.argv[1].lower()
    user_id = sys.argv[2]
    days_valid = None

    if len(sys.argv) >= 4:
        try:
            days_valid = int(sys.argv[3])
        except ValueError:
            print(f"Error: days_valid must be an integer, got {sys.argv[3]!r}")
            sys.exit(1)

    if plan not in ("free", "pro", "enterprise"):
        print(f"Error: plan must be 'free', 'pro', or 'enterprise', got {plan!r}")
        sys.exit(1)

    key = generate_license_key(plan, user_id, days_valid)
    print(key)


if __name__ == "__main__":
    main()
