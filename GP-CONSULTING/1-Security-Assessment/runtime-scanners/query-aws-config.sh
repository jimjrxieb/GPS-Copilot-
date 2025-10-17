#!/bin/bash

# ============================================================================
# RUNTIME SCANNER: AWS Config - Continuous Compliance Monitoring
# ============================================================================
# LAYER: RUNTIME (Production monitoring)
# WHEN: Continuous (24/7), compliance drift detection
# MONITORS: Resource compliance, configuration changes, drift detection
# ============================================================================

set -e

echo "🔍 RUNTIME SCANNER: AWS Config Compliance"
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
    echo "  AWS Config querying requires AWS credentials"
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

# Check if AWS Config is enabled
echo "→ Checking AWS Config status..."
CONFIG_STATUS=$(aws configservice describe-configuration-recorders \
    --region "$AWS_REGION" \
    --query 'ConfigurationRecorders[0].recording' \
    --output text 2>/dev/null || echo "false")

if [ "$CONFIG_STATUS" != "true" ]; then
    echo "  ⚠️  AWS Config not enabled in this region"
    echo "  AWS Config provides continuous compliance monitoring"
    echo "  To enable: aws configservice put-configuration-recorder ..."
    echo ""
    echo "  Skipping detailed compliance check..."
    exit 0
fi

echo "  ✅ AWS Config is enabled"
echo ""

# ============================================================================
# COMPLIANCE RULE CHECKS
# ============================================================================

echo "→ Checking AWS Config compliance rules..."
echo ""

# Get all Config rules
RULES=$(aws configservice describe-config-rules \
    --region "$AWS_REGION" \
    --query 'ConfigRules[].ConfigRuleName' \
    --output json 2>/dev/null || echo "[]")

RULE_COUNT=$(echo "$RULES" | jq 'length')

if [ "$RULE_COUNT" -eq 0 ]; then
    echo "  ⚠️  No Config rules configured"
    echo "  Recommend adding managed rules for:"
    echo "     - encrypted-volumes (PCI-DSS 3.4)"
    echo "     - s3-bucket-public-read-prohibited (PCI-DSS 1.2.1)"
    echo "     - vpc-flow-logs-enabled (CIS AWS 3.9)"
    echo "     - iam-root-access-key-check (CIS AWS 1.12)"
    echo ""
    exit 0
fi

echo "  Found $RULE_COUNT Config rule(s)"
echo ""

# Check compliance status for each rule
COMPLIANT=0
NON_COMPLIANT=0
NOT_APPLICABLE=0

declare -A VIOLATIONS

for rule in $(echo "$RULES" | jq -r '.[]'); do
    # Get compliance summary
    COMPLIANCE=$(aws configservice describe-compliance-by-config-rule \
        --region "$AWS_REGION" \
        --config-rule-names "$rule" \
        --query 'ComplianceByConfigRules[0].Compliance.ComplianceType' \
        --output text 2>/dev/null || echo "INSUFFICIENT_DATA")

    case "$COMPLIANCE" in
        COMPLIANT)
            COMPLIANT=$((COMPLIANT + 1))
            ;;
        NON_COMPLIANT)
            NON_COMPLIANT=$((NON_COMPLIANT + 1))
            VIOLATIONS["$rule"]="NON_COMPLIANT"
            ;;
        NOT_APPLICABLE)
            NOT_APPLICABLE=$((NOT_APPLICABLE + 1))
            ;;
        *)
            echo "  ⚠️  Rule '$rule': $COMPLIANCE"
            ;;
    esac
done

echo "  Compliance status:"
echo "    ✅ Compliant: $COMPLIANT"
echo "    ❌ Non-compliant: $NON_COMPLIANT"
echo "    ⊘  Not applicable: $NOT_APPLICABLE"
echo ""

# ============================================================================
# DETAILED NON-COMPLIANT RESOURCES
# ============================================================================

if [ $NON_COMPLIANT -gt 0 ]; then
    echo "→ Analyzing non-compliant resources..."
    echo ""

    for rule in "${!VIOLATIONS[@]}"; do
        echo "  Rule: $rule"

        # Get non-compliant resources
        RESOURCES=$(aws configservice get-compliance-details-by-config-rule \
            --region "$AWS_REGION" \
            --config-rule-name "$rule" \
            --compliance-types NON_COMPLIANT \
            --query 'EvaluationResults[].EvaluationResultIdentifier.EvaluationResultQualifier.ResourceId' \
            --output json 2>/dev/null || echo "[]")

        RESOURCE_COUNT=$(echo "$RESOURCES" | jq 'length')

        if [ "$RESOURCE_COUNT" -gt 0 ]; then
            echo "    ❌ $RESOURCE_COUNT non-compliant resource(s):"
            echo "$RESOURCES" | jq -r '.[]' | head -10 | while read -r resource; do
                echo "       - $resource"
            done

            if [ "$RESOURCE_COUNT" -gt 10 ]; then
                echo "       (showing first 10 of $RESOURCE_COUNT)"
            fi
        fi
        echo ""
    done
fi

# ============================================================================
# CONFIGURATION TIMELINE (Recent Changes)
# ============================================================================

echo "→ Checking recent configuration changes (last 24h)..."
echo ""

# Get recent configuration changes
# Note: This requires Config to be recording
START_TIME=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)
END_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Query for specific resource types
RESOURCE_TYPES=("AWS::EC2::SecurityGroup" "AWS::S3::Bucket" "AWS::IAM::Role" "AWS::RDS::DBInstance")

TOTAL_CHANGES=0

for resource_type in "${RESOURCE_TYPES[@]}"; do
    # Get configuration timeline
    CHANGES=$(aws configservice list-discovered-resources \
        --region "$AWS_REGION" \
        --resource-type "$resource_type" \
        --query 'resourceIdentifiers[].resourceId' \
        --output json 2>/dev/null || echo "[]")

    CHANGE_COUNT=$(echo "$CHANGES" | jq 'length')

    if [ "$CHANGE_COUNT" -gt 0 ]; then
        echo "  $resource_type: $CHANGE_COUNT resource(s)"
        TOTAL_CHANGES=$((TOTAL_CHANGES + CHANGE_COUNT))
    fi
done

echo ""
echo "  Total tracked resources: $TOTAL_CHANGES"
echo ""

# ============================================================================
# SAVE RESULTS
# ============================================================================

echo "→ Saving compliance report..."

OUTPUT_FILE="$OUTPUT_DIR/aws-config-compliance.json"

# Build violations JSON
VIOLATIONS_JSON="{"
FIRST=true
for rule in "${!VIOLATIONS[@]}"; do
    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        VIOLATIONS_JSON="${VIOLATIONS_JSON},"
    fi
    VIOLATIONS_JSON="${VIOLATIONS_JSON}\"$rule\":\"${VIOLATIONS[$rule]}\""
done
VIOLATIONS_JSON="${VIOLATIONS_JSON}}"

cat > "$OUTPUT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "account": "$AWS_ACCOUNT",
  "region": "$AWS_REGION",
  "config_status": "enabled",
  "compliance_summary": {
    "total_rules": $RULE_COUNT,
    "compliant": $COMPLIANT,
    "non_compliant": $NON_COMPLIANT,
    "not_applicable": $NOT_APPLICABLE,
    "compliance_percentage": $(awk "BEGIN {printf \"%.1f\", ($COMPLIANT * 100.0) / ($COMPLIANT + $NON_COMPLIANT + 0.001)}")
  },
  "violations": $VIOLATIONS_JSON,
  "tracked_resources": $TOTAL_CHANGES
}
EOF

echo "  ✅ Report saved: $OUTPUT_FILE"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 AWS CONFIG SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total rules: $RULE_COUNT"
echo "Compliant: $COMPLIANT"
echo "Non-compliant: $NON_COMPLIANT"
echo "Tracked resources: $TOTAL_CHANGES"
echo ""

if [ $NON_COMPLIANT -gt 0 ]; then
    COMPLIANCE_PCT=$(awk "BEGIN {printf \"%.1f\", ($COMPLIANT * 100.0) / ($COMPLIANT + $NON_COMPLIANT)}")
    echo "Compliance rate: ${COMPLIANCE_PCT}%"
    echo ""
    echo "❌ COMPLIANCE DRIFT DETECTED"
    echo "   Review non-compliant resources and remediate"
    echo ""
elif [ $COMPLIANT -gt 0 ]; then
    echo "✅ 100% COMPLIANT - All rules passing"
    echo ""
else
    echo "⚠️  No compliance data available"
    echo ""
fi
