#!/bin/bash
# ============================================================================
# CI SCANNER: Secret Scanning (Gitleaks)
# ============================================================================
# Stage: CI (Continuous Integration)
# When: git commit, git push, pre-receive hook
# Speed: ~3 seconds
# Purpose: Detect AWS keys, API tokens, passwords in commits
# ============================================================================

set -e

echo "🔍 CI SCANNER: Secret Scanning (Gitleaks)"
echo "═══════════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

PROJECT_ROOT="$(cd ../../.. && pwd)"
echo "Project root: $PROJECT_ROOT"
echo

echo "→ Running Gitleaks..."
cd "$PROJECT_ROOT"

gitleaks detect \
  --source . \
  --report-format json \
  --report-path secops/2-findings/raw/gitleaks-results.json \
  --no-git \
  --verbose 2>/dev/null || echo "⚠️  Gitleaks found secrets"

cd - > /dev/null

SECRETS=$(jq 'length' "$OUTPUT_DIR/gitleaks-results.json" 2>/dev/null || echo "0")
echo "✅ Gitleaks complete: $SECRETS secrets found"

echo
echo "✅ Secret Scanning Complete"
echo "   Results: $OUTPUT_DIR/gitleaks-results.json"
