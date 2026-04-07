#!/bin/bash
# prepare-release.sh - Automate release preparation for Homebrew and WinGet

set -e

VERSION=${1:-}
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/prepare-release.sh <version>"
    echo "Example: ./scripts/prepare-release.sh 1.0.0"
    exit 1
fi

echo "Preparing release for Drift v$VERSION..."

# Step 1: Create GitHub release tag
echo "Step 1: Creating git tag..."
git tag "v$VERSION"
git push origin "v$VERSION"

# Step 2: Download tarball from GitHub
echo "Step 2: Downloading tarball..."
TARBALL="v${VERSION}.tar.gz"
TARBALL_URL="https://github.com/a-elhaag/driftshell/archive/refs/tags/v${VERSION}.tar.gz"
wget "$TARBALL_URL"

# Step 3: Calculate SHA256 for tarball
echo "Step 3: Calculating SHA256 for tarball..."
TARBALL_SHA256=$(sha256sum "$TARBALL" | awk '{print $1}')
echo "Tarball SHA256: $TARBALL_SHA256"

# Step 4: Build Windows executable
echo "Step 4: Building Windows executable..."
python -m pip install pyinstaller
pyinstaller --onefile --console driftshell/main.py -n drift

# Step 5: Calculate SHA256 for .exe
echo "Step 5: Calculating SHA256 for Windows executable..."
EXE_SHA256=$(sha256sum dist/drift.exe | awk '{print $1}')
echo "Executable SHA256: $EXE_SHA256"

# Step 6: Update Homebrew formula
echo "Step 6: Updating Homebrew formula..."
if [ -d "../homebrew-driftshell" ]; then
    sed -i "" "s|refs/tags/v[0-9.]*|refs/tags/v${VERSION}|g" Formula/drift.rb
    sed -i "" "s|sha256 \".*\"|sha256 \"${TARBALL_SHA256}\"|g" Formula/drift.rb

    cd ../homebrew-driftshell
    cp ../driftshell/Formula/drift.rb Formula/
    git add Formula/drift.rb
    git commit -m "Update drift to v$VERSION"
    git push origin main
    cd ../driftshell
    echo "✓ Updated homebrew-driftshell"
else
    echo "⚠ homebrew-driftshell not found at ../homebrew-driftshell"
    echo "  Update Formula/drift.rb manually:"
    echo "  - url: refs/tags/v$VERSION"
    echo "  - sha256: $TARBALL_SHA256"
fi

# Step 7: Update WinGet manifest
echo "Step 7: Updating WinGet manifest..."
sed -i "" "s|PackageVersion: [0-9.]*|PackageVersion: $VERSION|g" manifests/a-elhaag/driftshell/1.0.0.yaml
sed -i "" "s|refs/tags/v[0-9.]*|refs/tags/v${VERSION}|g" manifests/a-elhaag/driftshell/1.0.0.yaml
sed -i "" "s|InstallerSha256: .*|InstallerSha256: $EXE_SHA256|g" manifests/a-elhaag/driftshell/1.0.0.yaml

echo ""
echo "================================"
echo "Release v$VERSION ready!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Create GitHub release at: https://github.com/a-elhaag/driftshell/releases/tag/v$VERSION"
echo "2. Upload to release:"
echo "   - $TARBALL"
echo "   - dist/drift.exe"
echo "3. Commit WinGet manifest update:"
echo "   git add manifests/"
echo "   git commit -m 'Update to v$VERSION'"
echo "   git push"
echo "4. Update WinGet PR or create new one at: https://github.com/microsoft/winget-pkgs"
echo ""
echo "Tarball SHA256:   $TARBALL_SHA256"
echo "Executable SHA256: $EXE_SHA256"
