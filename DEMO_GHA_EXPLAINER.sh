#!/bin/bash
# Demo: Jade GHA Explainer - Week 2 Intelligence Layer
# Shows AI-powered GitHub Actions security scan analysis

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Jade GHA Explainer - AI-Powered Security Analysis Demo    ║${NC}"
echo -e "${BLUE}║              Week 2: Intelligence Layer                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) not installed${NC}"
    echo "Install: https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI not authenticated${NC}"
    echo "Run: gh auth login"
    exit 1
fi

echo -e "${GREEN}✓ GitHub CLI installed and authenticated${NC}"

# Check jade command
if [ ! -f "bin/jade" ]; then
    echo -e "${RED}❌ Jade CLI not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Jade CLI available${NC}"
echo ""

# Demo menu
echo -e "${BLUE}Select demo scenario:${NC}"
echo "1. Example: Analyze a sample workflow run (recommended for first-time users)"
echo "2. Custom: Analyze your own workflow run (requires repo and run ID)"
echo "3. Show help and documentation"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}�� Demo Scenario: Sample Workflow Analysis${NC}"
        echo ""
        echo "This demo shows how jade explain-gha works:"
        echo "1. Fetches workflow run metadata from GitHub"
        echo "2. Downloads all security scan artifacts"
        echo "3. Parses results from multiple scanners (Bandit, Trivy, Semgrep, etc.)"
        echo "4. Calculates risk scores and prioritizes findings"
        echo "5. Uses AI to explain vulnerabilities to junior engineers"
        echo ""

        # Example repo and run ID
        EXAMPLE_REPO="guidepoint/cloud-project"
        echo -e "${BLUE}Example Repository:${NC} $EXAMPLE_REPO"
        echo ""

        # Get latest run (or use hardcoded example)
        echo -e "${YELLOW}Fetching latest security scan run...${NC}"
        LATEST_RUN=$(gh run list \
            --repo "$EXAMPLE_REPO" \
            --workflow security_scan.yml \
            --limit 1 \
            --json databaseId \
            -q '.[0].databaseId' 2>/dev/null || echo "")

        if [ -z "$LATEST_RUN" ]; then
            echo -e "${YELLOW}⚠️  Could not fetch latest run. Using example run ID.${NC}"
            LATEST_RUN="1234567890"
            echo ""
            echo -e "${YELLOW}NOTE: This is a simulated demo.${NC}"
            echo "In production, jade explain-gha will:"
            echo "  • Fetch actual workflow run data"
            echo "  • Download security scan artifacts"
            echo "  • Parse real scanner results"
            echo "  • Generate AI-powered explanations"
            echo ""
            read -p "Press Enter to see command usage and example output..."
        fi

        echo ""
        echo -e "${GREEN}Run ID:${NC} $LATEST_RUN"
        echo ""

        # Show the command
        echo -e "${BLUE}Command:${NC}"
        echo "bin/jade explain-gha $EXAMPLE_REPO $LATEST_RUN"
        echo ""

        read -p "Execute analysis? (y/N): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            echo ""
            bin/jade explain-gha "$EXAMPLE_REPO" "$LATEST_RUN" 2>&1 || {
                echo ""
                echo -e "${YELLOW}Note: Analysis failed (this is expected if run doesn't exist)${NC}"
                echo ""
                echo -e "${BLUE}Example output would show:${NC}"
                echo "╔══════════════════════════════════════════════════════════════╗"
                echo "║           SECURITY SCAN RESULTS SUMMARY                      ║"
                echo "╚══════════════════════════════════════════════════════════════╝"
                echo ""
                echo "Total Findings: 47"
                echo "Risk Score: 245 (weighted by severity)"
                echo ""
                echo "Severity Breakdown:"
                echo "  🔴 Critical: 5"
                echo "  🟠 High:     12"
                echo "  🟡 Medium:   20"
                echo "  🟢 Low:      10"
                echo ""
                echo "Scanners Used: 8"
                echo "Scanner Types: bandit, trivy, semgrep, gitleaks, checkov, tfsec, safety, npm-audit"
                echo ""
                echo "======================================================================"
                echo "AI SECURITY ANALYSIS"
                echo "======================================================================"
                echo ""
                echo "Based on the security scan results, here are the critical issues:"
                echo ""
                echo "1. 🔴 SQL Injection Vulnerability (bandit-B608)"
                echo "   - What: Unsanitized user input in SQL query"
                echo "   - Risk: Attackers can execute arbitrary SQL"
                echo "   - Fix: Use parameterized queries"
                echo ""
                echo "2. 🔴 Hardcoded AWS Credentials (gitleaks)"
                echo "   - What: AWS access key in code"
                echo "   - Risk: Full account compromise"
                echo "   - Fix: Rotate key, use Secrets Manager"
                echo ""
                echo "[... additional findings ...]"
                echo ""
                echo "Confidence Score: 94.5%"
            }
        fi
        ;;

    2)
        echo ""
        echo -e "${YELLOW}📝 Custom Workflow Analysis${NC}"
        echo ""
        read -p "Enter repository (owner/repo): " repo
        read -p "Enter workflow run ID: " run_id

        if [ -z "$repo" ] || [ -z "$run_id" ]; then
            echo -e "${RED}❌ Repository and run ID are required${NC}"
            exit 1
        fi

        echo ""
        echo -e "${BLUE}Command:${NC}"
        echo "bin/jade explain-gha $repo $run_id"
        echo ""

        read -p "Save results to file? (y/N): " save_file
        if [[ $save_file =~ ^[Yy]$ ]]; then
            OUTPUT_FILE="gha-analysis-$(date +%Y%m%d-%H%M%S).json"
            echo ""
            echo -e "${YELLOW}🔍 Analyzing workflow run...${NC}"
            bin/jade explain-gha "$repo" "$run_id" --output "$OUTPUT_FILE"
            echo ""
            echo -e "${GREEN}✅ Analysis saved to:${NC} $OUTPUT_FILE"
        else
            echo ""
            echo -e "${YELLOW}🔍 Analyzing workflow run...${NC}"
            bin/jade explain-gha "$repo" "$run_id"
        fi
        ;;

    3)
        echo ""
        echo -e "${BLUE}📚 Jade GHA Explainer Documentation${NC}"
        echo ""
        echo -e "${GREEN}Command:${NC}"
        echo "bin/jade explain-gha --help"
        echo ""
        bin/jade explain-gha --help
        echo ""
        echo -e "${BLUE}Full Documentation:${NC}"
        echo "GP-DOCS/guides/JADE_GHA_EXPLAINER.md"
        echo ""
        echo -e "${BLUE}Week 2 Summary:${NC}"
        echo "GP-DOCS/guides/WEEK2_GHA_INTELLIGENCE.md"
        echo ""
        echo -e "${BLUE}Usage Examples:${NC}"
        echo ""
        echo "# Basic analysis"
        echo "jade explain-gha owner/repo 1234567890"
        echo ""
        echo "# Save to file"
        echo "jade explain-gha owner/repo 1234567890 --output analysis.json"
        echo ""
        echo "# Brief mode (AI explanation only)"
        echo "jade explain-gha owner/repo 1234567890 --brief"
        echo ""
        echo -e "${BLUE}Finding Run IDs:${NC}"
        echo ""
        echo "# List recent runs"
        echo "gh run list --repo owner/repo"
        echo ""
        echo "# Get specific workflow"
        echo "gh run list --repo owner/repo --workflow security_scan.yml"
        echo ""
        ;;

    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Demo Complete!${NC}"
echo ""
echo -e "${BLUE}Key Features Demonstrated:${NC}"
echo "✓ Multi-scanner artifact fetching (15+ tools supported)"
echo "✓ Intelligent result parsing and consolidation"
echo "✓ Risk scoring and severity prioritization"
echo "✓ AI-powered vulnerability explanations"
echo "✓ Junior engineer-friendly output"
echo "✓ Full observability with evidence logging"
echo ""
echo -e "${BLUE}View Evidence Log:${NC}"
echo "grep 'explain_gha' ~/.jade/evidence.jsonl | jq"
echo ""
echo -e "${BLUE}View Dashboard:${NC}"
echo "bin/jade-stats"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "• Integrate with CI/CD pipeline"
echo "• Set up automated analysis on PR"
echo "• Configure Slack notifications"
echo "• Explore auto-remediation features (Week 3+)"
echo ""