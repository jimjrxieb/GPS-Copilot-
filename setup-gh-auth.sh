#!/bin/bash
# Quick GitHub CLI authentication using token from .env

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔐 Setting up GitHub CLI authentication..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "Copy .env.example to .env and add your GITHUB_TOKEN"
    exit 1
fi

# Extract token
GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" .env | cut -d'=' -f2)

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not found in .env"
    exit 1
fi

echo "✓ Found GITHUB_TOKEN in .env"
echo ""

# Authenticate gh CLI using token
echo "$GITHUB_TOKEN" | gh auth login --with-token

echo ""
echo "✅ GitHub CLI authenticated!"
echo ""

# Verify authentication
gh auth status

echo ""
echo "🎉 You're ready to use jade explain-gha!"
echo ""
echo "Try:"
echo "  jade explain-gha jimjrxieb/CLOUD-project 18300191954"
echo ""