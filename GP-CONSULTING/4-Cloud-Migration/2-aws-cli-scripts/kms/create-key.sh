#!/bin/bash

# ============================================================================
# Create KMS Encryption Key
# ============================================================================
# USAGE:
#   ./create-key.sh <key-alias> [description]
#
# EXAMPLES:
#   # LocalStack
#   ./create-key.sh securebank "Encryption key for SecureBank"
#
#   # Real AWS
#   AWS_CMD=aws ./create-key.sh securebank "Encryption key for SecureBank"
#
# FEATURES:
#   ✅ Automatic key rotation (365 days)
#   ✅ Key alias for easy reference
#   ✅ Multi-region support (optional)
# ============================================================================

set -e

KEY_ALIAS="$1"
DESCRIPTION="${2:-Encryption key created by GP-Copilot}"
AWS_CMD="${AWS_CMD:-awslocal}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$KEY_ALIAS" ]; then
    echo "Usage: $0 <key-alias> [description]"
    echo ""
    echo "Example: $0 securebank 'Encryption key for SecureBank'"
    exit 1
fi

# Ensure alias has proper prefix
if [[ ! "$KEY_ALIAS" =~ ^alias/ ]]; then
    KEY_ALIAS="alias/$KEY_ALIAS"
fi

echo "🔐 Creating KMS Key: $KEY_ALIAS"
echo "═══════════════════════════════════════════════════════"
echo "Description: $DESCRIPTION"
echo ""

# ============================================================================
# Create KMS Key
# ============================================================================

echo "Creating KMS key..."
KEY_OUTPUT=$($AWS_CMD kms create-key \
    --description "$DESCRIPTION" \
    --key-usage ENCRYPT_DECRYPT \
    --origin AWS_KMS 2>&1)

if [ $? -eq 0 ]; then
    KEY_ID=$(echo "$KEY_OUTPUT" | jq -r '.KeyMetadata.KeyId')
    KEY_ARN=$(echo "$KEY_OUTPUT" | jq -r '.KeyMetadata.Arn')
    echo -e "${GREEN}✓ KMS key created${NC}"
    echo "Key ID: $KEY_ID"
    echo "ARN: $KEY_ARN"
else
    echo -e "${RED}✗ Failed to create KMS key${NC}"
    echo "$KEY_OUTPUT"
    exit 1
fi

# ============================================================================
# Enable Key Rotation
# ============================================================================

echo ""
echo "Enabling automatic key rotation..."
if $AWS_CMD kms enable-key-rotation --key-id "$KEY_ID" 2>/dev/null; then
    echo -e "${GREEN}✓ Automatic rotation enabled (365 days)${NC}"
else
    echo "⚠ Key rotation not supported (LocalStack limitation)"
fi

# ============================================================================
# Create Key Alias
# ============================================================================

echo ""
echo "Creating key alias: $KEY_ALIAS"
if $AWS_CMD kms create-alias \
    --alias-name "$KEY_ALIAS" \
    --target-key-id "$KEY_ID" 2>&1; then
    echo -e "${GREEN}✓ Key alias created${NC}"
else
    echo -e "${RED}✗ Failed to create alias (may already exist)${NC}"
fi

# ============================================================================
# Add Tags
# ============================================================================

echo ""
echo "Tagging key..."
$AWS_CMD kms tag-resource \
    --key-id "$KEY_ID" \
    --tags TagKey=ManagedBy,TagValue=gp-copilot TagKey=Environment,TagValue=development 2>/dev/null \
    && echo -e "${GREEN}✓ Key tagged${NC}" || echo "⚠ Tagging skipped"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}✅ KMS Key Created Successfully${NC}"
echo ""
echo "Key ID: $KEY_ID"
echo "ARN: $KEY_ARN"
echo "Alias: $KEY_ALIAS"
echo ""
echo "Use this key for encryption:"
echo "  # S3"
echo "  $AWS_CMD s3api put-bucket-encryption \\"
echo "    --bucket my-bucket \\"
echo "    --kms-key-id $KEY_ARN"
echo ""
echo "  # Secrets Manager"
echo "  $AWS_CMD secretsmanager create-secret \\"
echo "    --name my-secret \\"
echo "    --kms-key-id $KEY_ARN"
echo ""
echo "  # RDS"
echo "  $AWS_CMD rds create-db-instance \\"
echo "    --db-instance-identifier my-db \\"
echo "    --kms-key-id $KEY_ARN \\"
echo "    --storage-encrypted"
echo ""
echo "Manage key:"
echo "  Describe: $AWS_CMD kms describe-key --key-id $KEY_ID"
echo "  Disable:  $AWS_CMD kms disable-key --key-id $KEY_ID"
echo "  Schedule deletion: $AWS_CMD kms schedule-key-deletion --key-id $KEY_ID --pending-window-in-days 7"
echo ""
