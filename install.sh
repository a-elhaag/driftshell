#!/bin/sh
set -e

# Drift installer
# Usage: curl -fsSL https://raw.githubusercontent.com/a-elhaag/driftshell/main/install.sh | sh

TAP="a-elhaag/driftshell"
FORMULA="drift"

printf "\033[1;34m\n  Installing Drift...\n\033[0m\n"

# Check Homebrew
if ! command -v brew >/dev/null 2>&1; then
    printf "\033[1;31mHomebrew not found.\033[0m\n"
    printf "Install it first: https://brew.sh\n"
    exit 1
fi

# Ensure fresh tap (remove stale local cache)
brew untap "$TAP" 2>/dev/null || true
rm -rf "$(brew --prefix)/Library/Taps/a-elhaag/homebrew-driftshell" 2>/dev/null || true
brew tap "$TAP"
brew install "$FORMULA"

printf "\n\033[1;32m✓ Drift installed!\033[0m\n\n"
printf "  Get started:\n"
printf "    \033[36mdrift\033[0m          — interactive mode\n"
printf "    \033[36md 'list files'\033[0m — quick query\n\n"
