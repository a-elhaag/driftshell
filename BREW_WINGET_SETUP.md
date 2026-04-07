# Drift: Homebrew & WinGet Setup

Quick start guide to get Drift on macOS/Linux (Homebrew) and Windows (WinGet).

---

## 🍺 Homebrew Setup (macOS/Linux)

### Create the Homebrew Tap

A "tap" is a custom Homebrew repository. Users will install from: `brew tap a-elhaag/driftshell`

```bash
# 1. Create new GitHub repo: homebrew-driftshell
#    https://github.com/a-elhaag/homebrew-driftshell
#    (Keep it public, no LICENSE needed for formulas)

# 2. Clone it locally
git clone https://github.com/a-elhaag/homebrew-driftshell.git
cd homebrew-driftshell

# 3. Create structure
mkdir -p Formula

# 4. Copy formula from driftshell repo
cp ../driftshell/Formula/drift.rb Formula/

# 5. Commit and push
git add Formula/drift.rb
git commit -m "Initial commit: Add drift formula"
git push -u origin main
```

### Generate SHA256 and Update Formula

Before your first release, calculate the checksum:

```bash
# After creating v1.0.0 release in driftshell repo:
wget https://github.com/a-elhaag/driftshell/archive/refs/tags/v1.0.0.tar.gz

# Calculate SHA256
sha256sum v1.0.0.tar.gz
# Output: abc123def456...

# Update Formula/drift.rb in homebrew-driftshell:
# Replace sha256 "placeholder_sha256" with sha256 "abc123def456..."

cd ../homebrew-driftshell
sed -i '' 's/sha256 "placeholder_sha256"/sha256 "abc123def456..."/g' Formula/drift.rb
git add Formula/drift.rb
git commit -m "Add SHA256 for v1.0.0"
git push
```

### Test Locally

```bash
# Test before pushing to users
brew tap a-elhaag/driftshell ../homebrew-driftshell

# Uninstall if needed
brew untap a-elhaag/driftshell
```

### Users Install

```bash
brew tap a-elhaag/driftshell
brew install drift
```

---

## 🪟 WinGet Setup (Windows)

### Prepare Windows Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone executable
pyinstaller --onefile --console driftshell/main.py -n drift

# You'll get: dist/drift.exe

# Calculate SHA256
sha256sum dist/drift.exe  # or on Windows: certUtil -hashfile dist\drift.exe SHA256
# Output: def456abc123...
```

### Submit to WinGet

```bash
# 1. Fork microsoft/winget-pkgs
#    https://github.com/microsoft/winget-pkgs

# 2. Clone your fork
git clone https://github.com/a-elhaag/winget-pkgs.git
cd winget-pkgs
git checkout -b feature/add-driftshell

# 3. Copy manifest to correct location
mkdir -p manifests/a-elhaag/driftshell/1.0.0
cp ../driftshell/manifests/a-elhaag/driftshell/1.0.0.yaml \
   manifests/a-elhaag/driftshell/1.0.0.yaml

# 4. Update manifest with SHA256 and exe URL
# Edit manifests/a-elhaag/driftshell/1.0.0.yaml:
#   - InstallerSha256: def456abc123...
#   - InstallerUrl: https://github.com/a-elhaag/driftshell/releases/download/v1.0.0/drift.exe

# 5. Commit and push
git add manifests/a-elhaag/
git commit -m "Add drift package"
git push -u origin feature/add-driftshell
```

### Create GitHub Release

Before WinGet can install, upload the files:

```bash
# Create release v1.0.0 in driftshell repo
# Upload to release:
#   - driftshell-1.0.0.tar.gz (from releases page)
#   - dist/drift.exe (Windows executable)

# Release URL: https://github.com/a-elhaag/driftshell/releases/tag/v1.0.0
```

### Submit PR to Microsoft

Open a pull request:
```
https://github.com/microsoft/winget-pkgs/compare/main...a-elhaag:winget-pkgs:feature/add-driftshell
```

Microsoft will validate. Once approved:

### Users Install

```powershell
winget install a-elhaag.driftshell
```

---

## 🚀 Automated Release Process

Use the release script to automate SHA256 calculation and updates:

```bash
./scripts/prepare-release.sh 1.0.0
```

This will:
1. Tag v1.0.0 in git
2. Download and calculate tarball SHA256
3. Build Windows .exe
4. Calculate .exe SHA256
5. Update both Formula and WinGet manifest
6. Push to homebrew-driftshell

Then manually:
1. Create GitHub release with tarball and .exe
2. Update WinGet PR with finalized manifest

---

## 📋 Checklist for v1.0.0

- [ ] Create `homebrew-driftshell` GitHub repo
- [ ] Copy `Formula/drift.rb` to tap
- [ ] Create driftshell v1.0.0 release with tarball
- [ ] Calculate tarball SHA256 and update formula
- [ ] Build `drift.exe` with PyInstaller
- [ ] Upload `drift.exe` to GitHub release
- [ ] Calculate exe SHA256
- [ ] Update WinGet manifest with SHA256 and exe URL
- [ ] Fork `microsoft/winget-pkgs`
- [ ] Add manifest to fork and create PR
- [ ] Wait for Microsoft approval (usually 2-7 days)

---

## 📝 File Locations

| File | Location | Purpose |
|------|----------|---------|
| `Formula/drift.rb` | `homebrew-driftshell/Formula/` | Homebrew formula |
| `manifests/a-elhaag/driftshell/1.0.0.yaml` | `winget-pkgs/manifests/` | WinGet manifest |
| `prepare-release.sh` | `driftshell/scripts/` | Automation script |

---

## 💡 Tips

- **Homebrew updates**: Just update formula in tap, no new approval needed
- **WinGet updates**: Update manifest in PR or create new one
- **Test locally**: `brew tap ../homebrew-driftshell` before submitting
- **Validate WinGet**: Microsoft checks for common issues automatically

---

## 🔗 Links

- **Your Repos**: 
  - Main: https://github.com/a-elhaag/driftshell
  - Homebrew: https://github.com/a-elhaag/homebrew-driftshell (create this)
- **Official**:
  - Homebrew: https://brew.sh
  - WinGet: https://github.com/microsoft/winget-pkgs
  - PyInstaller: https://pyinstaller.org

---

## ❓ Troubleshooting

**Homebrew formula not found:**
```bash
brew tap a-elhaag/driftshell --full
```

**WinGet validation fails:**
- Check manifest YAML is valid: `powershell -NoProfile -Command "Get-Content manifests/.../1.0.0.yaml | ConvertFrom-Json"`
- Ensure SHA256 is correct (not truncated)
- InstallerUrl must be publicly accessible

**SHA256 mismatch:**
- Recalculate with: `sha256sum filename` (macOS/Linux) or `certUtil -hashfile filename SHA256` (Windows)
- Update manifest and test download
