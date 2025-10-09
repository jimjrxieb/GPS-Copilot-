#!/bin/bash
# Analyze GHA logs without gh CLI authentication
# This script helps analyze already-downloaded GitHub Actions logs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       GitHub Actions Log Analyzer (Alternative Method)       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if user wants to download logs or analyze existing file
echo "Select option:"
echo "1. Download logs now (requires gh auth)"
echo "2. I already downloaded logs manually"
echo "3. Setup gh auth and use jade explain-gha"
echo ""
read -p "Choice (1-3): " choice

case $choice in
    1)
        read -p "Enter repo (owner/repo): " repo
        read -p "Enter run ID: " run_id

        OUTPUT_FILE="$HOME/gha-scan-results-${run_id}.txt"

        echo ""
        echo "Downloading logs..."
        gh run view "$run_id" --repo "$repo" --log > "$OUTPUT_FILE" 2>&1 || {
            echo "❌ Error: gh CLI not authenticated or run not found"
            echo ""
            echo "To authenticate:"
            echo "  gh auth login"
            echo ""
            echo "Or download logs manually:"
            echo "  1. Go to: https://github.com/$repo/actions/runs/$run_id"
            echo "  2. Click 'Summary' → Download logs"
            echo "  3. Extract and run this script again with option 2"
            exit 1
        }

        echo "✓ Logs saved to: $OUTPUT_FILE"
        LOG_FILE="$OUTPUT_FILE"
        ;;

    2)
        echo ""
        read -p "Enter path to log file: " LOG_FILE

        if [ ! -f "$LOG_FILE" ]; then
            echo "❌ File not found: $LOG_FILE"
            exit 1
        fi
        ;;

    3)
        echo ""
        echo "Setting up GitHub CLI authentication..."
        echo ""
        echo "Run: gh auth login"
        echo ""
        echo "Then use jade explain-gha:"
        echo "  jade explain-gha jimjrxieb/CLOUD-project 18300191954"
        exit 0
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Parse log file for security findings
echo ""
echo "📊 Analyzing security scan results..."
echo ""

# Extract key information
echo "=== WORKFLOW SUMMARY ==="
grep -E "(Running|Completed|Failed|Success)" "$LOG_FILE" | head -20 || echo "No workflow status found"

echo ""
echo "=== SECRET SCAN RESULTS ==="
grep -iE "(secret|credential|key|password|token)" "$LOG_FILE" | grep -iE "(found|detected|exposed)" | head -10 || echo "No secrets detected"

echo ""
echo "=== SAST FINDINGS ==="
grep -iE "(bandit|semgrep|eslint|gosec)" "$LOG_FILE" | grep -iE "(issue|finding|vulnerability)" | head -10 || echo "No SAST findings in logs"

echo ""
echo "=== CONTAINER SCAN ==="
grep -iE "(trivy|grype)" "$LOG_FILE" | grep -iE "(critical|high|vulnerability)" | head -10 || echo "No container vulnerabilities in logs"

echo ""
echo "=== INFRASTRUCTURE FINDINGS ==="
grep -iE "(checkov|tfsec|kubescape)" "$LOG_FILE" | grep -iE "(failed|violation|critical)" | head -10 || echo "No IaC findings in logs"

echo ""
echo "=== SEVERITY SUMMARY ==="
echo ""
echo "Critical findings:"
grep -ci "critical" "$LOG_FILE" 2>/dev/null || echo "0"

echo "High findings:"
grep -ci "high" "$LOG_FILE" 2>/dev/null || echo "0"

echo "Medium findings:"
grep -ci "medium" "$LOG_FILE" 2>/dev/null || echo "0"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📝 Full analysis saved to log file"
echo ""
echo "For AI-powered analysis, use:"
echo "  jade explain-gha jimjrxieb/CLOUD-project 18300191954"
echo ""
echo "This requires:"
echo "  1. gh auth login (to authenticate)"
echo "  2. Read access to the repository"
echo ""