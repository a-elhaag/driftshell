#!/bin/bash
# Update WinGet manifest with actual SHA256 from built executable

VERSION=${1:-}
if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/update-winget-sha256.sh <version>"
    echo "Example: ./scripts/update-winget-sha256.sh 1.0.0"
    exit 1
fi

MANIFEST="manifests/a-elhaag/driftshell/${VERSION}.yaml"
DOWNLOAD_URL="https://github.com/a-elhaag/driftshell/releases/download/v${VERSION}/drift.exe"

# Download the .exe and calculate SHA256
echo "Downloading $DOWNLOAD_URL..."
curl -L -o /tmp/drift.exe "$DOWNLOAD_URL"

# Calculate SHA256
EXE_SHA256=$(sha256sum /tmp/drift.exe | awk '{print $1}')
echo "SHA256: $EXE_SHA256"

# Update manifest
echo "Updating $MANIFEST..."
sed -i '' "s/InstallerSha256: .*/InstallerSha256: $EXE_SHA256/g" "$MANIFEST"

echo "✓ Updated $MANIFEST with SHA256"
echo ""
echo "Commit and push:"
echo "  git add $MANIFEST"
echo "  git commit -m 'Update WinGet manifest SHA256 for v$VERSION'"
echo "  git push"

# Clean up
rm -f /tmp/drift.exe
