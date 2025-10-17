#!/bin/bash

# ============================================================================
# Migrate Secrets from HashiCorp Vault to AWS Secrets Manager
# ============================================================================
# USAGE:
#   ./migrate-from-vault.sh <vault-path> [kms-key-id]
#
# EXAMPLES:
#   # Migrate all secrets from vault path
#   ./migrate-from-vault.sh secret/securebank
#
#   # With KMS encryption
#   ./migrate-from-vault.sh secret/securebank arn:aws:kms:us-east-1:123456789012:key/xxx
#
# PREREQUISITES:
#   - vault CLI installed
#   - VAULT_ADDR and VAULT_TOKEN environment variables set
#   - awslocal or aws CLI configured
# ============================================================================

set -e

VAULT_PATH="$1"
KMS_KEY_ID="$2"
AWS_CMD="${AWS_CMD:-awslocal}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$VAULT_PATH" ]; then
    echo "Usage: $0 <vault-path> [kms-key-id]"
    echo ""
    echo "Example: $0 secret/securebank"
    exit 1
fi

echo "🔐 Migrating Secrets from Vault to AWS Secrets Manager"
echo "═══════════════════════════════════════════════════════"
echo "Vault Path: $VAULT_PATH"
echo ""

# ============================================================================
# Check Prerequisites
# ============================================================================

if ! command -v vault &> /dev/null; then
    echo -e "${RED}❌ vault CLI not found${NC}"
    echo "Install: https://www.vaultproject.io/downloads"
    exit 1
fi

if [ -z "$VAULT_ADDR" ]; then
    echo -e "${RED}❌ VAULT_ADDR not set${NC}"
    echo "Export: export VAULT_ADDR=http://localhost:8200"
    exit 1
fi

if [ -z "$VAULT_TOKEN" ]; then
    echo -e "${YELLOW}⚠ VAULT_TOKEN not set${NC}"
    echo "You may need to authenticate: vault login"
fi

# ============================================================================
# List Secrets in Vault
# ============================================================================

echo "Listing secrets in Vault..."
SECRETS=$(vault kv list -format=json "$VAULT_PATH" 2>/dev/null | jq -r '.[]' || echo "")

if [ -z "$SECRETS" ]; then
    echo -e "${RED}❌ No secrets found at $VAULT_PATH${NC}"
    exit 1
fi

SECRET_COUNT=$(echo "$SECRETS" | wc -l)
echo -e "${GREEN}✓ Found $SECRET_COUNT secrets${NC}"
echo ""

# ============================================================================
# Migrate Each Secret
# ============================================================================

MIGRATED=0
FAILED=0

while IFS= read -r secret_name; do
    # Skip empty lines
    [ -z "$secret_name" ] && continue

    # Remove trailing slash if present
    secret_name="${secret_name%/}"

    echo "Migrating: $secret_name"

    # Get secret value from Vault
    SECRET_VALUE=$(vault kv get -format=json "$VAULT_PATH/$secret_name" 2>/dev/null | jq -r '.data.data' || echo "")

    if [ -z "$SECRET_VALUE" ] || [ "$SECRET_VALUE" = "null" ]; then
        echo -e "${RED}  ✗ Failed to read from Vault${NC}"
        FAILED=$((FAILED + 1))
        continue
    fi

    # Create secret in AWS Secrets Manager
    AWS_SECRET_NAME="${secret_name//\//-}"  # Replace / with - for AWS naming

    if [ -n "$KMS_KEY_ID" ]; then
        if $AWS_CMD secretsmanager create-secret \
            --name "$AWS_SECRET_NAME" \
            --description "Migrated from Vault: $VAULT_PATH/$secret_name" \
            --secret-string "$SECRET_VALUE" \
            --kms-key-id "$KMS_KEY_ID" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ Migrated to AWS Secrets Manager${NC}"
            MIGRATED=$((MIGRATED + 1))
        else
            echo -e "${YELLOW}  ⚠ Secret may already exist, attempting update...${NC}"
            if $AWS_CMD secretsmanager update-secret \
                --secret-id "$AWS_SECRET_NAME" \
                --secret-string "$SECRET_VALUE" > /dev/null 2>&1; then
                echo -e "${GREEN}  ✓ Updated existing secret${NC}"
                MIGRATED=$((MIGRATED + 1))
            else
                echo -e "${RED}  ✗ Failed to create or update${NC}"
                FAILED=$((FAILED + 1))
            fi
        fi
    else
        if $AWS_CMD secretsmanager create-secret \
            --name "$AWS_SECRET_NAME" \
            --description "Migrated from Vault: $VAULT_PATH/$secret_name" \
            --secret-string "$SECRET_VALUE" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ Migrated to AWS Secrets Manager${NC}"
            MIGRATED=$((MIGRATED + 1))
        else
            echo -e "${YELLOW}  ⚠ Secret may already exist, attempting update...${NC}"
            if $AWS_CMD secretsmanager update-secret \
                --secret-id "$AWS_SECRET_NAME" \
                --secret-string "$SECRET_VALUE" > /dev/null 2>&1; then
                echo -e "${GREEN}  ✓ Updated existing secret${NC}"
                MIGRATED=$((MIGRATED + 1))
            else
                echo -e "${RED}  ✗ Failed to create or update${NC}"
                FAILED=$((FAILED + 1))
            fi
        fi
    fi

done <<< "$SECRETS"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Migration Complete${NC}"
else
    echo -e "${YELLOW}⚠ Migration Complete with Errors${NC}"
fi
echo ""
echo "Statistics:"
echo "  Total secrets: $SECRET_COUNT"
echo "  Migrated: $MIGRATED"
echo "  Failed: $FAILED"
echo ""
echo "Verify secrets:"
echo "  $AWS_CMD secretsmanager list-secrets"
echo ""
echo "Next steps:"
echo "  1. Update application configs to use AWS Secrets Manager"
echo "  2. Test application with new secrets"
echo "  3. Disable Vault secrets (DO NOT DELETE until verified)"
echo ""
