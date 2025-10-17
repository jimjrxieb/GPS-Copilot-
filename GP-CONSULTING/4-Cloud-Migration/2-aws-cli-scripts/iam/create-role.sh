#!/bin/bash

# ============================================================================
# Create IAM Role with Least Privilege
# ============================================================================
# USAGE:
#   ./create-role.sh <role-name> <trusted-service> [policy-arn1,policy-arn2,...]
#
# EXAMPLES:
#   # EC2 role
#   ./create-role.sh api-server-role ec2.amazonaws.com
#
#   # ECS task role
#   ./create-role.sh ecs-task-role ecs-tasks.amazonaws.com
#
#   # Lambda role with managed policies
#   ./create-role.sh lambda-role lambda.amazonaws.com \
#     "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
#
# TRUSTED SERVICES:
#   - ec2.amazonaws.com
#   - ecs-tasks.amazonaws.com
#   - lambda.amazonaws.com
#   - rds.amazonaws.com
#   - eks.amazonaws.com
# ============================================================================

set -e

ROLE_NAME="$1"
TRUSTED_SERVICE="$2"
POLICY_ARNS="${3:-}"
AWS_CMD="${AWS_CMD:-awslocal}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ -z "$ROLE_NAME" ] || [ -z "$TRUSTED_SERVICE" ]; then
    echo "Usage: $0 <role-name> <trusted-service> [policy-arns]"
    echo ""
    echo "Trusted services:"
    echo "  - ec2.amazonaws.com"
    echo "  - ecs-tasks.amazonaws.com"
    echo "  - lambda.amazonaws.com"
    echo "  - rds.amazonaws.com"
    echo "  - eks.amazonaws.com"
    echo ""
    echo "Example:"
    echo "  $0 api-server-role ec2.amazonaws.com"
    exit 1
fi

echo "👤 Creating IAM Role: $ROLE_NAME"
echo "═══════════════════════════════════════════════════════"
echo "Trusted Service: $TRUSTED_SERVICE"
echo ""

# ============================================================================
# Create AssumeRole Policy
# ============================================================================

ASSUME_ROLE_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "$TRUSTED_SERVICE"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
)

# ============================================================================
# Create IAM Role
# ============================================================================

echo "Creating IAM role..."
if ROLE_OUTPUT=$($AWS_CMD iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document "$ASSUME_ROLE_POLICY" \
    --description "Created by GP-Copilot migration" 2>&1); then

    ROLE_ARN=$(echo "$ROLE_OUTPUT" | jq -r '.Role.Arn')
    echo -e "${GREEN}✓ IAM role created${NC}"
    echo "ARN: $ROLE_ARN"
else
    echo -e "${RED}✗ Failed to create IAM role${NC}"
    echo "$ROLE_OUTPUT"
    exit 1
fi

# ============================================================================
# Attach Managed Policies
# ============================================================================

if [ -n "$POLICY_ARNS" ]; then
    echo ""
    echo "Attaching managed policies..."

    IFS=',' read -ra POLICIES <<< "$POLICY_ARNS"
    for policy_arn in "${POLICIES[@]}"; do
        echo "  Attaching: $policy_arn"
        if $AWS_CMD iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn "$policy_arn" 2>&1; then
            echo -e "${GREEN}    ✓ Attached${NC}"
        else
            echo -e "${RED}    ✗ Failed to attach${NC}"
        fi
    done
fi

# ============================================================================
# Create Instance Profile (for EC2)
# ============================================================================

if [ "$TRUSTED_SERVICE" = "ec2.amazonaws.com" ]; then
    echo ""
    echo "Creating instance profile for EC2..."

    if $AWS_CMD iam create-instance-profile \
        --instance-profile-name "$ROLE_NAME" 2>/dev/null; then
        echo -e "${GREEN}✓ Instance profile created${NC}"

        # Add role to instance profile
        if $AWS_CMD iam add-role-to-instance-profile \
            --instance-profile-name "$ROLE_NAME" \
            --role-name "$ROLE_NAME" 2>&1; then
            echo -e "${GREEN}✓ Role added to instance profile${NC}"
        fi
    else
        echo "⚠ Instance profile already exists or creation failed"
    fi
fi

# ============================================================================
# Tag Role
# ============================================================================

echo ""
echo "Tagging role..."
$AWS_CMD iam tag-role \
    --role-name "$ROLE_NAME" \
    --tags Key=ManagedBy,Value=gp-copilot Key=Environment,Value=development 2>/dev/null \
    && echo -e "${GREEN}✓ Role tagged${NC}" || echo "⚠ Tagging skipped"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}✅ IAM Role Created Successfully${NC}"
echo ""
echo "Role Name: $ROLE_NAME"
echo "ARN: $ROLE_ARN"
echo "Trusted Service: $TRUSTED_SERVICE"
echo ""

if [ -n "$POLICY_ARNS" ]; then
    echo "Attached Policies:"
    IFS=',' read -ra POLICIES <<< "$POLICY_ARNS"
    for policy_arn in "${POLICIES[@]}"; do
        echo "  - $policy_arn"
    done
    echo ""
fi

echo "Use this role:"
if [ "$TRUSTED_SERVICE" = "ec2.amazonaws.com" ]; then
    echo "  # Launch EC2 with this role"
    echo "  $AWS_CMD ec2 run-instances \\"
    echo "    --image-id ami-xxx \\"
    echo "    --instance-type t3.micro \\"
    echo "    --iam-instance-profile Name=$ROLE_NAME"
elif [ "$TRUSTED_SERVICE" = "ecs-tasks.amazonaws.com" ]; then
    echo "  # Use in ECS task definition"
    echo "  \"taskRoleArn\": \"$ROLE_ARN\""
elif [ "$TRUSTED_SERVICE" = "lambda.amazonaws.com" ]; then
    echo "  # Use in Lambda function"
    echo "  $AWS_CMD lambda create-function \\"
    echo "    --function-name my-function \\"
    echo "    --role $ROLE_ARN"
fi

echo ""
echo "Manage role:"
echo "  List policies: $AWS_CMD iam list-attached-role-policies --role-name $ROLE_NAME"
echo "  Detach policy: $AWS_CMD iam detach-role-policy --role-name $ROLE_NAME --policy-arn <arn>"
echo "  Delete role:   $AWS_CMD iam delete-role --role-name $ROLE_NAME"
echo ""
