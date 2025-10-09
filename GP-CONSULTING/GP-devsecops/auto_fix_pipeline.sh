#!/bin/bash
# auto_fix_pipeline.sh - Automated pipeline debugging
# Usage: ./auto_fix_pipeline.sh owner/repo

set -e  # Exit on error

REPO="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$REPO" ]; then
    echo -e "${RED}Error: Repository not specified${NC}"
    echo "Usage: ./auto_fix_pipeline.sh owner/repo"
    echo "Example: ./auto_fix_pipeline.sh jimjrxieb/CLOUD-project"
    exit 1
fi

echo -e "${BLUE}🔍 Checking pipeline status for $REPO...${NC}"
echo ""

# Run the Python debugger
cd "$SCRIPT_DIR"
python3 pipeline_debugger.py "$REPO"

EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -eq 0 ]; then
    # Check if all passing or failures detected
    RECENT_RUNS=$(gh run list --repo "$REPO" --limit 1 --json conclusion --jq '.[0].conclusion')

    if [ "$RECENT_RUNS" = "success" ]; then
        echo -e "${GREEN}✅ All workflows passing! No action needed.${NC}"
        echo ""
        echo "📊 View workflows:"
        echo "   https://github.com/$REPO/actions"
    else
        echo -e "${YELLOW}📚 NEXT STEPS:${NC}"
        echo ""
        echo "1. Review recommendations above"
        echo "2. Edit workflow files:"
        echo "   vim .github/workflows/<workflow>.yml"
        echo ""
        echo "3. Common fixes:"
        echo "   • Add: continue-on-error: true  (for optional tools)"
        echo "   • Add: if: false                 (to disable job)"
        echo "   • Update: @v3 → @v4              (for deprecated actions)"
        echo ""
        echo "4. Commit and push:"
        echo "   git add .github/workflows/"
        echo "   git commit -m \"Fix: <description>\""
        echo "   git push"
        echo ""
        echo "5. Monitor pipeline:"
        echo "   sleep 120 && gh run list --repo $REPO --limit 2"
        echo ""
        echo "📖 Full guide:"
        echo "   cat $SCRIPT_DIR/CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md"
    fi
else
    echo -e "${RED}❌ Error running debugger${NC}"
    echo "Check that:"
    echo "  • GitHub CLI is installed: gh --version"
    echo "  • You're authenticated: gh auth status"
    echo "  • Repository exists: gh repo view $REPO"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
