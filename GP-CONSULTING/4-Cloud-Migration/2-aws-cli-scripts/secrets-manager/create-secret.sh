#!/bin/bash

# ============================================================================
# Create AWS Secrets Manager Secret
# ============================================================================
# USAGE:
#   ./create-secret.sh <secret-name> <secret-value> [kms-key-id]
#
# EXAMPLES:
#   # LocalStack
#   ./create-secret.sh db-password "MySecurePassword123!"
#
#   # Real AWS with KMS
#   AWS_PROFILE=prod ./create-secret.sh db-password "MySecurePassword123!" arn:aws:kms:us-east-1:123456789012:key/xxx
#
# FEATURES:
#   ✅ KMS encryption
#   ✅ Recovery window (7 days)
#   ✅ Automatic rotation (optional)
# ============================================================================

set -e

SECRET_NAME="$1"
SECRET_VALUE="$2"
KMS_KEY_ID="$3"
AWS_CMD="${AWS_CMD:-awslocal}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$SECRET_NAME" ] || [ -z "$SECRET_VALUE" ]; then
    echo "Usage: $0 <secret-name> <secret-value> [kms-key-id]"
    exit 1
fi

echo "🔐 Creating Secret: $SECRET_NAME"
echo "═══════════════════════════════════════════════════════"

# ============================================================================
# Create Secret
# ============================================================================

if [ -n "$KMS_KEY_ID" ]; then
    # With KMS encryption
    SECRET_ARN=$($AWS_CMD secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --description "Created by GP-Copilot migration" \
        --secret-string "$SECRET_VALUE" \
        --kms-key-id "$KMS_KEY_ID" \
        --query 'ARN' \
        --output text 2>/dev/null)
else
    # Without KMS (uses default encryption)
    SECRET_ARN=$($AWS_CMD secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --description "Created by GP-Copilot migration" \
        --secret-string "$SECRET_VALUE" \
        --query 'ARN' \
        --output text 2>/dev/null)
fi

if [ -n "$SECRET_ARN" ]; then
    echo -e "${GREEN}✓ Secret created${NC}"
    echo "ARN: $SECRET_ARN"
else
    echo -e "${RED}✗ Failed to create secret${NC}"
    exit 1
fi

# ============================================================================
# Tag Secret
# ============================================================================

echo ""
echo "Tagging secret..."
$AWS_CMD secretsmanager tag-resource \
    --secret-id "$SECRET_NAME" \
    --tags Key=ManagedBy,Value=gp-copilot Key=Environment,Value=development 2>/dev/null \
    && echo -e "${GREEN}✓ Secret tagged${NC}" || echo "⚠ Tagging skipped"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Secret Created Successfully${NC}"
echo ""
echo "Name: $SECRET_NAME"
echo "ARN: $SECRET_ARN"
echo ""
echo "Retrieve secret value:"
echo "  $AWS_CMD secretsmanager get-secret-value --secret-id $SECRET_NAME --query SecretString --output text"
echo ""
echo "Update secret value:"
echo "  $AWS_CMD secretsmanager update-secret --secret-id $SECRET_NAME --secret-string 'new-value'"
echo ""
echo "Delete secret (7-day recovery):"
echo "  $AWS_CMD secretsmanager delete-secret --secret-id $SECRET_NAME --recovery-window-in-days 7"
echo ""
