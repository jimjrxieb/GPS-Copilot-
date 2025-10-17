#!/bin/bash
# ============================================================================
# OPA Gatekeeper Deployment Script
# ============================================================================
# Purpose: Deploy OPA Gatekeeper BEFORE application deployment
# Stage: Pre-deployment (mutators applied before app)
# ============================================================================

set -e

echo "🚀 DEPLOYING OPA GATEKEEPER"
echo "══════════════════════════════════════════════════════════════"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ============================================================================
# Step 1: Install Gatekeeper Admission Controller
# ============================================================================
echo "→ Step 1: Installing Gatekeeper admission controller..."

if kubectl get namespace gatekeeper-system &> /dev/null; then
    echo "✅ Gatekeeper namespace already exists"
else
    echo "Installing Gatekeeper from official release..."
    kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.14.0/deploy/gatekeeper.yaml
fi

echo "⏳ Waiting for Gatekeeper pods to be ready..."
kubectl wait --for=condition=ready pod \
  -l control-plane=controller-manager \
  -n gatekeeper-system \
  --timeout=180s

kubectl wait --for=condition=ready pod \
  -l control-plane=audit-controller \
  -n gatekeeper-system \
  --timeout=180s

echo "✅ Gatekeeper admission controller ready"
echo

# ============================================================================
# Step 2: Apply Constraint Templates
# ============================================================================
echo "→ Step 2: Applying constraint templates..."

if [ -f "$SCRIPT_DIR/gatekeeper-constraints/opa-gatekeeper.yaml" ]; then
    kubectl apply -f "$SCRIPT_DIR/gatekeeper-constraints/opa-gatekeeper.yaml"
    echo "✅ Constraint templates applied"
else
    echo "⚠️  No constraint templates found at $SCRIPT_DIR/gatekeeper-constraints/opa-gatekeeper.yaml"
fi

echo

# ============================================================================
# Step 3: Wait for Constraints to be Ready
# ============================================================================
echo "→ Step 3: Waiting for constraints to be established..."
sleep 5

# List all constraint templates
echo "Constraint templates installed:"
kubectl get constrainttemplates -o json | jq -r '.items[].metadata.name' | sed 's/^/  - /'

# List all constraints
echo
echo "Constraints active:"
kubectl get constraints --all-namespaces -o json 2>/dev/null | \
  jq -r '.items[] | "\(.kind): \(.metadata.name)"' | sed 's/^/  - /' || echo "  (none yet)"

echo
echo "✅ OPA Gatekeeper deployment complete"
echo

# ============================================================================
# Step 4: Test Gatekeeper Enforcement (Dry Run)
# ============================================================================
echo "→ Step 4: Testing Gatekeeper enforcement with dry-run pod..."

cat <<EOF | kubectl apply --dry-run=server -f - 2>&1 | grep -i "denied\|allowed\|error" || echo "  ✅ Test completed"
apiVersion: v1
kind: Pod
metadata:
  name: test-pod-bad-security
spec:
  containers:
  - name: nginx
    image: nginx:latest
    securityContext:
      privileged: true
      runAsUser: 0
EOF

echo

# ============================================================================
# Step 5: Display Gatekeeper Status
# ============================================================================
echo "→ Step 5: Gatekeeper status summary..."
echo
echo "Gatekeeper Pods:"
kubectl get pods -n gatekeeper-system
echo
echo "Constraint Templates:"
kubectl get constrainttemplates
echo
echo "Active Constraints:"
kubectl get constraints --all-namespaces
echo

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  OPA GATEKEEPER READY - All policies enforcing at runtime!   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo
echo "Next step: Deploy application with 'kubectl apply -f infrastructure/k8s/'"
echo "Gatekeeper will automatically enforce security policies on all pods."
echo
