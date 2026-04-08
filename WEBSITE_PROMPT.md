# Drift Website — Full Product Prompt

## What You're Building

A marketing + account portal website for **Drift** (`driftshell`), a privacy-first CLI tool that converts plain English into shell commands using locally-run LLMs (Ollama). No cloud inference, no API keys — everything runs on the user's machine.

**Stack:** Next.js 15 (App Router), TypeScript, Tailwind CSS v4, shadcn/ui, Framer Motion

**Domain:** `driftshell.dev`

---

## Product Context

Drift is installed via:
```bash
pip install driftshell
```

CLI alias: `drift` or `d`

**Core value prop:** Type what you want in plain English, Drift generates and optionally runs the shell command — entirely locally, no data leaves your machine.

**Example interaction:**
```
d [~/Projects/myapp] > delete all node_modules folders recursively
  Command: find . -type d -name "node_modules" -exec rm -rf {} +
  Risk: medium — Run? [y/N]: y
  Done.
```

**Key features:**
- Natural language → shell command (via Gemma 4, auto-selected by hardware)
- `--explain` mode: shows command + plain English breakdown before running
- `--dry-run` / `-n`: shows command, never executes
- 3-layer safety gate: blocklist → LLM risk scorer → user confirmation
- `drift undo`: snapshot-based rollback of the last destructive command
- `drift history`: full audit log (SQLite, local)
- Interactive REPL: `drift` or `d` alone launches a persistent shell session
- Hardware-aware model routing: auto-picks Gemma 4 31B / 26B MoE / E4B based on VRAM/RAM
- HMAC-signed license keys, sealed config (tamper-proof limits enforcement)

---

## Brand Identity

### Color Tokens

| Token | Hex | Role |
|-------|-----|------|
| `drift-blue` | `#58a6ff` | Primary accent, CTAs, links, highlights |
| `drift-green` | `#3fb950` | Success, low-risk, "safe" badges |
| `drift-amber` | `#d29922` | Warnings, mid-risk, caution states |
| `drift-red` | `#f85149` | Errors, destructive, high-risk |
| `drift-muted` | `#8b949e` | Secondary text, captions, placeholders |

### Background Palette

| Use | Value |
|-----|-------|
| Page background | `#0d1117` (GitHub dark — near-black) |
| Card / panel surface | `#161b22` |
| Border / separator | `#21262d` |
| Subtle hover | `#1c2128` |
| Input background | `#0d1117` |

### Typography
- **Display / headings:** `Inter` or `Cal Sans` — clean, technical, no serifs
- **Monospace (code blocks, CLI demos):** `JetBrains Mono` or `Fira Code`
- Heading weight: 700–800
- Body: 400–500, `#c9d1d9` (GitHub text color on dark)

### Tone
- Developer-first. Direct, no fluff. No buzzwords like "AI-powered" or "cutting-edge".
- Copy feels like it was written by a senior engineer who is slightly annoyed by cloud-first tools.
- Emphasis: **local**, **private**, **yours**.

### Logo / Wordmark
- ASCII-art inspired `DRIFT` wordmark rendered in `drift-blue`
- Use a terminal-style render for hero: monospaced, uppercase, sharp
- Can be a stylized `D>` glyph for favicon / icon contexts

---

## Site Architecture

### Pages

#### 1. `/` — Landing Page
The main marketing page. Sections:

**Hero**
- Headline: `"Shell commands, in plain English."` (or similar — keep it under 6 words, punchy)
- Sub: `"Drift runs on your machine. No cloud. No API key. No data leaves."` 
- Two CTAs: `[Install Free]` (primary, drift-blue) + `[See the docs]` (ghost/outline)
- Background: terminal window animation showing a live `d [~/Projects] >` session with a few example queries typewriting in. Commands auto-execute with green checkmarks.

**How it works** (3-step visual)
1. Type what you want → `find all files larger than 100MB`
2. Drift generates the command → `find . -size +100M -type f`
3. Review, confirm, done → with optional `--explain` breakdown shown

**Features grid** (6 cells, icon + title + 1-line description)
- Local LLMs only — Gemma 4 auto-selected by your hardware. Nothing leaves your terminal.
- 3-layer safety — Blocklist + LLM risk scorer + confirmation gate before anything destructive runs.
- Snapshot undo — `drift undo` rolls back the last destructive command instantly.
- Explain mode — `--explain` shows the command and a plain-English breakdown before execution.
- Full audit log — Every command logged locally in SQLite. Your history, forever.
- REPL mode — `drift` alone opens a persistent shell session with context memory.

**Terminal demo block**
- Large dark terminal panel, syntax-highlighted, shows a multi-step session:
  ```
  d [~/Projects/api] > show me disk usage for each folder
    Command: du -sh */
    Risk: low — executing...
    156M   node_modules
    42M    dist
    8.2M   src

  d [~/Projects/api] > delete node_modules
    Command: rm -rf node_modules
    Risk: high — irreversible file deletion
    Run? [y/N]: y
    Done. Snapshot saved → drift undo to restore.
  ```

**Model routing section**
- Title: `"Runs on your hardware, whatever it is."`
- Table showing auto-selection: VRAM ≥ 16GB → Gemma 4 31B / VRAM ≥ 8GB → Gemma 4 26B MoE / Anything else → Gemma 4 E4B
- Copy: `"Drift detects your VRAM and RAM at startup and picks the best model that fits. Override anytime in config."`

**Pricing** (abbreviated — full page at `/pricing`)
- Three-card preview: Free / Pro / Enterprise
- CTA: `[See full pricing]`

**Install section**
```bash
pip install driftshell
drift "list all git repos in my home folder"
```
- Dark code block, copy button, drift-blue accent

**Footer**
- Links: Docs, GitHub, Pricing, Status, Privacy
- `© 2026 Drift. Apache 2.0 open source.`

---

#### 2. `/pricing` — Pricing Page

Three tiers displayed as cards, Pro highlighted (border in drift-blue, "Most Popular" badge):

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| Daily queries | 20 | 100 | 1,000 |
| Auto-exec / day | 3 | 30 | 500 |
| Snapshots | 1 | 10 | 100 |
| Explain mode | ✓ | ✓ | ✓ |
| Dry-run mode | ✓ | ✓ | ✓ |
| Priority support | — | ✓ | ✓ |
| Team seats | — | — | Custom |

**Pricing (suggested — fill in real amounts):**
- Free: $0 / forever
- Pro: $9 / month or $79 / year
- Enterprise: Contact us

**CTA per card:**
- Free: `[Install Free]` → pip install command
- Pro: `[Get Pro]` → `/checkout?plan=pro`
- Enterprise: `[Contact us]` → mailto or form

**Below cards:**
- FAQ accordion (5–6 items):
  - "Does Drift send my data anywhere?" → No. All inference is local via Ollama.
  - "What happens when my trial expires?" → You revert to Free tier automatically. No interruption.
  - "How does the license work?" → You get a signed key via email. Run `drift license activate <key>`.
  - "Can I use Drift on multiple machines?" → Yes, activate the same key on each machine.
  - "What's the refund policy?" → 14-day money-back, no questions asked.
  - "Is there a student / OSS discount?" → Email us.

---

#### 3. `/account` — User Account Dashboard

Requires authentication. Shows:

**Sidebar navigation:**
- Overview
- License & Subscription
- Usage
- Settings
- Billing History

**Overview panel:**
- Welcome back, `{name}`
- Current plan badge (Free / Pro / Enterprise in matching color)
- Quick stats: queries today, auto-execs today, snapshots used
- Quick action: `[Upgrade]` if on Free

**License & Subscription panel:**
- Active license info:
  - Plan: PRO
  - Email: user@example.com
  - Issued: 2026-04-07
  - Expires: 2027-04-07
  - Days remaining: progress bar
- License key (blurred, with `[Reveal]` toggle + `[Copy]` button)
- Activate a new key: text input + `[Activate]` button
- Danger zone: `[Cancel subscription]` (red, behind confirmation modal)

**Usage panel:**
- Daily query usage: `47 / 100` progress bar in drift-blue
- Auto-exec usage: `12 / 30` progress bar
- Snapshots: `3 / 10` progress bar
- Reset time: "Resets in 6h 22m"

**Settings panel:**
- Change email
- Change password
- Delete account (danger zone, red)

**Billing History panel:**
- Table: Date | Plan | Amount | Status | Invoice
- Download invoice link per row

---

#### 4. `/checkout` — Purchase Flow

Query params: `?plan=pro&billing=monthly` (or `annual`)

**Steps:**
1. Plan confirmation card (what they're buying, price, features)
2. Email + password (or "Sign in" if existing account)
3. Payment (Stripe Elements — card number, expiry, CVC)
4. Confirm + pay

**Post-payment:**
- Show generated license key in a large monospaced block
- `[Copy key]` button
- Instructions: `drift license activate "<key>"`
- Email confirmation sent

---

#### 5. `/docs` — Documentation (optional, can be external)

If included, use a sidebar doc layout:
- Getting Started
- Installation
- Commands Reference (`drift ask`, `drift undo`, `drift history`, `drift license`, `drift settings`, `drift status`)
- Model Selection
- Safety System
- Configuration (`~/.drift/config.toml`)
- Licensing & Plans
- Troubleshooting

---

#### 6. `/login` and `/signup`

- Minimal, centered card layout
- Email + password fields
- Drift wordmark at top in drift-blue
- Dark background (#0d1117)
- "Forgot password?" link
- OAuth optional: `[Continue with GitHub]`

---

## Component Design Notes

### Terminal / Code Block Component
- Background: `#0d1117` or `#161b22`
- Top bar: traffic-light dots (decorative) + `drift — zsh` title
- Prompt line: `d [path] >` in `#58a6ff`
- Command text: `#c9d1d9`
- Output: `#8b949e`
- Success indicator: `#3fb950`
- Risk badge: amber or red depending on risk level
- Typewriter animation for hero demo (use Framer Motion or a lightweight typewriter lib)

### Plan Cards
- Background: `#161b22`
- Border: `#21262d` (default), `#58a6ff` (Pro/highlighted)
- Feature check icons: `#3fb950`
- Missing feature: `#8b949e` dash
- CTA button: filled drift-blue for primary, outline for secondary

### Progress bars
- Track: `#21262d`
- Fill: `#58a6ff` (normal), `#d29922` (>80%), `#f85149` (>95%)
- Rounded, height 6px

### Badges
- Free: `#8b949e` text, `#21262d` bg
- Pro: `#58a6ff` text, `rgba(88,166,255,0.1)` bg
- Enterprise: `#d29922` text, `rgba(210,153,34,0.1)` bg

### Buttons
- Primary: `bg-[#58a6ff] text-[#0d1117] font-semibold hover:bg-[#79b8ff]`
- Ghost: `border border-[#21262d] text-[#c9d1d9] hover:bg-[#1c2128]`
- Danger: `bg-[#f85149] text-white hover:bg-[#ff6b6b]`
- All buttons: `rounded-md px-4 py-2 text-sm transition-colors`

---

## Authentication

Use **Clerk** or **NextAuth.js** (your choice). The account portal requires a session. The marketing pages (landing, pricing, docs) are public.

Protect these routes:
- `/account/*`
- `/checkout` (email capture at minimum)

---

## Backend / API Routes (Next.js API or separate service)

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/license/generate` | POST | Internal: generate HMAC-signed key (admin only) |
| `/api/license/validate` | POST | Verify a key is valid (for dashboard display) |
| `/api/checkout/session` | POST | Create Stripe checkout session |
| `/api/webhooks/stripe` | POST | Handle payment events, provision license key |
| `/api/account/usage` | GET | Fetch usage stats for dashboard |
| `/api/account/license` | GET/DELETE | Get or revoke active license |

**License key generation** uses the same HMAC-SHA256 logic as the CLI:
```
key = base64(json_payload) + "." + hmac_sha256(DRIFT_LICENSE_SECRET, json_payload)
```
Master secret comes from env var `DRIFT_LICENSE_SECRET`.

---

## Animations & Motion

- Hero terminal: typewriter effect, commands appear one by one with realistic delay
- Section entrance: fade-up on scroll (Framer Motion `whileInView`)
- Pricing card hover: subtle scale (1.02) + border glow in drift-blue
- Plan card toggle (monthly/annual): smooth pill slider
- Progress bars: animate fill on mount
- Page transitions: fade between routes (Next.js layout transition)

Keep animations subtle. This is a developer tool — no confetti, no excessive motion.

---

## SEO & Meta

- Title: `Drift — Plain English Shell Commands`
- Description: `"Local AI shell assistant. Type what you want, Drift runs the command. No cloud. No API key."`
- OG image: terminal screenshot with the DRIFT wordmark and a live session
- Twitter card: `summary_large_image`
- Canonical: `https://driftshell.dev`

---

## File / Folder Structure (suggested)

```
app/
  (marketing)/
    page.tsx            ← landing
    pricing/page.tsx
    docs/page.tsx
  (auth)/
    login/page.tsx
    signup/page.tsx
  (portal)/
    account/
      page.tsx          ← overview
      license/page.tsx
      usage/page.tsx
      settings/page.tsx
      billing/page.tsx
    checkout/page.tsx
  api/
    license/
      generate/route.ts
      validate/route.ts
    checkout/session/route.ts
    webhooks/stripe/route.ts
    account/
      usage/route.ts
      license/route.ts
components/
  terminal/
    TerminalWindow.tsx
    TypewriterDemo.tsx
  pricing/
    PlanCard.tsx
    PricingToggle.tsx
    FeatureRow.tsx
  account/
    UsageBar.tsx
    LicensePanel.tsx
    BillingTable.tsx
  ui/                   ← shadcn generated
lib/
  license.ts            ← HMAC signing/validation (mirrors CLI logic)
  stripe.ts
  auth.ts
  db.ts                 ← Postgres or SQLite for users/licenses
styles/
  globals.css           ← Tailwind + CSS custom properties
```

---

## Tailwind Config Additions

```js
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      drift: {
        blue:    '#58a6ff',
        green:   '#3fb950',
        amber:   '#d29922',
        red:     '#f85149',
        muted:   '#8b949e',
        bg:      '#0d1117',
        surface: '#161b22',
        border:  '#21262d',
        hover:   '#1c2128',
        text:    '#c9d1d9',
      }
    },
    fontFamily: {
      mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      sans: ['Inter', 'system-ui', 'sans-serif'],
    }
  }
}
```

---

## Copy / Messaging Cheat Sheet

| Context | Copy |
|---------|------|
| Hero headline | "Shell commands, in plain English." |
| Hero subheadline | "Drift runs on your machine. No cloud. No API key. No data leaves." |
| Install CTA | "Install free — `pip install driftshell`" |
| Privacy badge | "100% local. Zero telemetry." |
| Free plan card | "Start for free. No credit card required." |
| Pro plan card | "For developers who live in the terminal." |
| Enterprise card | "For teams. Volume limits, team seats, priority support." |
| License activate | "Run `drift license activate <your-key>` in any terminal." |
| Upgrade nudge | "You've used 20/20 daily queries. Upgrade to Pro for 100/day." |
| Expiry warning | "Your Pro license expires in 7 days. Renew to keep your limits." |

---

## Do Not

- Do not use light mode as the default. Dark only, matching the CLI aesthetic.
- Do not use rounded-full pill buttons — use `rounded-md`.
- Do not add gradients on primary CTAs — flat `#58a6ff` fill only.
- Do not use purple, teal, or pink anywhere — only the 5 brand tokens above.
- Do not use stock photos — terminal screenshots, code blocks, and abstract dark UI only.
- Do not write marketing copy with adjectives like "powerful", "seamless", "robust", or "cutting-edge".

---

## Environment Variables Needed

```bash
# Auth
NEXTAUTH_SECRET=
NEXTAUTH_URL=https://driftshell.dev

# Stripe
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=

# License signing (must match CLI master secret)
DRIFT_LICENSE_SECRET=

# Database
DATABASE_URL=

# Optional: Clerk (if using Clerk instead of NextAuth)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
```
