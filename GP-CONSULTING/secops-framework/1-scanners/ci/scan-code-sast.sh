#!/bin/bash
# ============================================================================
# CI SCANNER: Code SAST (Bandit + Semgrep)
# ============================================================================
# Stage: CI (Continuous Integration)
# When: git commit, pull request, before deployment
# Speed: ~15 seconds
# Purpose: Find code-level vulnerabilities early when cheap to fix
# ============================================================================

set -e

echo "🔍 CI SCANNER: Code SAST (Bandit + Semgrep)"
echo "═══════════════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

PROJECT_ROOT="$(cd ../../.. && pwd)"
echo "Project root: $PROJECT_ROOT"
echo

# ============================================================================
# Bandit (Python SAST)
# ============================================================================
if [ -d "$PROJECT_ROOT/backend" ]; then
  echo "→ Running Bandit (Python SAST)..."
  bandit -r "$PROJECT_ROOT/backend/" \
    -f json \
    -o "$OUTPUT_DIR/bandit-results.json" 2>/dev/null || echo "⚠️  Bandit found issues"

  ISSUES=$(jq '.results | length' "$OUTPUT_DIR/bandit-results.json" 2>/dev/null || echo "0")
  echo "✅ Bandit complete: $ISSUES issues found"
else
  echo "⏭️  No backend/ directory, skipping Bandit"
fi

echo

# ============================================================================
# Semgrep (Multi-language SAST)
# ============================================================================
if [ -d "$PROJECT_ROOT/backend" ] || [ -d "$PROJECT_ROOT/frontend" ]; then
  echo "→ Running Semgrep (Multi-language SAST)..."

  SCAN_DIRS=""
  [ -d "$PROJECT_ROOT/backend" ] && SCAN_DIRS="$SCAN_DIRS $PROJECT_ROOT/backend/"
  [ -d "$PROJECT_ROOT/frontend/src" ] && SCAN_DIRS="$SCAN_DIRS $PROJECT_ROOT/frontend/src/"

  semgrep --config auto \
    $SCAN_DIRS \
    --json \
    --output "$OUTPUT_DIR/semgrep-results.json" 2>/dev/null || echo "⚠️  Semgrep found issues"

  ISSUES=$(jq '.results | length' "$OUTPUT_DIR/semgrep-results.json" 2>/dev/null || echo "0")
  echo "✅ Semgrep complete: $ISSUES issues found"
else
  echo "⏭️  No backend/frontend directories, skipping Semgrep"
fi

echo
echo "✅ SAST Scanning Complete"
echo "   Results: $OUTPUT_DIR/bandit-results.json"
echo "   Results: $OUTPUT_DIR/semgrep-results.json"
