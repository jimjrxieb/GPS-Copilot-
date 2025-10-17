#!/bin/bash
# ============================================================================
# AWS SECRETS MANAGER SETUP - SecureBank
# ============================================================================
# Creates AWS Secrets Manager secrets for SecureBank application
# PCI-DSS 8.2.1: Secure credential storage
# ============================================================================

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
LOCALSTACK_ENDPOINT="${LOCALSTACK_ENDPOINT:-http://localhost:4566}"

# Detect if using LocalStack or real AWS
if [[ "$LOCALSTACK_ENDPOINT" == *"localhost"* ]] || [[ "$LOCALSTACK_ENDPOINT" == *"127.0.0.1"* ]]; then
    echo "📦 Using LocalStack endpoint: $LOCALSTACK_ENDPOINT"
    ENDPOINT_FLAG="--endpoint-url=$LOCALSTACK_ENDPOINT"
else
    echo "☁️  Using real AWS endpoint"
    ENDPOINT_FLAG=""
fi

echo "============================================================================"
echo "AWS SECRETS MANAGER SETUP - SecureBank"
echo "============================================================================"
echo ""

# ============================================================================
# 1. Database Credentials
# ============================================================================
echo "1️⃣  Creating database credentials secret..."

aws $ENDPOINT_FLAG secretsmanager create-secret \
  --region "$AWS_REGION" \
  --name securebank/database \
  --description "SecureBank database credentials (PCI-DSS 8.2.1)" \
  --secret-string '{
    "username": "admin",
    "password": "SuperSecure123!",
    "host": "securebank-db.abc123.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "database": "securebank"
  }' \
  2>/dev/null || aws $ENDPOINT_FLAG secretsmanager update-secret \
  --region "$AWS_REGION" \
  --name securebank/database \
  --secret-string '{
    "username": "admin",
    "password": "SuperSecure123!",
    "host": "securebank-db.abc123.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "database": "securebank"
  }'

echo "✅ Database credentials created: securebank/database"

# ============================================================================
# 2. Stripe API Key
# ============================================================================
echo "2️⃣  Creating Stripe API key secret..."

aws $ENDPOINT_FLAG secretsmanager create-secret \
  --region "$AWS_REGION" \
  --name securebank/stripe-api-key \
  --description "Stripe payment processing API key" \
  --secret-string 'sk_live_abc123xyz789' \
  2>/dev/null || aws $ENDPOINT_FLAG secretsmanager update-secret \
  --region "$AWS_REGION" \
  --name securebank/stripe-api-key \
  --secret-string 'sk_live_abc123xyz789'

echo "✅ Stripe API key created: securebank/stripe-api-key"

# ============================================================================
# 3. JWT Signing Secret
# ============================================================================
echo "3️⃣  Creating JWT signing secret..."

aws $ENDPOINT_FLAG secretsmanager create-secret \
  --region "$AWS_REGION" \
  --name securebank/jwt-secret \
  --description "JWT token signing secret (PCI-DSS 8.2.1)" \
  --secret-string 'my-super-secret-jwt-key-12345' \
  2>/dev/null || aws $ENDPOINT_FLAG secretsmanager update-secret \
  --region "$AWS_REGION" \
  --name securebank/jwt-secret \
  --secret-string 'my-super-secret-jwt-key-12345'

echo "✅ JWT secret created: securebank/jwt-secret"

# ============================================================================
# 4. Encryption Key
# ============================================================================
echo "4️⃣  Creating encryption key secret..."

aws $ENDPOINT_FLAG secretsmanager create-secret \
  --region "$AWS_REGION" \
  --name securebank/encryption-key \
  --description "Application-level encryption key (PCI-DSS 3.4)" \
  --secret-string 'aes256-encryption-key-base64-encoded-value' \
  2>/dev/null || aws $ENDPOINT_FLAG secretsmanager update-secret \
  --region "$AWS_REGION" \
  --name securebank/encryption-key \
  --secret-string 'aes256-encryption-key-base64-encoded-value'

echo "✅ Encryption key created: securebank/encryption-key"

# ============================================================================
# 5. List All Secrets
# ============================================================================
echo ""
echo "📋 All SecureBank secrets:"
echo "============================================================================"

aws $ENDPOINT_FLAG secretsmanager list-secrets \
  --region "$AWS_REGION" \
  --query 'SecretList[?starts_with(Name, `securebank/`)].{Name:Name,Description:Description}' \
  --output table

echo ""
echo "✅ Secrets Manager setup complete!"
echo ""
echo "Retrieve a secret with:"
echo "  aws secretsmanager get-secret-value --secret-id securebank/database --query SecretString --output text"
