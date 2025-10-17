#!/bin/bash
# ============================================================================
# CD SCANNER: IaC Security (tfsec + Checkov + OPA)
# ============================================================================
# Stage: CD (Continuous Deployment)
# When: terraform plan, terraform apply
# Speed: ~25 seconds
# Purpose: Validate infrastructure is secure before deployment
# ============================================================================

set -e

echo "🔍 CD SCANNER: IaC Security (tfsec + Checkov + OPA)"
echo "══════════════════════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

PROJECT_ROOT="$(cd ../../.. && pwd)"
TF_DIR="$PROJECT_ROOT/infrastructure/terraform"

echo "Project root: $PROJECT_ROOT"
echo "Terraform dir: $TF_DIR"
echo

if [ ! -d "$TF_DIR" ]; then
  echo "❌ No Terraform directory found at $TF_DIR"
  exit 0
fi

# ============================================================================
# tfsec (Terraform security)
# ============================================================================
echo "→ Running tfsec..."
tfsec "$TF_DIR" \
  --format json \
  --out "$OUTPUT_DIR/tfsec-results.json" 2>/dev/null || echo "⚠️  tfsec found issues"

ISSUES=$(jq '.results | length' "$OUTPUT_DIR/tfsec-results.json" 2>/dev/null || echo "0")
echo "✅ tfsec complete: $ISSUES issues found"
echo

# ============================================================================
# Checkov (Multi-cloud IaC)
# ============================================================================
echo "→ Running Checkov..."
checkov -d "$TF_DIR" \
  --framework terraform \
  --output json \
  --output-file-path "$OUTPUT_DIR" 2>/dev/null || echo "⚠️  Checkov found issues"

# Checkov creates results_json.json
if [ -f "$OUTPUT_DIR/results_json.json" ]; then
  mv "$OUTPUT_DIR/results_json.json" "$OUTPUT_DIR/checkov-results.json"
fi

FAILED=$(jq '.summary.failed // 0' "$OUTPUT_DIR/checkov-results.json" 2>/dev/null || echo "0")
echo "✅ Checkov complete: $FAILED checks failed"
echo

# ============================================================================
# OPA/Conftest (Custom policies from Phase 3: Hardening)
# ============================================================================
# Reference centralized policies in Phase 3 (enforcement layer)
GP_CONSULTING="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POLICY_DIR="$GP_CONSULTING/3-Hardening/policies/opa"

if [ -d "$POLICY_DIR" ]; then
  echo "→ Running OPA/Conftest..."
  echo "   Policy source: Phase 3 Hardening (centralized enforcement policies)"
  conftest test "$TF_DIR" \
    -p "$POLICY_DIR" \
    --output json > "$OUTPUT_DIR/opa-conftest-results.json" 2>/dev/null || echo "⚠️  OPA found policy violations"

  FAILURES=$(jq '[.[]?.failures[]?] | length' "$OUTPUT_DIR/opa-conftest-results.json" 2>/dev/null || echo "0")
  echo "✅ OPA/Conftest complete: $FAILURES policy violations"
else
  echo "⏭️  No OPA policies found at $POLICY_DIR, skipping Conftest"
  echo "   Expected location: GP-CONSULTING/3-Hardening/policies/opa/"
fi

echo
echo "✅ IaC Security Scanning Complete"
echo "   Results: $OUTPUT_DIR/tfsec-results.json"
echo "   Results: $OUTPUT_DIR/checkov-results.json"
echo "   Results: $OUTPUT_DIR/opa-conftest-results.json"
