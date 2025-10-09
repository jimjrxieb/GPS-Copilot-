#!/bin/bash
set -e

echo "🔍 SecOps Phase 1: AUDIT - Running all security scanners..."
echo "═══════════════════════════════════════════════════════════"

# Create output directory
mkdir -p ../2-findings/raw/

# Run each scanner
echo ""
echo "→ Running IaC security scan (tfsec + Checkov)..."
./scan-iac.sh

echo ""
echo "→ Running code security scan (Bandit + Semgrep)..."
./scan-code.sh

echo ""
echo "→ Running container security scan (Trivy)..."
./scan-containers.sh

echo ""
echo "→ Running secret detection (Gitleaks)..."
./scan-secrets.sh

echo ""
echo "→ Running OPA policy validation..."
./scan-opa.sh

echo ""
echo "✅ All scans complete! Results saved to: secops/2-findings/raw/"
echo ""
echo "📊 Next step: Run aggregation - cd ../2-findings && python3 aggregate-findings.py"
