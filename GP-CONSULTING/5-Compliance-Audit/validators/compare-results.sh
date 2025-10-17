#!/bin/bash

# SecOps Validator: Before/After Comparison
# Compares Act 1 (audit) vs Act 4 (validation) scan results

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FINDINGS_DIR="$SCRIPT_DIR/../2-findings"
RAW_DIR="$FINDINGS_DIR/raw"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 SECOPS VALIDATOR: Before/After Comparison"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we have scan results
if [ ! -d "$RAW_DIR" ]; then
    echo "❌ No findings directory found: $RAW_DIR"
    echo ""
    echo "Run scanners first:"
    echo "  cd ../1-scanners && ./run-all-ci-cd-runtime.sh"
    exit 1
fi

# Function to count findings by severity
count_findings() {
    local file=$1
    local severity=$2

    if [ ! -f "$file" ]; then
        echo "0"
        return
    fi

    # Different tools have different JSON schemas
    case "$file" in
        *bandit*)
            jq "[.results[] | select(.issue_severity == \"$severity\")] | length" "$file" 2>/dev/null || echo "0"
            ;;
        *semgrep*)
            jq "[.results[] | select(.extra.severity == \"$severity\")] | length" "$file" 2>/dev/null || echo "0"
            ;;
        *tfsec*)
            jq "[.results[] | select(.severity == \"$severity\")] | length" "$file" 2>/dev/null || echo "0"
            ;;
        *checkov*)
            jq "[.results.failed_checks[] | select(.severity == \"$severity\")] | length" "$file" 2>/dev/null || echo "0"
            ;;
        *gitleaks*)
            # Gitleaks doesn't have severity, count all as HIGH
            if [ "$severity" == "HIGH" ]; then
                jq "length" "$file" 2>/dev/null || echo "0"
            else
                echo "0"
            fi
            ;;
        *)
            echo "0"
            ;;
    esac
}

# Function to aggregate all findings
aggregate_findings() {
    local critical=0
    local high=0
    local medium=0
    local low=0

    # Bandit (Python SAST)
    if [ -f "$RAW_DIR/bandit-results.json" ]; then
        critical=$((critical + $(count_findings "$RAW_DIR/bandit-results.json" "CRITICAL")))
        high=$((high + $(count_findings "$RAW_DIR/bandit-results.json" "HIGH")))
        medium=$((medium + $(count_findings "$RAW_DIR/bandit-results.json" "MEDIUM")))
        low=$((low + $(count_findings "$RAW_DIR/bandit-results.json" "LOW")))
    fi

    # Semgrep (Multi-language)
    if [ -f "$RAW_DIR/semgrep-results.json" ]; then
        critical=$((critical + $(count_findings "$RAW_DIR/semgrep-results.json" "CRITICAL")))
        high=$((high + $(count_findings "$RAW_DIR/semgrep-results.json" "HIGH")))
        medium=$((medium + $(count_findings "$RAW_DIR/semgrep-results.json" "MEDIUM")))
    fi

    # Gitleaks (Secrets)
    if [ -f "$RAW_DIR/gitleaks-results.json" ]; then
        high=$((high + $(jq "length" "$RAW_DIR/gitleaks-results.json" 2>/dev/null || echo 0)))
    fi

    # tfsec (Terraform)
    if [ -f "$RAW_DIR/tfsec-results.json" ]; then
        critical=$((critical + $(count_findings "$RAW_DIR/tfsec-results.json" "CRITICAL")))
        high=$((high + $(count_findings "$RAW_DIR/tfsec-results.json" "HIGH")))
        medium=$((medium + $(count_findings "$RAW_DIR/tfsec-results.json" "MEDIUM")))
        low=$((low + $(count_findings "$RAW_DIR/tfsec-results.json" "LOW")))
    fi

    # Checkov (IaC)
    if [ -f "$RAW_DIR/checkov-results.json" ]; then
        critical=$((critical + $(count_findings "$RAW_DIR/checkov-results.json" "CRITICAL")))
        high=$((high + $(count_findings "$RAW_DIR/checkov-results.json" "HIGH")))
        medium=$((medium + $(count_findings "$RAW_DIR/checkov-results.json" "MEDIUM")))
    fi

    # Kubescape (Kubernetes)
    if [ -f "$RAW_DIR/kubescape-results.json" ]; then
        # Kubescape uses numeric scores, convert to severity
        local k8s_issues=$(jq ".results.controlReports | length" "$RAW_DIR/kubescape-results.json" 2>/dev/null || echo 0)
        medium=$((medium + k8s_issues))
    fi

    echo "$critical $high $medium $low"
}

# Get current findings
echo "📊 Analyzing current scan results..."
echo ""

read CRITICAL HIGH MEDIUM LOW <<< $(aggregate_findings)
TOTAL=$((CRITICAL + HIGH + MEDIUM + LOW))

echo "CURRENT SCAN RESULTS:"
echo "  CRITICAL:  $CRITICAL"
echo "  HIGH:      $HIGH"
echo "  MEDIUM:    $MEDIUM"
echo "  LOW:       $LOW"
echo "  ───────────────────────────────────────────────────────────"
echo "  TOTAL:     $TOTAL"
echo ""

# Check if we have baseline (for comparison)
BASELINE_FILE="$FINDINGS_DIR/baseline-counts.txt"

if [ -f "$BASELINE_FILE" ]; then
    echo "📊 Comparing with baseline (Act 1 audit)..."
    echo ""

    # Read baseline
    read BASELINE_CRITICAL BASELINE_HIGH BASELINE_MEDIUM BASELINE_LOW <<< $(cat "$BASELINE_FILE")
    BASELINE_TOTAL=$((BASELINE_CRITICAL + BASELINE_HIGH + BASELINE_MEDIUM + BASELINE_LOW))

    # Calculate differences
    DIFF_CRITICAL=$((BASELINE_CRITICAL - CRITICAL))
    DIFF_HIGH=$((BASELINE_HIGH - HIGH))
    DIFF_MEDIUM=$((BASELINE_MEDIUM - MEDIUM))
    DIFF_LOW=$((BASELINE_LOW - LOW))
    DIFF_TOTAL=$((BASELINE_TOTAL - TOTAL))

    echo "BEFORE → AFTER COMPARISON:"
    echo ""
    echo "  Severity    | Before | After | Fixed"
    echo "  ───────────────────────────────────────"
    printf "  CRITICAL    | %6d | %5d | %s%d\n" $BASELINE_CRITICAL $CRITICAL "$([ $DIFF_CRITICAL -gt 0 ] && echo '+' || echo '')" $DIFF_CRITICAL
    printf "  HIGH        | %6d | %5d | %s%d\n" $BASELINE_HIGH $HIGH "$([ $DIFF_HIGH -gt 0 ] && echo '+' || echo '')" $DIFF_HIGH
    printf "  MEDIUM      | %6d | %5d | %s%d\n" $BASELINE_MEDIUM $MEDIUM "$([ $DIFF_MEDIUM -gt 0 ] && echo '+' || echo '')" $DIFF_MEDIUM
    printf "  LOW         | %6d | %5d | %s%d\n" $BASELINE_LOW $LOW "$([ $DIFF_LOW -gt 0 ] && echo '+' || echo '')" $DIFF_LOW
    echo "  ───────────────────────────────────────"
    printf "  TOTAL       | %6d | %5d | %s%d\n" $BASELINE_TOTAL $TOTAL "$([ $DIFF_TOTAL -gt 0 ] && echo '+' || echo '')" $DIFF_TOTAL
    echo ""

    # Summary
    if [ $DIFF_TOTAL -gt 0 ]; then
        PERCENTAGE=$((DIFF_TOTAL * 100 / BASELINE_TOTAL))
        echo "✅ IMPROVEMENT: $DIFF_TOTAL violations fixed ($PERCENTAGE% reduction)"

        if [ $DIFF_CRITICAL -gt 0 ]; then
            echo "✅ CRITICAL: $DIFF_CRITICAL fixed ($(((DIFF_CRITICAL * 100) / BASELINE_CRITICAL))% reduction)"
        fi

        if [ $DIFF_HIGH -gt 0 ]; then
            echo "✅ HIGH: $DIFF_HIGH fixed ($(((DIFF_HIGH * 100) / BASELINE_HIGH))% reduction)"
        fi
    elif [ $DIFF_TOTAL -lt 0 ]; then
        echo "⚠️  REGRESSION: $((DIFF_TOTAL * -1)) new violations introduced"
    else
        echo "ℹ️  No change from baseline"
    fi

    echo ""

    # Regressions check
    if [ $CRITICAL -gt $BASELINE_CRITICAL ]; then
        echo "❌ REGRESSION: $(((CRITICAL - BASELINE_CRITICAL))) new CRITICAL violations!"
    fi

    if [ $HIGH -gt $BASELINE_HIGH ]; then
        echo "⚠️  REGRESSION: $(((HIGH - BASELINE_HIGH))) new HIGH violations"
    fi

else
    echo "ℹ️  No baseline found. Saving current results as baseline..."
    echo "$CRITICAL $HIGH $MEDIUM $LOW" > "$BASELINE_FILE"
    echo "✅ Baseline saved: $BASELINE_FILE"
    echo ""
    echo "Run this script again after remediation to see improvements."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ COMPARISON COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Generate detailed diff report
DIFF_REPORT="$FINDINGS_DIR/diff-report.txt"
echo "Generating detailed diff report: $DIFF_REPORT"

{
    echo "SecOps Framework - Before/After Comparison Report"
    echo "Generated: $(date)"
    echo ""
    echo "Current Results:"
    echo "  CRITICAL: $CRITICAL"
    echo "  HIGH:     $HIGH"
    echo "  MEDIUM:   $MEDIUM"
    echo "  LOW:      $LOW"
    echo "  TOTAL:    $TOTAL"
    echo ""

    if [ -f "$BASELINE_FILE" ]; then
        echo "Baseline Results:"
        echo "  CRITICAL: $BASELINE_CRITICAL"
        echo "  HIGH:     $BASELINE_HIGH"
        echo "  MEDIUM:   $BASELINE_MEDIUM"
        echo "  LOW:      $BASELINE_LOW"
        echo "  TOTAL:    $BASELINE_TOTAL"
        echo ""

        echo "Improvements:"
        echo "  CRITICAL: $([ $DIFF_CRITICAL -gt 0 ] && echo "+$DIFF_CRITICAL fixed" || echo "No change")"
        echo "  HIGH:     $([ $DIFF_HIGH -gt 0 ] && echo "+$DIFF_HIGH fixed" || echo "No change")"
        echo "  MEDIUM:   $([ $DIFF_MEDIUM -gt 0 ] && echo "+$DIFF_MEDIUM fixed" || echo "No change")"
        echo "  LOW:      $([ $DIFF_LOW -gt 0 ] && echo "+$DIFF_LOW fixed" || echo "No change")"
        echo "  TOTAL:    $([ $DIFF_TOTAL -gt 0 ] && echo "+$DIFF_TOTAL fixed" || echo "No change")"
    fi
} > "$DIFF_REPORT"

echo "✅ Diff report saved: $DIFF_REPORT"
echo ""
echo "Next steps:"
echo "  1. Review findings: ls ../2-findings/raw/"
echo "  2. Apply fixes: cd ../3-fixers/auto-fixers && ./fix-*.sh"
echo "  3. Re-scan: cd ../1-scanners && ./run-all-ci-cd-runtime.sh"
echo "  4. Compare again: ./compare-results.sh"
echo ""
