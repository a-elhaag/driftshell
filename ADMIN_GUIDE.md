# Drift Admin & Support Guide

## Quick Reference: License Management

### Generate a License Key (Admin Only)

```bash
# Pro plan for 1 year
python -m driftshell.tools.license_generator pro customer@acme.com 365

# Enterprise plan, perpetual (no expiry)
python -m driftshell.tools.license_generator enterprise corp@bigcorp.com

# Free plan (rarely needed, users get this by default)
python -m driftshell.tools.license_generator free email@example.com
```

**Output:** A single line string like `{"plan":"pro",...}.signature`

### Distribute Keys

1. **Email to customer** (via HTTPS or encrypted channel, never plain HTTP)
2. **Provide activation instructions** (see below)
3. **Keep record** of key issued, customer email, plan, expiry date

### Customer Activates License

Provide this instruction:

```
Run this command and paste the key we sent you:

$ drift license activate "payload.signature_here"

If successful, you'll see:
License activated for PRO plan
  User: your@email.com
  Daily queries: 100
  Auto-exec per day: 30
  Snapshots: 10
  Expires in: 365 days
```

---

## Support Scenarios

### Scenario 1: Customer Lost Their License Key

**Problem:** "I lost my license key, can you send it again?"

**Solution:**
1. Regenerate the key with same plan and duration
2. Send new key via secure channel
3. Customer activates with `drift license activate`

```bash
# If original was pro for 1 year (expires 2027-04-07)
# Regenerate now (2026-04-07):
python -m driftshell.tools.license_generator pro customer@acme.com 365
```

### Scenario 2: License Expired

**Problem:** "My license expired. Can I renew?"

**Solution:**
1. Check expiry with customer: `drift license status`
2. Generate new key with extended period
3. Customer activates: `drift license activate "new_key"`

```bash
# Generate 2-year renewal
python -m driftshell.tools.license_generator pro customer@acme.com 730
```

### Scenario 3: Customer Wants to Upgrade Plan

**Problem:** "Can I upgrade from Pro to Enterprise?"

**Solution:**
1. Confirm tier upgrade (Pro → Enterprise)
2. Generate new Enterprise key with same/extended duration
3. Customer runs:
   ```bash
   drift license activate "new_enterprise_key"
   drift license status  # Verify new limits
   ```

### Scenario 4: Customer Needs to Remove License (Sandbox/Testing)

**Problem:** "I accidentally activated wrong license, help!"

**Solution:**
1. Customer runs: `drift license remove`
2. Confirm revert to FREE tier: `drift license status`
3. Generate correct key and have them reactivate

---

## License Key Anatomy

Example key:
```
{"plan":"pro","user_id":"demo@example.com","issued_at":"2026-04-07T01:44:29.360750","expires_at":"2026-10-04T01:44:29.360750"}.d279203f0e8a30111b5185d7a9fb16709b2baf093a770f41fd6539f356f93cf7
```

**Format:** `{json_payload}.{hmac_signature}`

**Fields in payload:**
- `plan`: "free", "pro", or "enterprise"
- `user_id`: Customer email or identifier
- `issued_at`: When key was generated (ISO 8601)
- `expires_at`: When key expires (ISO 8601), or null for perpetual

**Signature:**
- HMAC-SHA256 of the JSON payload
- Uses master secret (environment variable)
- Cannot be forged or tampered with
- If modified, signature fails validation

---

## Verification: Did License Activate Correctly?

```bash
# Customer should see this after activation:
drift license status

# Output should show:
# Active License
#   Plan: PRO
#   User: customer@acme.com
#   Issued: 2026-04-07T01:44:29.360750
#   Expires: 2026-10-04T01:44:29.360750
#   Days remaining: 180
```

If customer sees "No license activated" or "License INVALID":
1. Check key was copied correctly (no extra spaces)
2. Verify key wasn't truncated
3. Generate a fresh key and have them try again

---

## Security: Keys Cannot Be Forged

**Do not worry about:**
- Keys being leaked (they're signed, can't be edited)
- Customers creating fake keys (signature validation fails)
- Keys being used on other machines (they're tied to user_id, no machine ID check—they can be used anywhere, which is intentional for flexibility)

**Do worry about:**
- Master secret being compromised (all keys become worthless)
- Keys being sent in plain HTTP (always use HTTPS)
- Too many keys generated with weak user_ids (audit logging—future feature)

---

## Timeline

**At Each Stage:**
1. **Key Generation** (you): `python -m driftshell.tools.license_generator pro customer@acme.com 365`
2. **Distribution** (you): Email via secure channel
3. **Activation** (customer): `drift license activate "key_here"`
4. **Verification** (customer): `drift license status`
5. **Expiry** (automatic): After expiry date, limit enforcement automatically switches to FREE tier

---

## Common Admin Tasks

### View All Generated Keys

(Currently no central registry—you maintain this)

**Recommendation:** Keep a spreadsheet
| Customer | Email | Plan | Generated | Expires | Notes |
|----------|-------|------|-----------|---------|-------|
| ACME Corp | sales@acme.com | PRO | 2026-04-07 | 2027-04-07 | Contact: John |
| Big Corp | admin@bigcorp.com | ENTERPRISE | 2026-04-01 | Perpetual | Lifetime license |

### Set Master Secret (Ops)

In production environment:
```bash
export DRIFT_LICENSE_SECRET="your-secret-key-here"

# Then run generator:
python -m driftshell.tools.license_generator pro customer@acme.com 365
```

**Important:** Master secret must be the same for:
- Key generation (admin tool)
- Key validation (when customer activates)

If you rotate the secret:
- All previously generated keys become invalid
- Customers will see "License INVALID"
- You'll need to regenerate all keys with new secret
- Only rotate if secret is compromised

---

## Limit Enforcement

Once a license is activated, Drift automatically enforces the plan limits:

**FREE Tier (Default)**
- 20 queries per day
- 3 auto-executions per day
- 1 snapshot
- Resets at midnight UTC

**PRO Tier**
- 100 queries per day
- 30 auto-executions per day
- 10 snapshots
- Resets at midnight UTC

**ENTERPRISE Tier**
- 1000 queries per day
- 500 auto-executions per day
- 100 snapshots
- Resets at midnight UTC

**Users cannot:**
- Edit config TOML to increase limits (sealed config prevents this)
- Use multiple license keys (only one active at a time)
- Share licenses (signed to user_id, but no hardware binding)

---

## Future Enhancements (Roadmap)

- [ ] Audit log of all license activations/removals
- [ ] Automatic expiry reminders (30 days, 7 days before)
- [ ] License revocation (for support/abuse cases)
- [ ] Admin dashboard (view active licenses, customers, usage)
- [ ] Auto-renewal system
- [ ] Per-team licensing (for large orgs)
- [ ] Feature flags beyond limits (e.g., "analytics", "api-access")
