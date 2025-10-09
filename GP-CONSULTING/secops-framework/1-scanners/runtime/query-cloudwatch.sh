#!/bin/bash
# ============================================================================
# RUNTIME MONITOR: CloudWatch Logs
# ============================================================================
# Stage: RUNTIME
# When: Continuous (24/7)
# Speed: Real-time
# Purpose: Query application logs for errors and anomalies
# ============================================================================

set -e

echo "🔍 RUNTIME MONITOR: CloudWatch Logs"
echo "═══════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

if ! aws sts get-caller-identity &> /dev/null; then
  echo "⏭️  AWS credentials not configured"
  exit 0
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region || echo "us-east-1")

echo "AWS Account: $ACCOUNT_ID"
echo "Region: $REGION"
echo

# ============================================================================
# List log groups
# ============================================================================
echo "→ Listing CloudWatch log groups..."
aws logs describe-log-groups \
  --query 'logGroups[?contains(logGroupName, `securebank`) || contains(logGroupName, `aws`)].logGroupName' \
  --output json > "$OUTPUT_DIR/cloudwatch-log-groups.json" 2>/dev/null

LOG_GROUPS=$(jq -r '.[]' "$OUTPUT_DIR/cloudwatch-log-groups.json" 2>/dev/null || echo "")

if [ -z "$LOG_GROUPS" ]; then
  echo "⏭️  No log groups found"
  exit 0
fi

echo "Found $(echo "$LOG_GROUPS" | wc -l) log groups"
echo

# ============================================================================
# Query errors in last hour
# ============================================================================
START_TIME=$(date -u -d '1 hour ago' +%s)000
END_TIME=$(date -u +%s)000

echo "→ Querying errors in last hour..."

# Query each log group
for LOG_GROUP in $LOG_GROUPS; do
  echo "   Scanning: $LOG_GROUP"

  aws logs filter-log-events \
    --log-group-name "$LOG_GROUP" \
    --filter-pattern "ERROR" \
    --start-time "$START_TIME" \
    --end-time "$END_TIME" \
    --output json >> "$OUTPUT_DIR/cloudwatch-errors-temp.json" 2>/dev/null || echo "     (no errors)"
done

# Combine results
if [ -f "$OUTPUT_DIR/cloudwatch-errors-temp.json" ]; then
  jq -s 'add | {events: [.[]?.events[]?] | unique_by(.eventId)}' "$OUTPUT_DIR/cloudwatch-errors-temp.json" > "$OUTPUT_DIR/cloudwatch-errors.json"
  rm "$OUTPUT_DIR/cloudwatch-errors-temp.json"

  ERROR_COUNT=$(jq '.events | length' "$OUTPUT_DIR/cloudwatch-errors.json" 2>/dev/null || echo "0")
  echo "✅ Found $ERROR_COUNT error events in last hour"
else
  echo "✅ No errors found (good!)"
  echo '{"events": []}' > "$OUTPUT_DIR/cloudwatch-errors.json"
fi

# ============================================================================
# Query recent 5xx responses
# ============================================================================
echo
echo "→ Querying 5xx HTTP responses..."

aws logs filter-log-events \
  --log-group-name "/aws/lambda/securebank" \
  --filter-pattern "\"HTTP/1.1\" 5" \
  --start-time "$START_TIME" \
  --end-time "$END_TIME" \
  --output json > "$OUTPUT_DIR/cloudwatch-5xx-errors.json" 2>/dev/null || echo "   (no 5xx errors)"

if [ -f "$OUTPUT_DIR/cloudwatch-5xx-errors.json" ]; then
  HTTP_ERRORS=$(jq '.events | length' "$OUTPUT_DIR/cloudwatch-5xx-errors.json" 2>/dev/null || echo "0")
  echo "✅ Found $HTTP_ERRORS HTTP 5xx responses"
fi

echo
echo "✅ CloudWatch Logs Monitoring Complete"
echo "   Results: $OUTPUT_DIR/cloudwatch-errors.json"
echo "   Results: $OUTPUT_DIR/cloudwatch-5xx-errors.json"
