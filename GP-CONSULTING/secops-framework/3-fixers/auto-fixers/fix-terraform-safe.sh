#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔧 SecOps Auto-Fixer: Terraform Security (Safe Mode)"
echo "═══════════════════════════════════════════════════════"

TF_DIR="../../../../infrastructure/terraform"
BACKUP_DIR="$TF_DIR.backup.$(date +%Y%m%d-%H%M%S)"

# Validate Terraform directory exists
if [ ! -d "$TF_DIR" ]; then
  echo -e "${RED}❌ Error: Terraform directory not found: $TF_DIR${NC}"
  exit 1
fi

# Create backup
echo ""
echo "→ Creating backup..."
cp -r "$TF_DIR" "$BACKUP_DIR"
echo -e "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"

# Track if any changes were made
CHANGES_MADE=false

# Fix 1: Enable RDS encryption
echo ""
echo "→ Checking RDS encryption..."
if [ -f "$TF_DIR/rds.tf" ] && grep -q "storage_encrypted.*=.*false" "$TF_DIR/rds.tf"; then
  sed -i.bak 's/storage_encrypted[[:space:]]*=[[:space:]]*false/storage_encrypted = true/g' "$TF_DIR/rds.tf"
  echo -e "${GREEN}✅ Enabled RDS encryption${NC}"
  CHANGES_MADE=true
else
  echo -e "${YELLOW}⏭️  RDS encryption already enabled or file not found${NC}"
fi

# Fix 2: Make RDS private
echo ""
echo "→ Checking RDS public access..."
if [ -f "$TF_DIR/rds.tf" ] && grep -q "publicly_accessible.*=.*true" "$TF_DIR/rds.tf"; then
  sed -i.bak 's/publicly_accessible[[:space:]]*=[[:space:]]*true/publicly_accessible = false/g' "$TF_DIR/rds.tf"
  echo -e "${GREEN}✅ Made RDS private${NC}"
  CHANGES_MADE=true
else
  echo -e "${YELLOW}⏭️  RDS already private or file not found${NC}"
fi

# Fix 3: Enable EKS private endpoint
echo ""
echo "→ Checking EKS endpoint access..."
if [ -f "$TF_DIR/eks.tf" ]; then
  if grep -q "endpoint_public_access.*=.*true" "$TF_DIR/eks.tf"; then
    sed -i.bak 's/endpoint_public_access[[:space:]]*=[[:space:]]*true/endpoint_public_access = false/g' "$TF_DIR/eks.tf"
    echo -e "${GREEN}✅ Disabled EKS public access${NC}"
    CHANGES_MADE=true
  fi

  if grep -q "endpoint_private_access.*=.*false" "$TF_DIR/eks.tf"; then
    sed -i.bak 's/endpoint_private_access[[:space:]]*=[[:space:]]*false/endpoint_private_access = true/g' "$TF_DIR/eks.tf"
    echo -e "${GREEN}✅ Enabled EKS private access${NC}"
    CHANGES_MADE=true
  fi
else
  echo -e "${YELLOW}⏭️  EKS file not found${NC}"
fi

# Validate Terraform after changes
if [ "$CHANGES_MADE" = true ]; then
  echo ""
  echo "→ Validating Terraform configuration..."
  cd "$TF_DIR"

  # Format files
  terraform fmt > /dev/null 2>&1 || true

  # Validate
  if terraform validate > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Terraform validation passed${NC}"
  else
    echo -e "${RED}❌ Terraform validation FAILED${NC}"
    echo ""
    echo "Rolling back changes..."
    rm -rf "$TF_DIR"
    cp -r "$BACKUP_DIR" "$TF_DIR"
    echo -e "${YELLOW}⚠️  Changes rolled back. Check backup: $BACKUP_DIR${NC}"
    exit 1
  fi

  cd - > /dev/null
fi

# Show diff
if [ "$CHANGES_MADE" = true ]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📋 CHANGES MADE"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  cd "$TF_DIR"
  git diff --color 2>/dev/null || diff -u "$BACKUP_DIR" "$TF_DIR" 2>/dev/null || echo "Changes made - see backup for comparison"
  cd - > /dev/null
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
  echo ""
  echo -e "${YELLOW}⏭️  No changes needed - infrastructure already secure!${NC}"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ AUTO-FIXES COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Backup location: $BACKUP_DIR"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes above"
echo "   2. Test plan:"
echo "      cd $TF_DIR"
echo "      terraform plan"
echo ""
echo "   3. If satisfied, commit:"
echo "      git add ."
echo '      git commit -m "Apply SecOps auto-fixes"'
echo ""
echo "   4. To rollback:"
echo "      rm -rf $TF_DIR"
echo "      cp -r $BACKUP_DIR $TF_DIR"
echo ""
