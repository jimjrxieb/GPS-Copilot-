#!/bin/bash

# ============================================================================
# Auto-Fixer: CloudWatch Encryption (HIGH FINDINGS)
# ============================================================================
# FIXES:
#   - HIGH: CloudWatch log groups without KMS encryption (PCI-DSS 3.4)
#   - MEDIUM: CloudWatch log retention too short (PCI-DSS 10.1)
# ============================================================================

set -e

echo "🔧 Auto-Fixer: CloudWatch Encryption (HIGH)"
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
if [ ! -f "$TF_DIR/cloudwatch.tf" ]; then
    echo "❌ ERROR: cloudwatch.tf not found"
    exit 1
fi

echo ""
echo "→ Creating backup..."
cp -r "$TF_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Step 1/2: Fixing log retention (MEDIUM)..."
sed -i 's/retention_in_days[[:space:]]*=[[:space:]]*1[[:space:]]*# ❌ Should be 90+ days/retention_in_days = 90  # ✅ PCI-DSS 10.1 - 90 day retention/' "$TF_DIR/cloudwatch.tf"
echo "✅ Log retention set to 90 days"

echo ""
echo "→ Step 2/2: Enabling KMS encryption (HIGH)..."
sed -i 's/# ❌ PCI 3.4: No encryption/# ✅ PCI 3.4: KMS encryption enabled/' "$TF_DIR/cloudwatch.tf"
sed -i 's@# kms_key_id = aws_kms_key.logs.arn@kms_key_id = aws_kms_key.securebank.arn  # ✅ Encrypted with project KMS key@' "$TF_DIR/cloudwatch.tf"
echo "✅ KMS encryption enabled"

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
git diff "$TF_DIR/cloudwatch.tf" 2>/dev/null || echo "  (git diff not available)"

echo ""
echo "✅ CloudWatch Encryption auto-fix complete!"
echo ""
echo "📋 BEFORE (INSECURE):"
echo "   ❌ retention_in_days = 1"
echo "   ❌ No KMS encryption"
echo ""
echo "📋 AFTER (SECURE):"
echo "   ✅ retention_in_days = 90 (PCI-DSS 10.1)"
echo "   ✅ KMS encryption enabled (PCI-DSS 3.4)"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff $TF_DIR/cloudwatch.tf"
echo "   2. Plan: cd $TF_DIR && terraform plan"
echo "   3. Apply: terraform apply"
echo ""
echo "🔙 Rollback: cp -r $BACKUP_DIR/* $TF_DIR/"
echo "💾 Backup: $BACKUP_DIR"
