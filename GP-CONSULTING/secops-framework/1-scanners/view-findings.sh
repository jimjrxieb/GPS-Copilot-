#!/bin/bash
# Quick viewer for scanner findings

echo "📊 Scanner Findings Summary"
echo "═══════════════════════════════════════"
echo ""

RAW_DIR="../2-findings/raw"

# Bandit findings
if [ -f "$RAW_DIR/bandit-results.json" ]; then
    BANDIT_COUNT=$(jq '.results | length' "$RAW_DIR/bandit-results.json" 2>/dev/null || echo "0")
    echo "🐍 Bandit (Python SAST): $BANDIT_COUNT findings"
    if [ "$BANDIT_COUNT" -gt 0 ]; then
        echo "   Top issues:"
        jq -r '.results[0:3] | .[] | "   - \(.issue_text) (\(.issue_severity)) in \(.filename):\(.line_number)"' "$RAW_DIR/bandit-results.json" 2>/dev/null
    fi
    echo ""
fi

# Semgrep findings
if [ -f "$RAW_DIR/semgrep-results.json" ]; then
    SEMGREP_COUNT=$(jq '.results | length' "$RAW_DIR/semgrep-results.json" 2>/dev/null || echo "0")
    echo "🔍 Semgrep (SAST): $SEMGREP_COUNT findings"
    if [ "$SEMGREP_COUNT" -gt 0 ]; then
        echo "   Issues:"
        jq -r '.results[] | "   - \(.extra.message) (\(.extra.severity)) in \(.path):\(.start.line)"' "$RAW_DIR/semgrep-results.json" 2>/dev/null
    fi
    echo ""
fi

# tfsec findings
if [ -f "$RAW_DIR/tfsec-results.json" ]; then
    TFSEC_COUNT=$(jq '.results | length' "$RAW_DIR/tfsec-results.json" 2>/dev/null || echo "0")
    echo "☁️  tfsec (Terraform): $TFSEC_COUNT findings"
    echo ""
fi

# Checkov findings
if [ -f "$RAW_DIR/checkov-results.json" ]; then
    CHECKOV_COUNT=$(jq 'try .results.failed_checks | length catch 0' "$RAW_DIR/checkov-results.json" 2>/dev/null || echo "0")
    echo "✓  Checkov (IaC): $CHECKOV_COUNT findings"
    echo ""
fi

# Gitleaks findings
if [ -f "$RAW_DIR/gitleaks-results.json" ]; then
    GITLEAKS_COUNT=$(jq 'length' "$RAW_DIR/gitleaks-results.json" 2>/dev/null || echo "0")
    echo "🔐 Gitleaks (Secrets): $GITLEAKS_COUNT findings"
    if [ "$GITLEAKS_COUNT" -gt 0 ]; then
        echo "   ⚠️  Hardcoded secrets detected!"
        jq -r '.[] | "   - \(.Description) in \(.File):\(.StartLine)"' "$RAW_DIR/gitleaks-results.json" 2>/dev/null | head -5
    fi
    echo ""
fi

# Trivy findings
for TRIVY_FILE in "$RAW_DIR"/trivy-*-results.json; do
    if [ -f "$TRIVY_FILE" ]; then
        COMPONENT=$(basename "$TRIVY_FILE" | sed 's/trivy-//;s/-results.json//')
        TRIVY_COUNT=$(jq '[.Results[]?.Vulnerabilities[]?] | length' "$TRIVY_FILE" 2>/dev/null || echo "0")
        echo "🐳 Trivy ($COMPONENT): $TRIVY_COUNT vulnerabilities"
    fi
done

echo ""
echo "═══════════════════════════════════════"
echo "📁 View raw results: ls -lh $RAW_DIR/"
echo "📊 Run aggregation: cd ../2-findings && python3 aggregate-findings.py"
