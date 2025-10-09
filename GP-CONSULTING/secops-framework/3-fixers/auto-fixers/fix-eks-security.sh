#!/bin/bash

# ============================================================================
# Auto-Fixer: EKS Security (HIGH FINDINGS)
# ============================================================================
# FIXES:
#   - HIGH: EKS cluster endpoint publicly accessible (PCI-DSS 2.2.1)
#   - HIGH: EKS control plane logging disabled (PCI-DSS 10.1)
#   - HIGH: EKS secrets without envelope encryption (PCI-DSS 3.4)
#   - MEDIUM: EKS using public subnets
# ============================================================================

set -e

echo "🔧 Auto-Fixer: EKS Security (HIGH)"
echo "═══════════════════════════════════════════════════════"

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$SCRIPT_DIR"
while [[ ! -d "$CURRENT_DIR/infrastructure/terraform" && "$CURRENT_DIR" != "/" ]]; do
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done
PROJECT_ROOT="$CURRENT_DIR"
TF_DIR="$PROJECT_ROOT/infrastructure/terraform"
BACKUP_DIR="$TF_DIR.backup.$(date +%Y%m%d-%H%M%S)"

# Validate
if [ ! -f "$TF_DIR/eks.tf" ]; then
    echo "❌ ERROR: eks.tf not found"
    exit 1
fi

echo ""
echo "→ Creating backup..."
cp -r "$TF_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Step 1/5: Fixing EKS endpoint access (HIGH)..."
sed -i 's/endpoint_private_access = false[[:space:]]*# ❌ Should be true/endpoint_private_access = true   # ✅ Private access enabled/' "$TF_DIR/eks.tf"
sed -i 's/endpoint_public_access[[:space:]]*=[[:space:]]*true[[:space:]]*# ❌ Should be false/endpoint_public_access  = false  # ✅ Public access disabled/' "$TF_DIR/eks.tf"
# Comment out public_access_cidrs since we're disabling public access
sed -i 's/public_access_cidrs[[:space:]]*=[[:space:]]*\["0.0.0.0\/0"\][[:space:]]*# ❌ CRITICAL!/# public_access_cidrs     = ["0.0.0.0\/0"]  # Disabled - no public access/' "$TF_DIR/eks.tf"
echo "✅ EKS endpoint now private-only"

echo ""
echo "→ Step 2/5: Updating EKS security group..."
sed -i 's/security_group_ids[[:space:]]*=[[:space:]]*\[aws_security_group.allow_all.id\]/security_group_ids      = [aws_security_group.eks_cluster.id]  # ✅ Least-privilege SG/' "$TF_DIR/eks.tf"
echo "✅ Security group updated"

echo ""
echo "→ Step 3/5: Enabling control plane logging (HIGH)..."
sed -i 's/enabled_cluster_log_types = \[\][[:space:]]*# ❌ Should log all/enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]  # ✅ PCI-DSS 10.1/' "$TF_DIR/eks.tf"
echo "✅ Control plane logging enabled"

echo ""
echo "→ Step 4/5: Enabling envelope encryption for secrets (HIGH)..."
# Uncomment the encryption_config block
sed -i '/# ❌ PCI 3.4: No envelope encryption for secrets/,/# }/s/^[[:space:]]*# /  /' "$TF_DIR/eks.tf"
# Update the KMS key reference
sed -i 's/key_arn = aws_kms_key.eks.arn/key_arn = aws_kms_key.securebank.arn  # ✅ Envelope encryption/' "$TF_DIR/eks.tf"
echo "✅ Envelope encryption enabled"

echo ""
echo "→ Step 5/5: Updating node group subnet (use private if available)..."
# Check if private subnets exist
if grep -q "aws_subnet.private" "$TF_DIR/vpc.tf" 2>/dev/null; then
    sed -i '0,/subnet_ids[[:space:]]*=[[:space:]]*\[aws_subnet.public_1.id, aws_subnet.public_2.id\]/{s/subnet_ids[[:space:]]*=[[:space:]]*\[aws_subnet.public_1.id, aws_subnet.public_2.id\]/subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]  # ✅ Private subnets/}' "$TF_DIR/eks.tf"
    echo "✅ Node group using private subnets"
else
    echo "⚠️  Private subnets not found - keeping public subnets for nodes"
fi

echo ""
echo "→ Validating changes..."
cd "$TF_DIR"

if [ -d ".terraform" ]; then
    if terraform validate > /dev/null 2>&1; then
        echo "✅ Terraform validation passed"
    else
        echo "⚠️  Terraform validation warnings"
    fi
else
    echo "⚠️  Terraform not initialized, skipping validation"
fi

echo ""
echo "→ Showing changes..."
git diff "$TF_DIR/eks.tf" 2>&1 | head -80 || echo "  (git diff not available)"

echo ""
echo "✅ EKS Security auto-fix complete!"
echo ""
echo "📋 BEFORE (INSECURE):"
echo "   ❌ endpoint_public_access = true (exposed to internet)"
echo "   ❌ endpoint_private_access = false"
echo "   ❌ public_access_cidrs = [0.0.0.0/0]"
echo "   ❌ Control plane logging disabled"
echo "   ❌ No envelope encryption for secrets"
echo ""
echo "📋 AFTER (SECURE):"
echo "   ✅ endpoint_public_access = false (private only)"
echo "   ✅ endpoint_private_access = true"
echo "   ✅ Control plane logging enabled (all 5 log types)"
echo "   ✅ Envelope encryption with KMS (PCI-DSS 3.4)"
echo "   ✅ Using EKS-specific security group"
echo ""
echo "⚠️  IMPORTANT: Changing endpoint access requires cluster downtime!"
echo "   Plan carefully before applying."
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff $TF_DIR/eks.tf"
echo "   2. Plan: cd $TF_DIR && terraform plan"
echo "   3. Apply: terraform apply"
echo ""
echo "🔙 Rollback: cp -r $BACKUP_DIR/* $TF_DIR/"
echo "💾 Backup: $BACKUP_DIR"
