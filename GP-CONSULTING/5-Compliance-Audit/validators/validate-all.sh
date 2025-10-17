#!/bin/bash
set -e

echo "✅ SecOps Phase 5: VALIDATE - Re-scanning for violations..."
echo "═══════════════════════════════════════════════════════════"

# Create output directory
mkdir -p after-fix/

echo ""
echo "→ Re-running all scanners (this may take a few minutes)..."

# Re-run Phase 1 scanners
cd ../1-scanners
./run-all-scans.sh

# Move results to validation directory
cd ../5-validators
mv ../2-findings/raw/* after-fix/ 2>/dev/null || true

echo ""
echo "→ Comparing before/after results..."

# Run comparison script
python3 compare-results.py

echo ""
echo "→ Generating validation report..."

# Generate pass/fail report
./generate-validation-report.sh

echo ""
echo "✅ Validation complete!"
echo ""
echo "📊 View results:"
echo "   - Comparison: cat validation-report.md"
echo "   - Metrics: cat violation-metrics.json"
