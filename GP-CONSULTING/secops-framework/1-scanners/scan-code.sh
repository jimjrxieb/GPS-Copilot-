#!/bin/bash
set -e

OUTPUT_DIR="../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Code Security Scan (Bandit + Semgrep)"
echo "═══════════════════════════════════════"

# Bandit scan (Python)
if command -v bandit >/dev/null 2>&1; then
  echo "→ Running Bandit on Python code..."
  bandit -r ../../backend/ \
    -f json \
    -o "$OUTPUT_DIR/bandit-results.json" \
    -ll || true
  echo "✅ Bandit scan complete"
else
  echo "⚠️  Bandit not installed. Install: pip install bandit"
fi

# Semgrep scan (multi-language)
if command -v semgrep >/dev/null 2>&1; then
  echo "→ Running Semgrep SAST scan..."
  semgrep --config auto \
    ../../backend/ \
    ../../frontend/src/ \
    --json \
    --output "$OUTPUT_DIR/semgrep-results.json" || true
  echo "✅ Semgrep scan complete"
else
  echo "⚠️  Semgrep not installed. Install: pip install semgrep"
fi

echo ""
echo "📁 Results saved to: $OUTPUT_DIR/"
