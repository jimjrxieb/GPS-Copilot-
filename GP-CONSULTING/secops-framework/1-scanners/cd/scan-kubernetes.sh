#!/bin/bash
# ============================================================================
# CD SCANNER: Kubernetes Security (Kubescape + Gatekeeper)
# ============================================================================
# Stage: CD (Continuous Deployment)
# When: kubectl apply, post-deployment
# Speed: ~30 seconds
# Purpose: Validate K8s manifests against CIS Benchmark and policies
# ============================================================================

set -e

echo "🔍 CD SCANNER: Kubernetes Security (Kubescape + Gatekeeper)"
echo "══════════════════════════════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

PROJECT_ROOT="$(cd ../../.. && pwd)"
K8S_DIR="$PROJECT_ROOT/infrastructure/k8s"

echo "Project root: $PROJECT_ROOT"
echo "Kubernetes dir: $K8S_DIR"
echo

if [ ! -d "$K8S_DIR" ]; then
  echo "❌ No Kubernetes directory found at $K8S_DIR"
  exit 0
fi

# ============================================================================
# Kubescape (CIS Kubernetes Benchmark)
# ============================================================================
if command -v kubescape &> /dev/null; then
  echo "→ Running Kubescape (CIS Benchmark)..."
  kubescape scan framework cis "$K8S_DIR" \
    --format json \
    --output "$OUTPUT_DIR/kubescape-results.json" 2>/dev/null || echo "⚠️  Kubescape found issues"

  SCORE=$(jq '.summaryDetails.complianceScore // 0' "$OUTPUT_DIR/kubescape-results.json" 2>/dev/null || echo "0")
  echo "✅ Kubescape complete: Compliance score $SCORE%"
else
  echo "⏭️  Kubescape not installed, skipping"
  echo "   Install: curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash"
fi

echo

# ============================================================================
# Check Gatekeeper status (if K8s cluster accessible)
# ============================================================================
if command -v kubectl &> /dev/null && kubectl cluster-info &> /dev/null; then
  echo "→ Checking Gatekeeper status..."

  if kubectl get namespace gatekeeper-system &> /dev/null; then
    echo "✅ Gatekeeper is installed"

    # Get constraint templates
    kubectl get constrainttemplates -o json > "$OUTPUT_DIR/gatekeeper-templates.json" 2>/dev/null

    TEMPLATES=$(jq '.items | length' "$OUTPUT_DIR/gatekeeper-templates.json" 2>/dev/null || echo "0")
    echo "   Constraint templates: $TEMPLATES"

    # Get constraints
    kubectl get constraints --all-namespaces -o json > "$OUTPUT_DIR/gatekeeper-constraints.json" 2>/dev/null

    # Get violations from constraints
    kubectl get constraints --all-namespaces -o json | \
      jq '[.items[] | select(.status.totalViolations > 0) | {name: .metadata.name, violations: .status.totalViolations}]' > "$OUTPUT_DIR/gatekeeper-violations.json" 2>/dev/null

    VIOLATIONS=$(jq '. | map(.violations) | add // 0' "$OUTPUT_DIR/gatekeeper-violations.json" 2>/dev/null || echo "0")
    echo "   Total violations: $VIOLATIONS"
  else
    echo "⚠️  Gatekeeper NOT installed - policies not enforcing!"
    echo "   Install: kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml"
  fi
else
  echo "⏭️  kubectl not available or no cluster, skipping Gatekeeper check"
fi

echo
echo "✅ Kubernetes Security Scanning Complete"
echo "   Results: $OUTPUT_DIR/kubescape-results.json"
echo "   Results: $OUTPUT_DIR/gatekeeper-*.json"
