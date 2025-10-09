#!/bin/bash
# ============================================================================
# CI SCANNER: Dependency Scanning (npm audit + pip-audit)
# ============================================================================
# Stage: CI (Continuous Integration)
# When: package.json change, requirements.txt change
# Speed: ~10 seconds
# Purpose: Find vulnerable npm/Python packages (CVEs)
# ============================================================================

set -e

echo "🔍 CI SCANNER: Dependency Scanning (npm + pip)"
echo "════════════════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

PROJECT_ROOT="$(cd ../../.. && pwd)"
echo "Project root: $PROJECT_ROOT"
echo

# ============================================================================
# npm audit (JavaScript dependencies)
# ============================================================================
if [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
  echo "→ Running npm audit..."
  cd "$PROJECT_ROOT/frontend/"

  npm audit --json > ../secops/2-findings/raw/npm-audit-results.json 2>/dev/null || echo "⚠️  npm audit found vulnerabilities"

  VULNS=$(jq '.metadata.vulnerabilities | add' ../secops/2-findings/raw/npm-audit-results.json 2>/dev/null || echo "0")
  echo "✅ npm audit complete: $VULNS vulnerabilities found"

  cd - > /dev/null
else
  echo "⏭️  No package.json found, skipping npm audit"
fi

echo

# ============================================================================
# pip-audit (Python dependencies)
# ============================================================================
if [ -f "$PROJECT_ROOT/backend/requirements.txt" ]; then
  echo "→ Running pip-audit..."

  pip-audit -r "$PROJECT_ROOT/backend/requirements.txt" \
    --format json \
    --output "$OUTPUT_DIR/pip-audit-results.json" 2>/dev/null || echo "⚠️  pip-audit found vulnerabilities"

  VULNS=$(jq '.dependencies | length' "$OUTPUT_DIR/pip-audit-results.json" 2>/dev/null || echo "0")
  echo "✅ pip-audit complete: $VULNS vulnerable packages found"
else
  echo "⏭️  No requirements.txt found, skipping pip-audit"
fi

echo
echo "✅ Dependency Scanning Complete"
echo "   Results: $OUTPUT_DIR/npm-audit-results.json"
echo "   Results: $OUTPUT_DIR/pip-audit-results.json"
