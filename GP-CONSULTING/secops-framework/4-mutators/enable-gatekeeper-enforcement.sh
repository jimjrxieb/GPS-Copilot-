#!/bin/bash

# ============================================================================
# Phase 4: Enable OPA Gatekeeper Policy Enforcement
# ============================================================================
# This script activates policy enforcement in Kubernetes by:
# 1. Changing enforcementAction from "dryrun" to "deny"
# 2. Enabling mutation webhooks for auto-fixing
# 3. Adding additional constraint templates
# ============================================================================

set -e

echo "🚀 SecOps Phase 4: MUTATE - Enabling Policy Enforcement"
echo "═══════════════════════════════════════════════════════"

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$SCRIPT_DIR"
while [[ ! -d "$CURRENT_DIR/infrastructure/k8s" && "$CURRENT_DIR" != "/" ]]; do
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done
PROJECT_ROOT="$CURRENT_DIR"
K8S_DIR="$PROJECT_ROOT/infrastructure/k8s"
BACKUP_DIR="$K8S_DIR.backup.$(date +%Y%m%d-%H%M%S)"

if [ ! -f "$K8S_DIR/opa-gatekeeper.yaml" ]; then
    echo "❌ ERROR: opa-gatekeeper.yaml not found"
    exit 1
fi

echo ""
echo "→ Creating backup..."
cp -r "$K8S_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Step 1/5: Enabling enforcement for non-root containers..."
sed -i 's/enforcementAction: dryrun[[:space:]]*# ❌ Should be "deny"!/enforcementAction: deny  # ✅ ENFORCED/' "$K8S_DIR/opa-gatekeeper.yaml"
echo "✅ Non-root container policy now enforced"

echo ""
echo "→ Step 2/5: Enabling enforcement for privileged containers..."
# This already has the same pattern, so the sed above catches both
echo "✅ Privileged container policy now enforced"

echo ""
echo "→ Step 3/5: Enabling enforcement for CVV/PIN detection..."
# Same pattern again
echo "✅ CVV/PIN detection policy now enforced"

echo ""
echo "→ Step 4/5: Enabling mutation webhooks..."
# Uncomment the mutation webhook
sed -i '/# apiVersion: mutations.gatekeeper.sh\/v1alpha1/,/# *fsGroup: 1000$/ s/^# //' "$K8S_DIR/opa-gatekeeper.yaml"
echo "✅ Mutation webhooks enabled (auto-inject security contexts)"

echo ""
echo "→ Step 5/5: Updating Gatekeeper status ConfigMap..."
sed -i 's/Enforcement:[[:space:]]*❌ DISABLED (audit mode only)/Enforcement:  ✅ ENABLED (deny mode)/' "$K8S_DIR/opa-gatekeeper.yaml"
sed -i 's/Mutations:[[:space:]]*❌ DISABLED/Mutations:    ✅ ENABLED/' "$K8S_DIR/opa-gatekeeper.yaml"
sed -i 's/(NOT enforced)/(✅ ENFORCED)/g' "$K8S_DIR/opa-gatekeeper.yaml"
echo "✅ Status ConfigMap updated"

echo ""
echo "→ Showing changes..."
git diff "$K8S_DIR/opa-gatekeeper.yaml" 2>&1 | head -100 || echo "  (git diff not available)"

echo ""
echo "✅ OPA Gatekeeper Policy Enforcement ENABLED!"
echo ""
echo "📋 BEFORE (INSECURE):"
echo "   ❌ enforcementAction: dryrun (policies don't block)"
echo "   ❌ Mutations disabled"
echo "   ❌ Violations allowed to deploy"
echo ""
echo "📋 AFTER (SECURE):"
echo "   ✅ enforcementAction: deny (policies block violations)"
echo "   ✅ Mutations enabled (auto-fix security contexts)"
echo "   ✅ Violations prevented at admission time"
echo ""
echo "📋 Policies Now Enforced:"
echo "   ✅ Block root containers (PCI-DSS 2.2.4)"
echo "   ✅ Block privileged containers (PCI-DSS 2.2.1)"
echo "   ✅ Block CVV/PIN in ConfigMaps (PCI-DSS 3.2.2/3.2.3)"
echo "   ✅ Auto-inject security contexts (mutation)"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff $K8S_DIR/opa-gatekeeper.yaml"
echo "   2. Apply to cluster: kubectl apply -f $K8S_DIR/opa-gatekeeper.yaml"
echo "   3. Test with violation: kubectl apply -f test-violation.yaml"
echo "   4. Verify blocking: kubectl get k8srequirenonroot"
echo ""
echo "🔙 Rollback: cp -r $BACKUP_DIR/* $K8S_DIR/"
echo "💾 Backup: $BACKUP_DIR"
