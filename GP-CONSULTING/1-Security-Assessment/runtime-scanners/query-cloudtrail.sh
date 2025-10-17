#!/bin/bash

# ============================================================================
# RUNTIME SCANNER: AWS CloudTrail - API Audit Trail Analysis
# ============================================================================
# LAYER: RUNTIME (Production monitoring)
# WHEN: Continuous (24/7), incident response
# MONITORS: AWS API calls, user activity, security events
# ============================================================================

set -e

echo "🔍 RUNTIME SCANNER: AWS CloudTrail"
echo "═══════════════════════════════════════════════════════"
echo "Layer: RUNTIME (Production monitoring)"
echo "When: Continuous (24/7)"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ ERROR: AWS CLI not installed"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null 2>&1; then
    echo "⚠️  WARNING: AWS credentials not configured"
    echo "  CloudTrail querying requires AWS credentials"
    echo "  Skipping..."
    exit 0
fi

AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo "AWS Account: $AWS_ACCOUNT"
echo "AWS Region: $AWS_REGION"
echo ""

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$SCRIPT_DIR"
while [[ ! -d "$CURRENT_DIR/secops" && "$CURRENT_DIR" != "/" ]]; do
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done
PROJECT_ROOT="$CURRENT_DIR"
OUTPUT_DIR="$PROJECT_ROOT/secops/2-findings/raw"

mkdir -p "$OUTPUT_DIR"

# Time range (last 24 hours)
START_TIME=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "→ Querying CloudTrail events (last 24 hours)..."
echo "  Start: $START_TIME"
echo "  End: $END_TIME"
echo ""

# ============================================================================
# SECURITY EVENT QUERIES
# ============================================================================

echo "→ Checking for suspicious activities..."
echo ""

# 1. Root account usage (CRITICAL - CIS AWS 1.7)
echo "  [1/8] Root account activity..."
ROOT_EVENTS=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --lookup-attributes AttributeKey=Username,AttributeValue=root \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --query 'Events[].{Time:EventTime,Event:EventName,User:Username,IP:SourceIPAddress}' \
    --output json 2>/dev/null || echo "[]")

ROOT_COUNT=$(echo "$ROOT_EVENTS" | jq 'length')
if [ "$ROOT_COUNT" -gt 0 ]; then
    echo "    ❌ CRITICAL: Root account used $ROOT_COUNT time(s) (CIS AWS 1.7)"
    echo "$ROOT_EVENTS" | jq -r '.[] | "       - \(.Time): \(.Event) from \(.IP)"'
else
    echo "    ✅ No root account activity"
fi
echo ""

# 2. Failed authentication attempts (possible brute force)
echo "  [2/8] Failed authentication attempts..."
FAILED_AUTH=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --lookup-attributes AttributeKey=EventName,AttributeValue=ConsoleLogin \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --query 'Events[?contains(CloudTrailEvent, `"errorCode"`)].{Time:EventTime,User:Username,IP:SourceIPAddress}' \
    --output json 2>/dev/null || echo "[]")

FAILED_COUNT=$(echo "$FAILED_AUTH" | jq 'length')
if [ "$FAILED_COUNT" -gt 5 ]; then
    echo "    ⚠️  WARNING: $FAILED_COUNT failed login attempts (possible brute force)"
    echo "$FAILED_AUTH" | jq -r '.[] | "       - \(.Time): \(.User) from \(.IP)"' | head -5
    echo "       (showing first 5)"
elif [ "$FAILED_COUNT" -gt 0 ]; then
    echo "    ℹ️  $FAILED_COUNT failed login attempts (normal)"
else
    echo "    ✅ No failed login attempts"
fi
echo ""

# 3. Security group changes (PCI-DSS 1.2.1)
echo "  [3/8] Security group modifications..."
SG_CHANGES=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --lookup-attributes AttributeKey=EventName,AttributeValue=AuthorizeSecurityGroupIngress \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --query 'Events[].{Time:EventTime,User:Username,Event:EventName,Resource:Resources[0].ResourceName}' \
    --output json 2>/dev/null || echo "[]")

SG_COUNT=$(echo "$SG_CHANGES" | jq 'length')
if [ "$SG_COUNT" -gt 0 ]; then
    echo "    ⚠️  $SG_COUNT security group change(s) detected"
    echo "$SG_CHANGES" | jq -r '.[] | "       - \(.Time): \(.User) modified \(.Resource)"'
else
    echo "    ✅ No security group changes"
fi
echo ""

# 4. S3 bucket policy changes (PCI-DSS 3.4)
echo "  [4/8] S3 bucket policy changes..."
S3_CHANGES=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::S3::Bucket \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --query 'Events[?EventName==`PutBucketPolicy` || EventName==`PutBucketAcl`].{Time:EventTime,User:Username,Event:EventName,Bucket:Resources[0].ResourceName}' \
    --output json 2>/dev/null || echo "[]")

S3_COUNT=$(echo "$S3_CHANGES" | jq 'length')
if [ "$S3_COUNT" -gt 0 ]; then
    echo "    ⚠️  $S3_COUNT S3 bucket policy change(s) detected"
    echo "$S3_CHANGES" | jq -r '.[] | "       - \(.Time): \(.User) changed \(.Bucket)"'
else
    echo "    ✅ No S3 bucket policy changes"
fi
echo ""

# 5. IAM changes (PCI-DSS 7.1, 8.2)
echo "  [5/8] IAM policy/role changes..."
IAM_CHANGES=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --lookup-attributes AttributeKey=EventName,AttributeValue=PutUserPolicy \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --query 'Events[].{Time:EventTime,User:Username,Event:EventName,Resource:Resources[0].ResourceName}' \
    --output json 2>/dev/null || echo "[]")

IAM_COUNT=$(echo "$IAM_CHANGES" | jq 'length')
if [ "$IAM_COUNT" -gt 0 ]; then
    echo "    ⚠️  $IAM_COUNT IAM change(s) detected"
    echo "$IAM_CHANGES" | jq -r '.[] | "       - \(.Time): \(.User) - \(.Event)"'
else
    echo "    ✅ No IAM changes"
fi
echo ""

# 6. Database deletions/modifications (PCI-DSS data integrity)
echo "  [6/8] Database deletions/modifications..."
DB_CHANGES=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::RDS::DBInstance \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --query 'Events[?EventName==`DeleteDBInstance` || EventName==`ModifyDBInstance`].{Time:EventTime,User:Username,Event:EventName,DB:Resources[0].ResourceName}' \
    --output json 2>/dev/null || echo "[]")

DB_COUNT=$(echo "$DB_CHANGES" | jq 'length')
if [ "$DB_COUNT" -gt 0 ]; then
    echo "    ⚠️  $DB_COUNT database change(s) detected"
    echo "$DB_CHANGES" | jq -r '.[] | "       - \(.Time): \(.User) - \(.Event) on \(.DB)"'
else
    echo "    ✅ No database changes"
fi
echo ""

# 7. Secret rotations/access (PCI-DSS 8.2.4)
echo "  [7/8] Secrets Manager activity..."
SECRET_ACCESS=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --lookup-attributes AttributeKey=EventName,AttributeValue=GetSecretValue \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --query 'Events[].{Time:EventTime,User:Username,Secret:Resources[0].ResourceName}' \
    --output json 2>/dev/null || echo "[]")

SECRET_COUNT=$(echo "$SECRET_ACCESS" | jq 'length')
if [ "$SECRET_COUNT" -gt 100 ]; then
    echo "    ⚠️  HIGH: $SECRET_COUNT secret accesses (possible enumeration attack)"
elif [ "$SECRET_COUNT" -gt 0 ]; then
    echo "    ℹ️  $SECRET_COUNT secret accesses (normal application usage)"
else
    echo "    ✅ No secret accesses"
fi
echo ""

# 8. Unusual API calls from unexpected IPs
echo "  [8/8] API calls from unusual locations..."
API_CALLS=$(aws cloudtrail lookup-events \
    --region "$AWS_REGION" \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --max-items 1000 \
    --query 'Events[].{Time:EventTime,Event:EventName,User:Username,IP:SourceIPAddress}' \
    --output json 2>/dev/null || echo "[]")

# Check for non-AWS IPs (crude check - production would use threat intelligence)
EXTERNAL_IPS=$(echo "$API_CALLS" | jq -r '.[].IP' | grep -v "^172\.\|^10\.\|^192\.168\." | sort -u | head -10)
if [ -n "$EXTERNAL_IPS" ]; then
    EXTERNAL_COUNT=$(echo "$EXTERNAL_IPS" | wc -l)
    echo "    ℹ️  API calls from $EXTERNAL_COUNT external IP(s):"
    echo "$EXTERNAL_IPS" | while read -r ip; do
        echo "       - $ip"
    done
else
    echo "    ✅ All API calls from internal IPs"
fi
echo ""

# ============================================================================
# SAVE RESULTS
# ============================================================================

echo "→ Saving detailed results..."

# Save all events to JSON
OUTPUT_FILE="$OUTPUT_DIR/cloudtrail-events.json"
cat > "$OUTPUT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "time_range": {
    "start": "$START_TIME",
    "end": "$END_TIME"
  },
  "account": "$AWS_ACCOUNT",
  "region": "$AWS_REGION",
  "findings": {
    "root_account_usage": $ROOT_EVENTS,
    "failed_authentication": $FAILED_AUTH,
    "security_group_changes": $SG_CHANGES,
    "s3_policy_changes": $S3_CHANGES,
    "iam_changes": $IAM_CHANGES,
    "database_changes": $DB_CHANGES,
    "secret_access": $SECRET_ACCESS
  },
  "summary": {
    "root_events": $ROOT_COUNT,
    "failed_auth": $FAILED_COUNT,
    "sg_changes": $SG_COUNT,
    "s3_changes": $S3_COUNT,
    "iam_changes": $IAM_COUNT,
    "db_changes": $DB_COUNT,
    "secret_access": $SECRET_COUNT
  }
}
EOF

echo "  ✅ Results saved: $OUTPUT_FILE"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 CLOUDTRAIL SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Root account usage: $ROOT_COUNT"
echo "Failed logins: $FAILED_COUNT"
echo "Security group changes: $SG_COUNT"
echo "S3 policy changes: $S3_COUNT"
echo "IAM changes: $IAM_COUNT"
echo "Database changes: $DB_COUNT"
echo "Secret accesses: $SECRET_COUNT"
echo ""

TOTAL_CRITICAL=$((ROOT_COUNT))
TOTAL_WARNINGS=$((SG_COUNT + S3_COUNT + IAM_COUNT + DB_COUNT))

if [ $TOTAL_CRITICAL -gt 0 ]; then
    echo "❌ CRITICAL FINDINGS: $TOTAL_CRITICAL"
elif [ $TOTAL_WARNINGS -gt 0 ]; then
    echo "⚠️  WARNINGS: $TOTAL_WARNINGS (review recommended)"
else
    echo "✅ No suspicious activity detected"
fi
echo ""
