#!/bin/bash
# ============================================================================
# RUNTIME MONITOR: AWS GuardDuty
# ============================================================================
# Stage: RUNTIME
# When: Continuous (24/7)
# Speed: Real-time
# Purpose: Detect compromised instances, malicious IPs, cryptocurrency mining
# ============================================================================

set -e

echo "🔍 RUNTIME MONITOR: AWS GuardDuty"
echo "══════════════════════════════════"

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
# Get GuardDuty detector ID
# ============================================================================
echo "→ Getting GuardDuty detector..."
DETECTOR_ID=$(aws guardduty list-detectors --query 'DetectorIds[0]' --output text 2>/dev/null)

if [ "$DETECTOR_ID" = "None" ] || [ -z "$DETECTOR_ID" ]; then
  echo "⏭️  GuardDuty not enabled in this region"
  echo "   Enable: aws guardduty create-detector --enable"
  exit 0
fi

echo "Detector ID: $DETECTOR_ID"
echo

# ============================================================================
# List findings
# ============================================================================
echo "→ Querying GuardDuty findings..."
aws guardduty list-findings \
  --detector-id "$DETECTOR_ID" \
  --max-results 100 \
  --output json > "$OUTPUT_DIR/guardduty-finding-ids.json" 2>/dev/null

FINDING_IDS=$(jq -r '.FindingIds[]' "$OUTPUT_DIR/guardduty-finding-ids.json" 2>/dev/null || echo "")

if [ -z "$FINDING_IDS" ]; then
  echo "✅ No GuardDuty findings (good!)"
  echo "[]" > "$OUTPUT_DIR/guardduty-findings.json"
  exit 0
fi

# Get finding details
aws guardduty get-findings \
  --detector-id "$DETECTOR_ID" \
  --finding-ids $(echo $FINDING_IDS | tr '\n' ' ') \
  --output json > "$OUTPUT_DIR/guardduty-findings.json" 2>/dev/null

# ============================================================================
# Summarize findings by severity
# ============================================================================
LOW=$(jq '[.Findings[] | select(.Severity >= 1 and .Severity < 4)] | length' "$OUTPUT_DIR/guardduty-findings.json" 2>/dev/null || echo "0")
MEDIUM=$(jq '[.Findings[] | select(.Severity >= 4 and .Severity < 7)] | length' "$OUTPUT_DIR/guardduty-findings.json" 2>/dev/null || echo "0")
HIGH=$(jq '[.Findings[] | select(.Severity >= 7)] | length' "$OUTPUT_DIR/guardduty-findings.json" 2>/dev/null || echo "0")

echo "✅ GuardDuty findings collected"
echo "   LOW: $LOW"
echo "   MEDIUM: $MEDIUM"
echo "   HIGH: $HIGH"

# ============================================================================
# List HIGH severity findings
# ============================================================================
if [ "$HIGH" -gt 0 ]; then
  echo
  echo "⚠️  HIGH SEVERITY FINDINGS:"
  jq -r '.Findings[] | select(.Severity >= 7) | "   🚨 \(.Type): \(.Title)"' "$OUTPUT_DIR/guardduty-findings.json"
fi

echo
echo "✅ GuardDuty Monitoring Complete"
echo "   Results: $OUTPUT_DIR/guardduty-findings.json"
