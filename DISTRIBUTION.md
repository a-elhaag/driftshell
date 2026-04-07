# Drift Distribution Setup

This document explains how to set up Drift for distribution via Homebrew and WinGet.

---

## Part 1: Homebrew (macOS/Linux)

### Step 1: Create Homebrew Tap Repository

A Homebrew "tap" is a custom repository that users can install from.

```bash
# Create a new GitHub repository called "homebrew-driftshell"
# At: https://github.com/a-elhaag/homebrew-driftshell

# Clone it locally
git clone https://github.com/a-elhaag/homebrew-driftshell.git
cd homebrew-driftshell

# Create the Formula directory
mkdir -p Formula

# Copy the formula from your main repo
cp ../driftshell/Formula/drift.rb Formula/

# Commit and push
git add Formula/drift.rb
git commit -m "Add drift formula"
git push -u origin main
```

### Step 2: Generate SHA256 for Release

Before users can install, you need to create a GitHub release and calculate the SHA256 hash:

```bash
# After creating a GitHub release (v1.0.0), download the tarball
wget https://github.com/a-elhaag/driftshell/archive/refs/tags/v1.0.0.tar.gz

# Calculate SHA256
sha256sum v1.0.0.tar.gz
# Output: abc123def456...

# Update Formula/drift.rb with the real SHA256
# Edit homebrew-driftshell/Formula/drift.rb and replace "placeholder_sha256"
```

### Step 3: Users Install With

```bash
brew tap a-elhaag/driftshell
brew install drift
```

### Update Homebrew Formula on New Releases

When you release a new version:

```bash
cd homebrew-driftshell

# Update Formula/drift.rb:
# 1. Change version in url: refs/tags/vX.Y.Z
# 2. Update sha256 (calculated from release tarball)
# 3. Commit and push

git add Formula/drift.rb
git commit -m "Update drift to vX.Y.Z"
git push
```

---

## Part 2: WinGet (Windows)

### Step 1: Fork WinGet Community Repository

```bash
# Fork https://github.com/microsoft/winget-pkgs
# Clone your fork
git clone https://github.com/a-elhaag/winget-pkgs.git
cd winget-pkgs

# Create feature branch
git checkout -b feature/add-driftshell
```

### Step 2: Create WinGet Manifest

The manifest is already in your main repo at `manifests/a-elhaag/driftshell/1.0.0.yaml`.

Create the same structure in your winget-pkgs fork:

```bash
mkdir -p manifests/a-elhaag/driftshell/1.0.0

# Copy manifest
cp ../../driftshell/manifests/a-elhaag/driftshell/1.0.0.yaml \
   manifests/a-elhaag/driftshell/1.0.0/
```

### Step 3: Generate SHA256 for Windows Executable

You'll need to build a Windows executable or create a Python wrapper:

**Option A: Python-based executable (recommended)**

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --console driftshell/main.py -n drift

# Calculate SHA256 of the .exe
sha256sum dist/drift.exe
# Output: def456abc123...

# Update the manifest with this SHA256
# Edit manifests/a-elhaag/driftshell/1.0.0.yaml
# Replace InstallerSha256: placeholder_sha256 with the real hash
```

**Option B: Upload to GitHub Releases**

```bash
# Build the executable
pyinstaller --onefile --console driftshell/main.py -n drift

# Create a GitHub release (v1.0.0) in driftshell repo
# Upload dist/drift.exe to the release

# The release download URL will be:
# https://github.com/a-elhaag/driftshell/releases/download/v1.0.0/drift.exe

# Update manifest InstallerUrl with this
```

### Step 4: Submit PR to Microsoft

```bash
# Commit your manifest
git add manifests/a-elhaag/driftshell/
git commit -m "Add drift package for WinGet"
git push -u origin feature/add-driftshell

# Open a PR to microsoft/winget-pkgs
# URL: https://github.com/microsoft/winget-pkgs/pull/new/main
```

Microsoft will validate your manifest. Once approved:

### Step 5: Users Install With

```powershell
winget install a-elhaag.driftshell
```

---

## Checklist

### Before First Release

- [ ] Create GitHub release v1.0.0 with tarball
- [ ] Calculate SHA256 for tarball
- [ ] Update `Formula/drift.rb` with SHA256
- [ ] Create `homebrew-driftshell` repository
- [ ] Push formula to homebrew-driftshell
- [ ] Build Windows executable (PyInstaller)
- [ ] Calculate SHA256 for .exe
- [ ] Upload .exe to GitHub release
- [ ] Update WinGet manifest with SHA256 and exe URL
- [ ] Fork `winget-pkgs` and add manifest
- [ ] Submit PR to microsoft/winget-pkgs

### For Each New Release

- [ ] Tag release in git: `git tag v1.0.1 && git push --tags`
- [ ] Create GitHub release with tarball and .exe
- [ ] Calculate SHA256 hashes
- [ ] Update both Formula/drift.rb and WinGet manifest
- [ ] Push formula update to homebrew-driftshell
- [ ] Update WinGet PR or submit new one

---

## Quick Links

- **Homebrew Tap**: https://github.com/a-elhaag/homebrew-driftshell
- **Main Repo**: https://github.com/a-elhaag/driftshell
- **WinGet Repo**: https://github.com/microsoft/winget-pkgs
- **PyInstaller Docs**: https://pyinstaller.org/en/stable/
