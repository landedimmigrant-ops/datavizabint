#!/bin/bash
# push_to_github.sh
# -----------------
# Pushes to GitHub. Token is saved in .github_token — set it once, never paste again.
#
# FIRST TIME: run with your token to save it:
#   bash push_to_github.sh ghp_xxxxxxxxxxxx
#
# EVERY TIME AFTER: just run with no arguments:
#   bash push_to_github.sh
#
# To get a token: github.com → Settings → Developer settings
#   → Personal access tokens → Tokens (classic) → check "repo" scope

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOKEN_FILE="$SCRIPT_DIR/.github_token"

# If a token is passed as argument, save it for future use
if [ -n "$1" ]; then
  echo "$1" > "$TOKEN_FILE"
  chmod 600 "$TOKEN_FILE"
  echo "Token saved. Future pushes just need: bash push_to_github.sh"
fi

# Read token from file
if [ ! -f "$TOKEN_FILE" ]; then
  echo ""
  echo "Error: No token found."
  echo "Run once with your token to save it:"
  echo "  bash push_to_github.sh ghp_xxxxxxxxxxxx"
  echo ""
  exit 1
fi

TOKEN=$(cat "$TOKEN_FILE" | tr -d '[:space:]')
REPO="github.com/landedimmigrant-ops/datavizabint.git"

cd "$SCRIPT_DIR"
echo "Pushing to GitHub..."
git remote set-url origin "https://landedimmigrant-ops:${TOKEN}@${REPO}"
git push origin main
git remote set-url origin "https://github.com/landedimmigrant-ops/datavizabint.git"
echo ""
echo "Done. Live at: https://landedimmigrant-ops.github.io/datavizabint/"
