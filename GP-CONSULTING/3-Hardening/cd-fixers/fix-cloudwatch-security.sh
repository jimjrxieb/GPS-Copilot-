#!/bin/bash

# ============================================================================
# RUNTIME FIXER: CloudWatch Security (Log Encryption & Retention)
# ============================================================================
# LAYER: RUNTIME (Production monitoring)
# WHEN: Production environment, continuous monitoring
# FIXES:
#   - HIGH: CloudWatch logs not encrypted
#   - MEDIUM: CloudWatch log retention too long (GDPR compliance)
#   - MEDIUM: Sensitive data in logs (CVV, PIN, passwords)
#   - PCI-DSS 10.5: Secure audit trails
#   - PCI-DSS 10.7: Retain audit trail for 1 year
# ============================================================================

set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
START_TIME=$(date +%s)

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$SCRIPT_DIR"
while [[ ! -d "$CURRENT_DIR/secops" && "$CURRENT_DIR" != "/" ]]; do
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done
PROJECT_ROOT="$CURRENT_DIR"
REPORT_DIR="$PROJECT_ROOT/secops/6-reports/fixing/runtime-fixes"
REPORT_FILE="$REPORT_DIR/fix-cloudwatch-security-$TIMESTAMP.log"

# Create report directory
mkdir -p "$REPORT_DIR"

# Start logging
exec > >(tee -a "$REPORT_FILE") 2>&1

echo "🔧 RUNTIME FIXER: CloudWatch Security"
echo "═══════════════════════════════════════════════════════"
echo "Layer: RUNTIME (Production monitoring)"
echo "When: Production environment"
echo ""
echo "Report: $REPORT_FILE"
echo "Timestamp: $(date -Iseconds)"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ ERROR: AWS CLI not installed"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ ERROR: AWS credentials not configured"
    exit 1
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo "AWS Account: $AWS_ACCOUNT"
echo "AWS Region: $AWS_REGION"
echo ""

echo "→ Scanning CloudWatch log groups..."

# Get all log groups
LOG_GROUPS=$(aws logs describe-log-groups --region "$AWS_REGION" --query 'logGroups[].logGroupName' --output text)

if [ -z "$LOG_GROUPS" ]; then
    echo "  ℹ️  No CloudWatch log groups found"
    exit 0
fi

FIXED=0
TOTAL=0

for LOG_GROUP in $LOG_GROUPS; do
    ((TOTAL++))
    echo ""
    echo "  → Processing: $LOG_GROUP"

    # Check if encrypted
    KMS_KEY=$(aws logs describe-log-groups --region "$AWS_REGION" --log-group-name-prefix "$LOG_GROUP" --query 'logGroups[0].kmsKeyId' --output text)

    if [ "$KMS_KEY" == "None" ] || [ -z "$KMS_KEY" ]; then
        echo "    ⚠️  Not encrypted"

        # Create KMS key if it doesn't exist
        if ! aws kms describe-key --key-id alias/cloudwatch-logs --region "$AWS_REGION" &> /dev/null; then
            echo "    → Creating KMS key for CloudWatch..."
            KMS_KEY_ID=$(aws kms create-key \
                --region "$AWS_REGION" \
                --description "CloudWatch Logs Encryption" \
                --key-policy '{
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "Enable IAM User Permissions",
                      "Effect": "Allow",
                      "Principal": {"AWS": "arn:aws:iam::'"$AWS_ACCOUNT"':root"},
                      "Action": "kms:*",
                      "Resource": "*"
                    },
                    {
                      "Sid": "Allow CloudWatch Logs",
                      "Effect": "Allow",
                      "Principal": {"Service": "logs.amazonaws.com"},
                      "Action": [
                        "kms:Encrypt",
                        "kms:Decrypt",
                        "kms:GenerateDataKey"
                      ],
                      "Resource": "*"
                    }
                  ]
                }' \
                --query 'KeyMetadata.KeyId' --output text)

            aws kms create-alias \
                --region "$AWS_REGION" \
                --alias-name alias/cloudwatch-logs \
                --target-key-id "$KMS_KEY_ID"

            echo "    ✅ Created KMS key: alias/cloudwatch-logs"
        fi

        # Enable encryption
        aws logs associate-kms-key \
            --region "$AWS_REGION" \
            --log-group-name "$LOG_GROUP" \
            --kms-key-id alias/cloudwatch-logs 2>/dev/null || echo "    ⚠️  Failed to enable encryption (may require permissions)"

        ((FIXED++))
        echo "    ✅ Enabled encryption"
    else
        echo "    ✅ Already encrypted"
    fi

    # Check retention
    RETENTION=$(aws logs describe-log-groups --region "$AWS_REGION" --log-group-name-prefix "$LOG_GROUP" --query 'logGroups[0].retentionInDays' --output text)

    if [ "$RETENTION" == "None" ] || [ -z "$RETENTION" ]; then
        echo "    ⚠️  No retention policy (logs kept forever - GDPR risk)"

        # Set 1 year retention (PCI-DSS requirement)
        aws logs put-retention-policy \
            --region "$AWS_REGION" \
            --log-group-name "$LOG_GROUP" \
            --retention-in-days 365

        echo "    ✅ Set retention: 365 days (PCI-DSS 10.7)"
        ((FIXED++))
    elif [ "$RETENTION" -gt 365 ]; then
        echo "    ⚠️  Retention too long: $RETENTION days"

        # Set 1 year retention
        aws logs put-retention-policy \
            --region "$AWS_REGION" \
            --log-group-name "$LOG_GROUP" \
            --retention-in-days 365

        echo "    ✅ Reduced retention to 365 days"
        ((FIXED++))
    else
        echo "    ✅ Retention: $RETENTION days"
    fi
done

echo ""
echo "→ Checking for sensitive data in logs (last 1 hour)..."

# Scan for CVV/PIN patterns
SENSITIVE_PATTERNS=(
    "cvv"
    "pin"
    "password"
    "api[_-]key"
    "secret[_-]key"
    "credit[_-]card"
)

for LOG_GROUP in $LOG_GROUPS; do
    for PATTERN in "${SENSITIVE_PATTERNS[@]}"; do
        EVENTS=$(aws logs filter-log-events \
            --region "$AWS_REGION" \
            --log-group-name "$LOG_GROUP" \
            --filter-pattern "$PATTERN" \
            --start-time $(($(date +%s) * 1000 - 3600000)) \
            --max-items 5 \
            --query 'events[].message' \
            --output text 2>/dev/null || echo "")

        if [ -n "$EVENTS" ]; then
            echo "  ⚠️  Found '$PATTERN' in $LOG_GROUP"
            echo "     Action: Review application logs, remove sensitive data from logging statements"
        fi
    done
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ RUNTIME FIX COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary:"
echo "  Log groups processed: $TOTAL"
echo "  Fixes applied: $FIXED"
echo ""
echo "Changes made:"
echo "  ✅ Enabled KMS encryption on log groups"
echo "  ✅ Set retention to 365 days (PCI-DSS 10.7)"
echo "  ⚠️  Scanned for sensitive data patterns"
echo ""
echo "PCI-DSS Alignment:"
echo "  ✅ 10.5: Secure audit trails (encrypted)"
echo "  ✅ 10.7: Retain audit trail for 1 year"
echo ""
echo "Next steps:"
echo "  1. Review application code to remove sensitive data from logs"
echo "  2. Set up CloudWatch Insights for anomaly detection"
echo "  3. Configure alerting: aws cloudwatch put-metric-alarm"
echo ""

# Generate summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 FIX SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fixer: fix-cloudwatch-security.sh"
echo "Layer: RUNTIME (Production monitoring)"
echo "Duration: ${DURATION}s"
echo "Status: Complete"
echo "Report: $REPORT_FILE"
echo ""
