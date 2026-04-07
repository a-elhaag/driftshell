# Drift v1.0.0 Release Status

## ✅ Completed

### Homebrew (macOS/Linux)
- ✅ Created homebrew-driftshell tap: https://github.com/a-elhaag/homebrew-driftshell
- ✅ Added Formula/drift.rb to tap
- ✅ Calculated SHA256 for tarball: `0019dfc4b32d63c1392aa264aed2253c1e0c2fb09216f8e2cc269bbfb8bb49b5`
- ✅ Updated formula with real SHA256

**Users can install with:**
```bash
brew tap a-elhaag/driftshell
brew install drift
```

### GitHub Release
- ✅ Created v1.0.0 tag
- ✅ Tarball available at: https://github.com/a-elhaag/driftshell/archive/refs/tags/v1.0.0.tar.gz

---

## ⏳ Pending

### Windows / WinGet

#### Step 1: GitHub Actions Build
The workflow will automatically build `drift.exe` when code is pushed.

**Next:** Push a commit or wait for next release cycle.

#### Step 2: Update WinGet Manifest
Once `drift.exe` is available in releases, run:
```bash
./scripts/update-winget-sha256.sh 1.0.0
```

#### Step 3: Submit to Microsoft
1. Fork https://github.com/microsoft/winget-pkgs
2. Add manifest to fork
3. Create PR to microsoft/winget-pkgs
4. Wait for approval (2-7 days)

**Users will install with:**
```powershell
winget install a-elhaag.driftshell
```

---

## 📋 Verification

### Test Homebrew (local)
```bash
brew tap a-elhaag/driftshell
brew install drift
drift --version
```

### Manual Release Creation (if needed)
Create a GitHub release with release notes:
1. Go to https://github.com/a-elhaag/driftshell/releases
2. Click "Create a new release"
3. Tag: `v1.0.0`
4. Title: `Drift v1.0.0`
5. Body:
```markdown
## Features
- HMAC-signed license keys
- Sealed configuration prevents runtime limit edits
- Free/Pro/Enterprise tiers
- CLI management (activate, status, remove)

## Installation

### macOS/Linux (Homebrew)
```bash
brew tap a-elhaag/driftshell
brew install drift
```

### Windows (WinGet) - Coming Soon
```powershell
winget install a-elhaag.driftshell
```

### All Platforms (pip)
```bash
pip install driftshell
```

## Changes
- Free tier: 20 daily commands (up from 10)
- Pro tier: 100 daily commands, 30 auto-execs, 10 snapshots
- Enterprise tier: 1000 daily commands, 500 auto-execs, 100 snapshots
```

---

## 🎯 Next Steps

1. **Homebrew**: Already live! Users can install now.
2. **WinGet**: 
   - [ ] GitHub Actions builds drift.exe (automatic)
   - [ ] Run `./scripts/update-winget-sha256.sh 1.0.0`
   - [ ] Fork microsoft/winget-pkgs and submit PR

---

## 📍 Quick Links

- **Main repo:** https://github.com/a-elhaag/driftshell
- **Homebrew tap:** https://github.com/a-elhaag/homebrew-driftshell
- **v1.0.0 release:** https://github.com/a-elhaag/driftshell/releases/tag/v1.0.0
- **WinGet repo:** https://github.com/microsoft/winget-pkgs
