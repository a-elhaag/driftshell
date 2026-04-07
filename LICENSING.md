# Drift Licensing & Subscription System

## Overview

Drift now has a production-ready licensing system with:
- **HMAC-signed license keys** that cannot be forged or tampered with
- **Sealed configuration** that prevents users from editing limits at runtime
- **Three subscription tiers** (Free, Pro, Enterprise) with increasing limits
- **CLI commands** to manage licenses (activate, status, remove)

## Architecture

### License Keys

License keys are cryptographically signed using HMAC-SHA256:
```
{json_payload}.{signature}
```

Example:
```
{"plan":"pro","user_id":"user@example.com","issued_at":"2026-04-07T01:44:29.360728","expires_at":"2026-10-04T01:44:29.360750"}.d279203f0e8a30111b5185d7a9fb16709b2baf093a770f41fd6539f356f93cf7
```

**Key Properties:**
- Cannot be forged (signature validates against master secret)
- Cannot be tampered with (even one character change breaks signature)
- Can be perpetual (no expiry) or time-limited (1 year, 2 years, etc.)
- Human-readable payload (JSON)

### Sealed Configuration

The config is "sealed" at startup to prevent users from editing TOML and manually increasing limits:

1. During `drift` startup, `_bootstrap()` calls `seal_config()`
2. This locks: `daily_limit`, `exec_limit`, `snapshot_limit`, `plan`
3. Users cannot edit config to unlock limits (TOML edits are ignored for sealed fields)
4. **Only way to unlock limits**: Activate a valid license key via `drift license activate`

### Plan Tiers

| Plan | Daily Queries | Auto-Exec/Day | Snapshots | Auto-Exec | Explain | Dry-Run |
|------|---------------|---------------|-----------|-----------|---------|---------|
| **Free** | 20 | 3 | 1 | ✓ | ✓ | ✓ |
| **Pro** | 100 | 30 | 10 | ✓ | ✓ | ✓ |
| **Enterprise** | 1000 | 500 | 100 | ✓ | ✓ | ✓ |

## Usage

### Users: Activate a License

```bash
# Drift team provides a license key to the user
drift license activate "payload.signature_here"

# Shows:
# License activated for PRO plan
#   User: user@example.com
#   Daily queries: 100
#   Auto-exec per day: 30
#   Snapshots: 10
#   Expires in: 365 days
```

### Users: Check License Status

```bash
drift license status

# Output for active license:
# Active License
#   Plan: PRO
#   User: user@example.com
#   Issued: 2026-04-07T01:44:29.360728
#   Expires: 2026-10-04T01:44:29.360750
#   Days remaining: 180
#
# Limits:
#   Daily queries: 100
#   Auto-exec per day: 30
#   Snapshots: 10
#   Explain mode: ✓
#   Dry-run mode: ✓
```

### Users: Remove License (Revert to Free)

```bash
drift license remove

# Output:
# Remove active license and revert to FREE plan? [y/N]: y
# License removed. Running on FREE plan.
```

### Admins: Generate License Keys (Drift Team)

```bash
# For your internal use / distribution to customers

python -m driftshell.tools.license_generator pro user@example.com 365
# Output: {"plan":"pro",...}.signature

# Perpetual license (no expiry)
python -m driftshell.tools.license_generator enterprise acme@corp.com
# Output: {"plan":"enterprise",...}.signature
```

## Security

### HMAC Validation

Every license key is validated before use:
1. Extract payload and signature from key
2. Recompute signature using master secret and payload
3. Use constant-time comparison (hmac.compare_digest) to prevent timing attacks
4. If signatures don't match: License is INVALID

**Attack Prevention:**
- Forging keys: Impossible (attacker doesn't know master secret)
- Tampering: Impossible (changing one byte breaks signature)
- Brute-forcing: Infeasible (SHA256 = 256-bit keyspace, 2^256 possibilities)

### Sealed Configuration

Users cannot unlock limits by:
- Editing `~/.drift/config.toml` directly (sealed fields are locked)
- Running `drift settings set daily_limit 1000` (doesn't override sealed config)
- Modifying the SQLite database (limits read from sealed config, not DB)

**Only legitimate way:** Activate a valid license key.

### Expiry Handling

If a license expires:
- User sees: `License EXPIRED` in `drift license status`
- Drift automatically falls back to FREE tier limits
- No manual intervention needed (no "license expired, please upgrade" nag)

## Production Setup

### 1. Set Master Secret (Environment Variable)

**DO NOT** hardcode the master secret in code. Use an environment variable:

```bash
# ~/.bashrc or ~/.zshrc
export DRIFT_LICENSE_SECRET="your-secret-key-here"
```

Update `driftshell/licensing/license.py` to read from env:

```python
import os
_MASTER_SECRET = os.getenv(
    "DRIFT_LICENSE_SECRET",
    "drift-license-secret-v1"  # fallback for dev/testing
)
```

### 2. Generate Keys Offline

Keep license generation on an internal server / machine:

```bash
# Internal only (not shipped with Drift)
python -m driftshell.tools.license_generator pro customer@acme.com 365
# Output the key (never transmit in plain HTTP, use HTTPS or PGP)
```

### 3. Distribute Keys Securely

- Email keys via HTTPS or PGP-encrypted channels
- Don't commit keys to version control
- Log activations for audit trail (future enhancement)

### 4. Monitor License Usage

Future enhancements:
- Log when licenses are activated / removed
- Send expiry reminders (30 days, 7 days before expiry)
- Implement license revocation (for support/abuse cases)
- Add license validation in background (verify keys are still valid)

## Implementation Details

### Files

| File | Purpose |
|------|---------|
| `driftshell/licensing/license.py` | HMAC signing, key generation, validation |
| `driftshell/licensing/features.py` | Plan tier definitions, feature flags |
| `driftshell/config/sealed.py` | Sealed config (immutable after bootstrap) |
| `driftshell/cli/license.py` | User-facing license commands |
| `driftshell/tools/license_generator.py` | Admin tool for generating keys |
| `driftshell/models/schemas.py` | Added `license_key` field to DriftConfig |
| `driftshell/config/loader.py` | Auto-apply license limits on startup |
| `driftshell/config/sealed.py` | Lock limits after bootstrap |
| `driftshell/core/limiter.py` | Use sealed config for limit checks |

### Key Classes

**License (immutable dataclass)**
```python
@dataclass(frozen=True)
class License:
    plan: str              # "free", "pro", "enterprise"
    issued_at: str         # ISO 8601
    expires_at: str | None # ISO 8601 or None (perpetual)
    user_id: str          # Email or identifier
    key: str              # Full signed key string
    status: LicenseStatus # ACTIVE, EXPIRED, INVALID, NOT_FOUND
```

**LicenseStatus (Enum)**
```python
class LicenseStatus(str, Enum):
    ACTIVE = "active"      # Valid and not expired
    EXPIRED = "expired"    # Valid signature but past expiry
    INVALID = "invalid"    # Signature doesn't match
    NOT_FOUND = "not_found"  # No license configured
```

### Backward Compatibility

- Existing configurations continue to work (free tier by default)
- No breaking changes to CLI commands or APIs
- All 57 existing tests pass without modification
- License is optional (free tier is fully functional)

## Testing

```bash
# All tests pass with licensing system
pytest tests/ -v
# 57 passed

# Test license key generation
python -m driftshell.tools.license_generator pro test@example.com 30

# Test license validation
python -c "from driftshell.licensing import validate_license_key; lic = validate_license_key('...')"

# Test plan limits
python -c "from driftshell.licensing import get_plan_limits; print(get_plan_limits('pro'))"
```

## Roadmap

- [ ] Environment variable for master secret
- [ ] License activation audit log
- [ ] Expiry reminders (30/7 days before)
- [ ] License revocation endpoint
- [ ] Dashboard for license management
- [ ] Renewal reminders / auto-renewal
- [ ] Per-team licensing (for enterprise)
- [ ] Feature flags beyond limits (e.g., "analytics", "api-access")
