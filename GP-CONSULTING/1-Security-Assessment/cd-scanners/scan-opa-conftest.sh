#!/bin/bash

# ============================================================================
# CD SCANNER: OPA/Conftest - Pre-deployment Policy Validation
# ============================================================================
# LAYER: CD (Pre-deployment)
# WHEN: Before terraform apply, in CI/CD pipeline
# VALIDATES: Terraform plans against custom Rego policies
# BLOCKS: Deployment if violations found
# ============================================================================

set -e

echo "🔍 CD SCANNER: OPA/Conftest Policy Validation"
echo "═══════════════════════════════════════════════════════"
echo "Layer: CD (Infrastructure pre-deployment)"
echo "When: Before terraform apply"
echo ""

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_DIR="$SCRIPT_DIR"
while [[ ! -d "$CURRENT_DIR/infrastructure/terraform" && "$CURRENT_DIR" != "/" ]]; do
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done
PROJECT_ROOT="$CURRENT_DIR"
TF_DIR="$PROJECT_ROOT/infrastructure/terraform"

# Reference centralized Phase 3 policies (enforcement layer)
GP_CONSULTING="$(cd "$SCRIPT_DIR/../.." && pwd)"
POLICY_DIR="$GP_CONSULTING/3-Hardening/policies/opa"
# Fallback to local policies if Phase 3 not available
if [ ! -d "$POLICY_DIR" ]; then
    POLICY_DIR="$SCRIPT_DIR/opa-policies"
fi

OUTPUT_DIR="$PROJECT_ROOT/secops/2-findings/raw"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if Conftest is installed
if ! command -v conftest &> /dev/null; then
    echo "⚠️  Conftest not installed. Installing..."

    # Detect OS
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)

    if [[ "$ARCH" == "x86_64" ]]; then
        ARCH="x86_64"
    elif [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
        ARCH="arm64"
    fi

    VERSION="0.45.0"
    DOWNLOAD_URL="https://github.com/open-policy-agent/conftest/releases/download/v${VERSION}/conftest_${VERSION}_${OS^}_${ARCH}.tar.gz"

    echo "  Downloading: $DOWNLOAD_URL"
    curl -L "$DOWNLOAD_URL" -o /tmp/conftest.tar.gz
    tar xzf /tmp/conftest.tar.gz -C /tmp
    sudo mv /tmp/conftest /usr/local/bin/
    rm /tmp/conftest.tar.gz

    echo "  ✅ Conftest installed"
fi

echo "→ Conftest version:"
conftest --version
echo ""

# Validation
if [ ! -d "$TF_DIR" ]; then
    echo "❌ ERROR: Terraform directory not found: $TF_DIR"
    exit 1
fi

if [ ! -d "$POLICY_DIR" ]; then
    echo "❌ ERROR: OPA policy directory not found: $POLICY_DIR"
    exit 1
fi

echo "→ Policy source: Phase 3 Hardening (centralized enforcement policies)"
echo "  Location: $POLICY_DIR"
echo ""
echo "→ Found OPA policies:"
ls -1 "$POLICY_DIR"/*.rego | while read -r policy; do
    echo "  - $(basename "$policy")"
done
echo ""

# Generate Terraform plan in JSON format
echo "→ Generating Terraform plan..."
cd "$TF_DIR"

# Check if Terraform is initialized
if [ ! -d ".terraform" ]; then
    echo "  ⚠️  Terraform not initialized, running terraform init..."
    terraform init -backend=false > /dev/null 2>&1 || true
fi

# Generate plan (may fail due to demo violations, that's expected)
PLAN_FILE="/tmp/terraform-plan-$$.tfplan"
PLAN_JSON="/tmp/terraform-plan-$$.json"

echo "  Creating Terraform plan..."
if terraform plan -out="$PLAN_FILE" > /dev/null 2>&1; then
    echo "  ✅ Terraform plan created"
else
    echo "  ⚠️  Terraform plan had errors (expected in demo), continuing with available files..."
fi

# Convert plan to JSON (if plan was created)
if [ -f "$PLAN_FILE" ]; then
    terraform show -json "$PLAN_FILE" > "$PLAN_JSON" 2>/dev/null || true
    rm "$PLAN_FILE"
fi

# If no plan JSON, use raw .tf files
if [ ! -f "$PLAN_JSON" ] || [ ! -s "$PLAN_JSON" ]; then
    echo "  Using raw Terraform files for validation..."
fi

echo ""
echo "→ Running OPA/Conftest validation..."
echo ""

# Track results
TOTAL_VIOLATIONS=0
TOTAL_WARNINGS=0
POLICIES_TESTED=0

# Test each policy
for policy in "$POLICY_DIR"/*.rego; do
    POLICY_NAME=$(basename "$policy" .rego)
    ((POLICIES_TESTED++))

    echo "  Testing policy: $POLICY_NAME"

    # Test against Terraform files
    OUTPUT_FILE="$OUTPUT_DIR/conftest-${POLICY_NAME}.json"

    if conftest test "$TF_DIR" -p "$policy" --output json > "$OUTPUT_FILE" 2>&1; then
        echo "    ✅ PASS - No violations"
    else
        # Parse results
        if [ -f "$OUTPUT_FILE" ]; then
            FAILURES=$(jq -r '.[].failures | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
            WARNINGS=$(jq -r '.[].warnings | length' "$OUTPUT_FILE" 2>/dev/null || echo "0")

            if [ "$FAILURES" -gt 0 ]; then
                echo "    ❌ FAIL - $FAILURES violation(s)"
                TOTAL_VIOLATIONS=$((TOTAL_VIOLATIONS + FAILURES))

                # Show violations
                jq -r '.[].failures[]?' "$OUTPUT_FILE" 2>/dev/null | while read -r msg; do
                    echo "       - $msg"
                done
            fi

            if [ "$WARNINGS" -gt 0 ]; then
                echo "    ⚠️  WARN - $WARNINGS warning(s)"
                TOTAL_WARNINGS=$((TOTAL_WARNINGS + WARNINGS))

                # Show warnings
                jq -r '.[].warnings[]?' "$OUTPUT_FILE" 2>/dev/null | while read -r msg; do
                    echo "       - $msg"
                done
            fi
        else
            echo "    ⚠️  Could not parse results"
        fi
    fi
    echo ""
done

# Cleanup
rm -f "$PLAN_JSON"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SCAN SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Policies tested: $POLICIES_TESTED"
echo "Violations found: $TOTAL_VIOLATIONS"
echo "Warnings: $TOTAL_WARNINGS"
echo ""
echo "Results saved to: $OUTPUT_DIR/conftest-*.json"
echo ""

if [ $TOTAL_VIOLATIONS -gt 0 ]; then
    echo "❌ DEPLOYMENT BLOCKED - Fix violations before terraform apply"
    exit 1
else
    echo "✅ VALIDATION PASSED - Safe to deploy"
    exit 0
fi
