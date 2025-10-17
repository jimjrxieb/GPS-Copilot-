#!/bin/bash
# Simple scan and fix workflow
# Usage: ./scan-and-fix.sh <project-name>

if [ -z "$1" ]; then
    echo "Usage: $0 <project-name>"
    echo "Example: $0 Portfolio"
    exit 1
fi

PROJECT="$1"
GP_COPILOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
cd "$GP_COPILOT_ROOT"

echo "🎯 Scanning and fixing: $PROJECT"
echo "=================================="

# Step 1: Scan
echo "📊 Step 1: Scanning..."
./gp-security scan "GP-PROJECTS/$PROJECT"

# Step 2: Fix
echo "🔧 Step 2: Applying fixes..."
./gp-security fix "GP-PROJECTS/$PROJECT"

# Step 3: Report
echo "📄 Step 3: Generating report..."
./gp-security report "GP-PROJECTS/$PROJECT"

echo "✅ Complete!"
