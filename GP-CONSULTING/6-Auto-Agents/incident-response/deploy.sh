#!/bin/bash
set -e

#############################################################################
# GuardDuty Incident Response - Deployment Script
#############################################################################
# Purpose: Package and deploy the incident response Lambda function
# Usage:
#   ./deploy.sh dev           # Deploy to dev environment (dry-run enabled)
#   ./deploy.sh prod          # Deploy to prod environment (dry-run disabled)
#   ./deploy.sh prod --test   # Deploy and run test
#
# Prerequisites:
#   - AWS CLI configured
#   - Python 3.11 installed
#   - boto3 installed (pip install boto3)
#
# Author: GP-Copilot / Jade AI
# Date: October 13, 2025
#############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-dev}"
RUN_TEST="${2}"
STACK_NAME="guardduty-incident-response-${ENVIRONMENT}"
REGION="${AWS_REGION:-us-east-1}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  GuardDuty Incident Response - Deployment Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Environment:${NC} $ENVIRONMENT"
echo -e "${GREEN}Stack Name:${NC} $STACK_NAME"
echo -e "${GREEN}Region:${NC} $REGION"
echo ""

#############################################################################
# Step 1: Validate Prerequisites
#############################################################################
echo -e "${YELLOW}[1/7] Validating prerequisites...${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found. Please install it first.${NC}"
    exit 1
fi

# Check boto3
if ! python3 -c "import boto3" 2>/dev/null; then
    echo -e "${RED}Error: boto3 not found. Installing...${NC}"
    pip install boto3
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured.${NC}"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: ${ACCOUNT_ID}${NC}"
echo -e "${GREEN}✓ All prerequisites validated${NC}"
echo ""

#############################################################################
# Step 2: Run Tests
#############################################################################
echo -e "${YELLOW}[2/7] Running tests...${NC}"

# Test guardduty_responder.py
echo "Testing guardduty_responder.py (dry-run)..."
if python3 guardduty_responder.py --finding-file test-finding.json --dry-run > /dev/null 2>&1; then
    echo -e "${GREEN}✓ guardduty_responder.py test passed${NC}"
else
    echo -e "${RED}✗ guardduty_responder.py test failed${NC}"
    exit 1
fi

# Test lambda_handler.py
echo "Testing lambda_handler.py..."
if python3 lambda_handler.py > /dev/null 2>&1; then
    echo -e "${GREEN}✓ lambda_handler.py test passed${NC}"
else
    echo -e "${RED}✗ lambda_handler.py test failed${NC}"
    exit 1
fi

echo ""

#############################################################################
# Step 3: Create Deployment Package
#############################################################################
echo -e "${YELLOW}[3/7] Creating deployment package...${NC}"

# Create temp directory
TEMP_DIR=$(mktemp -d)
echo "Working directory: $TEMP_DIR"

# Copy Python files
cp guardduty_responder.py "$TEMP_DIR/"
cp forensics_collector.py "$TEMP_DIR/"
cp lambda_handler.py "$TEMP_DIR/"

# Install dependencies to temp dir
echo "Installing dependencies..."
pip install boto3 -t "$TEMP_DIR/" --quiet

# Create ZIP
DEPLOYMENT_PACKAGE="lambda-deployment-${ENVIRONMENT}.zip"
cd "$TEMP_DIR"
zip -r "$SCRIPT_DIR/$DEPLOYMENT_PACKAGE" . > /dev/null
cd "$SCRIPT_DIR"

# Clean up temp dir
rm -rf "$TEMP_DIR"

echo -e "${GREEN}✓ Deployment package created: ${DEPLOYMENT_PACKAGE}${NC}"
echo -e "${GREEN}  Size: $(du -h $DEPLOYMENT_PACKAGE | cut -f1)${NC}"
echo ""

#############################################################################
# Step 4: Deploy CloudFormation Stack
#############################################################################
echo -e "${YELLOW}[4/7] Deploying CloudFormation stack...${NC}"

# Set parameters based on environment
if [ "$ENVIRONMENT" = "prod" ]; then
    DRY_RUN_MODE="false"
    MIN_SEVERITY="4.0"  # HIGH and CRITICAL
    NOTIFICATION_EMAIL="${SECURITY_EMAIL:-security-team@example.com}"
else
    DRY_RUN_MODE="true"
    MIN_SEVERITY="1.0"  # All severities for testing
    NOTIFICATION_EMAIL="${SECURITY_EMAIL:-dev-team@example.com}"
fi

echo "Deploying stack with parameters:"
echo "  DryRunMode: $DRY_RUN_MODE"
echo "  MinimumSeverity: $MIN_SEVERITY"
echo "  NotificationEmail: $NOTIFICATION_EMAIL"

aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        DryRunMode="$DRY_RUN_MODE" \
        MinimumSeverity="$MIN_SEVERITY" \
        NotificationEmail="$NOTIFICATION_EMAIL" \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$REGION"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ CloudFormation stack deployed successfully${NC}"
else
    echo -e "${RED}✗ CloudFormation stack deployment failed${NC}"
    exit 1
fi

echo ""

#############################################################################
# Step 5: Upload Lambda Code
#############################################################################
echo -e "${YELLOW}[5/7] Uploading Lambda function code...${NC}"

FUNCTION_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionArn'].OutputValue" \
    --output text \
    --region "$REGION" | cut -d':' -f7)

echo "Function name: $FUNCTION_NAME"

aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file "fileb://$DEPLOYMENT_PACKAGE" \
    --region "$REGION" > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Lambda code uploaded successfully${NC}"
else
    echo -e "${RED}✗ Lambda code upload failed${NC}"
    exit 1
fi

echo ""

#############################################################################
# Step 6: Get Stack Outputs
#############################################################################
echo -e "${YELLOW}[6/7] Retrieving stack outputs...${NC}"

FORENSICS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ForensicsBucketName'].OutputValue" \
    --output text \
    --region "$REGION")

SNS_TOPIC=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='SNSTopicArn'].OutputValue" \
    --output text \
    --region "$REGION")

echo -e "${GREEN}✓ Lambda Function: ${FUNCTION_NAME}${NC}"
echo -e "${GREEN}✓ Forensics Bucket: ${FORENSICS_BUCKET}${NC}"
echo -e "${GREEN}✓ SNS Topic: ${SNS_TOPIC}${NC}"
echo ""

#############################################################################
# Step 7: Run Test (Optional)
#############################################################################
if [ "$RUN_TEST" = "--test" ]; then
    echo -e "${YELLOW}[7/7] Running integration test...${NC}"

    # Create test event
    cat > test-event.json << EOF
{
  "version": "0",
  "id": "test-event-$(date +%s)",
  "detail-type": "GuardDuty Finding",
  "source": "aws.guardduty",
  "account": "$ACCOUNT_ID",
  "time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "region": "$REGION",
  "resources": [],
  "detail": $(cat test-finding.json)
}
EOF

    echo "Invoking Lambda function with test event..."
    aws lambda invoke \
        --function-name "$FUNCTION_NAME" \
        --payload file://test-event.json \
        --region "$REGION" \
        test-response.json > /dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Lambda invocation successful${NC}"
        echo "Response:"
        cat test-response.json | python3 -m json.tool
        rm test-event.json test-response.json
    else
        echo -e "${RED}✗ Lambda invocation failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}[7/7] Skipping test (use --test to run)${NC}"
fi

echo ""

#############################################################################
# Deployment Complete
#############################################################################
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Deployment Complete!                                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Stack Name:${NC} $STACK_NAME"
echo -e "${BLUE}Lambda Function:${NC} $FUNCTION_NAME"
echo -e "${BLUE}Forensics Bucket:${NC} $FORENSICS_BUCKET"
echo -e "${BLUE}SNS Topic:${NC} $SNS_TOPIC"
echo -e "${BLUE}Environment:${NC} $ENVIRONMENT"
echo -e "${BLUE}Dry Run Mode:${NC} $DRY_RUN_MODE"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Confirm SNS subscription email"
echo "2. Enable GuardDuty (if not already enabled)"
echo "3. Test with: ./test-incident-response.sh"
echo "4. Monitor CloudWatch Logs: /aws/lambda/$FUNCTION_NAME"
echo "5. Check forensics bucket: s3://$FORENSICS_BUCKET/"
echo ""
echo -e "${GREEN}Documentation:${NC} See README.md for usage details"
echo ""
