# WinGet Submission Guide for Drift

Submit Drift to the Windows Package Manager (WinGet).

---

## Step 1: Create v1.0.0 Release (5 minutes)

1. Go to https://github.com/a-elhaag/driftshell/releases
2. Click "Create a new release"
3. **Tag:** `v1.0.0`
4. **Release name:** `Drift v1.0.0`
5. Click "Publish release"

The GitHub Actions workflow will automatically build `drift.exe` and upload it to the release.

**Wait for the workflow to complete** (check Actions tab):
- https://github.com/a-elhaag/driftshell/actions

---

## Step 2: Update WinGet Manifest with SHA256 (2 minutes)

Once the release is ready and `drift.exe` is uploaded:

```bash
./scripts/update-winget-sha256.sh 1.0.0
```

This automatically:
1. Downloads `drift.exe` from the release
2. Calculates SHA256
3. Updates `manifests/a-elhaag/driftshell/1.0.0.yaml`

Then commit and push:

```bash
git add manifests/
git commit -m "Update WinGet manifest with SHA256 for v1.0.0"
git push
```

---

## Step 3: Fork microsoft/winget-pkgs (1 minute)

1. Go to https://github.com/microsoft/winget-pkgs
2. Click "Fork"
3. Clone your fork:

```bash
git clone https://github.com/a-elhaag/winget-pkgs.git
cd winget-pkgs
git checkout -b feature/add-driftshell
```

---

## Step 4: Add Manifest to Fork (2 minutes)

```bash
# Create directory structure
mkdir -p manifests/a-elhaag/driftshell/1.0.0

# Copy manifest from your main repo
cp ../driftshell/manifests/a-elhaag/driftshell/1.0.0.yaml \
   manifests/a-elhaag/driftshell/1.0.0.yaml

# Commit and push
git add manifests/a-elhaag/
git commit -m "Add drift package for WinGet"
git push -u origin feature/add-driftshell
```

---

## Step 5: Create Pull Request (2 minutes)

1. Go to your fork: https://github.com/a-elhaag/winget-pkgs
2. You should see a banner with "Compare & pull request"
3. Click it, or go to: https://github.com/microsoft/winget-pkgs/compare/main...a-elhaag:winget-pkgs:feature/add-driftshell
4. Review the changes (should be just your manifest)
5. Click "Create pull request"

**PR Title:** `Add drift package`
**PR Body:**
```
Submitting the Drift CLI package for inclusion in WinGet.

Drift is a local CLI that translates natural language to shell commands via Ollama (no cloud inference).

- Package: a-elhaag.driftshell
- Version: 1.0.0
- Platform: Windows x64
- Installer type: Portable executable

https://github.com/a-elhaag/driftshell
```

---

## Step 6: Microsoft Review & Approval (2-7 days)

Microsoft will:
1. Check YAML syntax
2. Validate SHA256 checksum
3. Test the installer
4. Check for policies

You may get comments. Common issues:
- **Invalid SHA256:** Recalculate with `./scripts/update-winget-sha256.sh 1.0.0`
- **URL unreachable:** Ensure release is public
- **Manifest syntax:** Fix any YAML issues

Once approved, your PR will be merged.

---

## Step 7: Users Can Install

After approval, users on Windows can install with:

```powershell
winget install a-elhaag.driftshell
```

---

## Full Checklist

- [ ] Create v1.0.0 release in driftshell repo
- [ ] GitHub Actions builds drift.exe (check Actions tab)
- [ ] drift.exe appears in release assets
- [ ] Run `./scripts/update-winget-sha256.sh 1.0.0`
- [ ] Verify SHA256 is updated in manifest
- [ ] Commit and push manifest update
- [ ] Fork microsoft/winget-pkgs
- [ ] Add manifest to fork
- [ ] Create PR to microsoft/winget-pkgs
- [ ] Wait for approval (2-7 days)
- [ ] PR merged ✓

---

## Troubleshooting

### Workflow didn't build drift.exe

Check Actions tab: https://github.com/a-elhaag/driftshell/actions

Look for the "Build Windows Executable" workflow. If it failed:
- Common issue: Missing dependencies in build
- Solution: Update `build-windows.yml` or install deps manually

### SHA256 mismatch

Recalculate:
```bash
./scripts/update-winget-sha256.sh 1.0.0
```

If the script fails, download manually:
```bash
curl -L -o drift.exe https://github.com/a-elhaag/driftshell/releases/download/v1.0.0/drift.exe
sha256sum drift.exe
# Update manifest manually
```

### PR stuck in review

Leave a comment in the PR asking for feedback. Microsoft volunteers review community submissions, so be patient and helpful.

---

## For Future Releases

For v1.0.1, v1.1.0, etc., repeat these steps:

1. Create release tag (workflow builds .exe)
2. Run `./scripts/update-winget-sha256.sh 1.0.1`
3. Update manifest to new version
4. Fork microsoft/winget-pkgs again or push to existing PR
5. Submit new PR or update existing

---

## Quick Links

- **Your repo:** https://github.com/a-elhaag/driftshell
- **WinGet repo:** https://github.com/microsoft/winget-pkgs
- **Your fork:** https://github.com/a-elhaag/winget-pkgs
- **Manifest location:** `manifests/a-elhaag/driftshell/1.0.0.yaml`
