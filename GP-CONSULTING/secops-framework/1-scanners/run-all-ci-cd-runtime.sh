#!/bin/bash
# ============================================================================
# SecOps Framework - CI/CD/Runtime Security Scanning
# ============================================================================
# Master orchestrator with stage-based execution
#
# Usage:
#   ./run-all-ci-cd-runtime.sh                    # Run all stages
#   ./run-all-ci-cd-runtime.sh --skip-ci          # Skip CI scanners
#   ./run-all-ci-cd-runtime.sh --skip-cd          # Skip CD scanners
#   ./run-all-ci-cd-runtime.sh --skip-runtime     # Skip runtime monitors
#   ./run-all-ci-cd-runtime.sh --only-ci          # Run CI only
#   ./run-all-ci-cd-runtime.sh --only-cd          # Run CD only
#   ./run-all-ci-cd-runtime.sh --only-runtime     # Run runtime only
# ============================================================================

set -e

echo "═══════════════════════════════════════════════════════════"
echo "🚀 SecOps Framework - CI/CD/Runtime Security Scanning"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Parse arguments
RUN_CI=true
RUN_CD=true
RUN_RUNTIME=true

while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-ci)
      RUN_CI=false
      shift
      ;;
    --skip-cd)
      RUN_CD=false
      shift
      ;;
    --skip-runtime)
      RUN_RUNTIME=false
      shift
      ;;
    --only-ci)
      RUN_CI=true
      RUN_CD=false
      RUN_RUNTIME=false
      shift
      ;;
    --only-cd)
      RUN_CI=false
      RUN_CD=true
      RUN_RUNTIME=false
      shift
      ;;
    --only-runtime)
      RUN_CI=false
      RUN_CD=false
      RUN_RUNTIME=true
      shift
      ;;
    --help)
      echo "Usage: ./run-all-ci-cd-runtime.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --skip-ci          Skip CI scanners (code-level)"
      echo "  --skip-cd          Skip CD scanners (infrastructure)"
      echo "  --skip-runtime     Skip runtime monitors"
      echo "  --only-ci          Run CI stage only"
      echo "  --only-cd          Run CD stage only"
      echo "  --only-runtime     Run runtime stage only"
      echo "  --help             Show this help"
      echo ""
      echo "Examples:"
      echo "  ./run-all-ci-cd-runtime.sh                  # Run all stages"
      echo "  ./run-all-ci-cd-runtime.sh --only-ci        # Fast code scan"
      echo "  ./run-all-ci-cd-runtime.sh --skip-runtime   # No AWS/K8s needed"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

START_TIME=$(date +%s)

# ═══════════════════════════════════════════════════════════
# STAGE 1: CI SCANNERS (Code-level)
# ═══════════════════════════════════════════════════════════

if [ "$RUN_CI" = true ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔍 STAGE 1: CI SCANNERS (Code-level)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "When: git commit, pull request, before deployment"
  echo "Speed: Fast (seconds to minutes)"
  echo "Focus: Find vulnerabilities early when cheap to fix"
  echo ""

  cd ci/

  echo "[1/4] SAST (Bandit + Semgrep)..."
  ./scan-code-sast.sh
  echo ""

  echo "[2/4] Secret Scanning (Gitleaks)..."
  ./scan-secrets.sh
  echo ""

  echo "[3/4] Dependency Scanning (npm + pip)..."
  ./scan-dependencies.sh
  echo ""

  echo "[4/4] Container Scanning (Trivy)..."
  ./scan-containers.sh
  echo ""

  cd ..
else
  echo "⏭️  Skipping CI scanners (--skip-ci flag)"
  echo ""
fi

# ═══════════════════════════════════════════════════════════
# STAGE 2: CD SCANNERS (Infrastructure)
# ═══════════════════════════════════════════════════════════

if [ "$RUN_CD" = true ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔍 STAGE 2: CD SCANNERS (Infrastructure)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "When: terraform apply, kubectl apply, infrastructure deployment"
  echo "Speed: Medium (minutes)"
  echo "Focus: Validate infrastructure is secure before production"
  echo ""

  cd cd/

  echo "[1/3] IaC Security (tfsec + Checkov + OPA)..."
  ./scan-iac.sh
  echo ""

  echo "[2/3] Kubernetes Security (Kubescape + Gatekeeper)..."
  ./scan-kubernetes.sh
  echo ""

  echo "[3/3] AWS Compliance (Config)..."
  ./scan-aws-compliance.sh
  echo ""

  cd ..
else
  echo "⏭️  Skipping CD scanners (--skip-cd flag)"
  echo ""
fi

# ═══════════════════════════════════════════════════════════
# STAGE 3: RUNTIME MONITORS
# ═══════════════════════════════════════════════════════════

if [ "$RUN_RUNTIME" = true ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔍 STAGE 3: RUNTIME MONITORS"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "When: 24/7 in production"
  echo "Speed: Real-time"
  echo "Focus: Detect threats and monitor live systems"
  echo ""

  cd runtime/

  echo "[1/3] Prometheus Metrics..."
  ./query-prometheus.sh
  echo ""

  echo "[2/3] AWS GuardDuty..."
  ./query-guardduty.sh
  echo ""

  echo "[3/3] CloudWatch Logs..."
  ./query-cloudwatch.sh
  echo ""

  cd ..
else
  echo "⏭️  Skipping runtime monitors (--skip-runtime flag)"
  echo ""
fi

# ═══════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SCANNING COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Duration: ${DURATION}s"
echo "Results: ../2-findings/raw/"
echo ""
echo "Stages executed:"
[ "$RUN_CI" = true ] && echo "  ✅ CI (Code-level)"
[ "$RUN_CD" = true ] && echo "  ✅ CD (Infrastructure)"
[ "$RUN_RUNTIME" = true ] && echo "  ✅ RUNTIME (Monitoring)"
echo ""
echo "Next steps:"
echo "  1. Aggregate findings: cd ../2-findings && python3 aggregate-findings.py"
echo "  2. Review reports: ls ../2-findings/reports/"
echo "  3. Run fixers: cd ../3-fixers/auto-fixers && ./fix-*.sh"
echo ""
