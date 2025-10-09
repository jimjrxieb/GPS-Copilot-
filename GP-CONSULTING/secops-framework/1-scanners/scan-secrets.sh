#!/bin/bash
set -e

OUTPUT_DIR="../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Secret Detection Scan (Gitleaks)"
echo "═══════════════════════════════════════"

# Gitleaks scan
if command -v gitleaks >/dev/null 2>&1; then
  echo "→ Running Gitleaks secret scan..."
  gitleaks detect \
    --source ../../ \
    --report-format json \
    --report-path "$OUTPUT_DIR/gitleaks-results.json" \
    --verbose || true
  echo "✅ Gitleaks scan complete"
else
  echo "⚠️  Gitleaks not installed. Install: brew install gitleaks"
fi

echo ""
echo "📁 Results saved to: $OUTPUT_DIR/"
