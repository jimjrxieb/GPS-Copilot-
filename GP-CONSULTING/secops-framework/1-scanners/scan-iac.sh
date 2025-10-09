#!/bin/bash
set -e

OUTPUT_DIR="../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

echo "🔍 IaC Security Scan (tfsec + Checkov)"
echo "═══════════════════════════════════════"

# tfsec scan
if command -v tfsec >/dev/null 2>&1; then
  echo "→ Running tfsec on Terraform..."
  tfsec ../../infrastructure/terraform/ \
    --format json \
    --out "$OUTPUT_DIR/tfsec-results.json" \
    --minimum-severity MEDIUM || true
  echo "✅ tfsec scan complete"
else
  echo "⚠️  tfsec not installed. Install: brew install tfsec"
fi

# Checkov scan
if command -v checkov >/dev/null 2>&1; then
  echo "→ Running Checkov on Terraform..."
  checkov -d ../../infrastructure/terraform/ \
    --framework terraform \
    --output json \
    --output-file-path "$OUTPUT_DIR" \
    --soft-fail || true
  mv "$OUTPUT_DIR/results_json.json" "$OUTPUT_DIR/checkov-results.json" 2>/dev/null || true
  echo "✅ Checkov scan complete"
else
  echo "⚠️  Checkov not installed. Install: pip install checkov"
fi

echo ""
echo "📁 Results saved to: $OUTPUT_DIR/"
