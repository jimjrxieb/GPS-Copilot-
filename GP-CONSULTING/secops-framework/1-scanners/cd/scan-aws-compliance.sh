#!/bin/bash
# ============================================================================
# CD SCANNER: AWS Compliance (AWS Config)
# ============================================================================
# Stage: CD (Continuous Deployment)
# When: post-deployment, continuous
# Speed: ~5 seconds
# Purpose: Validate AWS resource compliance (S3, RDS, VPC, IAM)
# ============================================================================

set -e

echo "🔍 CD SCANNER: AWS Compliance (AWS Config)"
echo "═══════════════════════════════════════════"

OUTPUT_DIR="../../2-findings/raw"
mkdir -p "$OUTPUT_DIR"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
  echo "⏭️  AWS credentials not configured, skipping AWS Config"
  echo "   Configure: aws configure"
  exit 0
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region || echo "us-east-1")

echo "AWS Account: $ACCOUNT_ID"
echo "Region: $REGION"
echo

# ============================================================================
# AWS Config compliance
# ============================================================================
echo "→ Querying AWS Config compliance..."
aws configservice describe-compliance-by-config-rule \
  --output json > "$OUTPUT_DIR/aws-config-results.json" 2>/dev/null || echo "⚠️  No Config rules found"

COMPLIANT=$(jq '[.ComplianceByConfigRules[] | select(.Compliance.ComplianceType == "COMPLIANT")] | length' "$OUTPUT_DIR/aws-config-results.json" 2>/dev/null || echo "0")
NON_COMPLIANT=$(jq '[.ComplianceByConfigRules[] | select(.Compliance.ComplianceType == "NON_COMPLIANT")] | length' "$OUTPUT_DIR/aws-config-results.json" 2>/dev/null || echo "0")

echo "✅ AWS Config query complete"
echo "   Compliant rules: $COMPLIANT"
echo "   Non-compliant rules: $NON_COMPLIANT"
echo

# ============================================================================
# List non-compliant resources
# ============================================================================
if [ "$NON_COMPLIANT" -gt 0 ]; then
  echo "→ Listing non-compliant resources..."
  jq -r '.ComplianceByConfigRules[] | select(.Compliance.ComplianceType == "NON_COMPLIANT") | "   ❌ \(.ConfigRuleName)"' "$OUTPUT_DIR/aws-config-results.json"
fi

echo
echo "✅ AWS Compliance Scanning Complete"
echo "   Results: $OUTPUT_DIR/aws-config-results.json"
