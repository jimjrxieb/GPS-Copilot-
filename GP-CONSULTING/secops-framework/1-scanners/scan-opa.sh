#!/bin/bash
set -e

OUTPUT_DIR="../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

echo "🔍 OPA Policy Validation"
echo "═══════════════════════════════════════"

# OPA test
if command -v opa >/dev/null 2>&1; then
  echo "→ Running OPA policy tests..."
  opa test ../../policies/ -v \
    --format json \
    > "$OUTPUT_DIR/opa-test-results.json" || true
  echo "✅ OPA tests complete"

  # Conftest (OPA for Terraform)
  if command -v conftest >/dev/null 2>&1; then
    echo "→ Running Conftest on Terraform..."
    conftest test ../../infrastructure/terraform/ \
      -p ../../policies/opa/ \
      --output json \
      > "$OUTPUT_DIR/conftest-results.json" || true
    echo "✅ Conftest scan complete"
  else
    echo "⚠️  Conftest not installed. Install: brew install conftest"
  fi
else
  echo "⚠️  OPA not installed. Install: brew install opa"
fi

echo ""
echo "📁 Results saved to: $OUTPUT_DIR/"
