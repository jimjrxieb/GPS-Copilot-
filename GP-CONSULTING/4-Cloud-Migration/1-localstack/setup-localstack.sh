#!/bin/bash

# ============================================================================
# Setup LocalStack - Test AWS Locally
# ============================================================================
# PURPOSE:
#   Install and configure LocalStack for local AWS testing
#   No AWS costs, fast iteration, offline development
#
# USAGE:
#   ./setup-localstack.sh [--install-cli] [--start] [--test]
#
# OPTIONS:
#   --install-cli    Install awslocal CLI
#   --start          Start LocalStack container
#   --test           Run service tests
#   --all            Do everything (default)
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 LocalStack Setup"
echo "═══════════════════════════════════════════════════════"
echo ""

# ============================================================================
# Parse Arguments
# ============================================================================

INSTALL_CLI=false
START_LOCALSTACK=false
RUN_TESTS=false

if [ $# -eq 0 ] || [ "$1" = "--all" ]; then
    INSTALL_CLI=true
    START_LOCALSTACK=true
    RUN_TESTS=true
else
    for arg in "$@"; do
        case $arg in
            --install-cli) INSTALL_CLI=true ;;
            --start) START_LOCALSTACK=true ;;
            --test) RUN_TESTS=true ;;
            *)
                echo "Unknown option: $arg"
                echo "Usage: ./setup-localstack.sh [--install-cli] [--start] [--test] [--all]"
                exit 1
                ;;
        esac
    done
fi

# ============================================================================
# Install awslocal CLI
# ============================================================================

if [ "$INSTALL_CLI" = true ]; then
    echo "📦 Installing awslocal CLI..."

    # Check if pip is available
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        echo -e "${RED}❌ pip not found. Please install Python 3 and pip${NC}"
        exit 1
    fi

    # Install awscli-local
    if command -v pip3 &> /dev/null; then
        pip3 install --user awscli-local
    else
        pip install --user awscli-local
    fi

    # Verify installation
    if command -v awslocal &> /dev/null; then
        echo -e "${GREEN}✓ awslocal installed successfully${NC}"
        awslocal --version
    else
        echo -e "${YELLOW}⚠ awslocal installed but not in PATH${NC}"
        echo "Add to PATH: export PATH=\$HOME/.local/bin:\$PATH"
    fi

    echo ""
fi

# ============================================================================
# Start LocalStack
# ============================================================================

if [ "$START_LOCALSTACK" = true ]; then
    echo "🐳 Starting LocalStack container..."

    # Check if docker is running
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker is not running${NC}"
        exit 1
    fi

    # Check if LocalStack is already running
    if docker ps | grep -q localstack-aws; then
        echo -e "${YELLOW}⚠ LocalStack is already running${NC}"
        docker ps | grep localstack-aws
    else
        # Start LocalStack
        cd "$SCRIPT_DIR"
        docker-compose -f docker-compose.localstack.yml up -d

        # Wait for LocalStack to be ready
        echo "Waiting for LocalStack to start..."
        MAX_WAIT=60
        COUNTER=0

        while [ $COUNTER -lt $MAX_WAIT ]; do
            if curl -sf http://localhost:4566/_localstack/health > /dev/null 2>&1; then
                echo -e "${GREEN}✓ LocalStack is ready${NC}"
                break
            fi

            echo -n "."
            sleep 2
            COUNTER=$((COUNTER + 2))
        done

        if [ $COUNTER -ge $MAX_WAIT ]; then
            echo -e "${RED}❌ LocalStack failed to start within ${MAX_WAIT}s${NC}"
            docker logs localstack-aws
            exit 1
        fi
    fi

    # Show LocalStack info
    echo ""
    echo "LocalStack Info:"
    echo "  Container: localstack-aws"
    echo "  Endpoint: http://localhost:4566"
    echo "  Dashboard: https://app.localstack.cloud (if using Pro)"
    echo ""

    # Show running services
    echo "Available Services:"
    curl -s http://localhost:4566/_localstack/health | jq -r '.services | to_entries[] | "  \(.key): \(.value)"' || true

    echo ""
fi

# ============================================================================
# Configure AWS CLI for LocalStack
# ============================================================================

if [ "$START_LOCALSTACK" = true ]; then
    echo "⚙️  Configuring AWS CLI..."

    # Create AWS credentials (dummy values for LocalStack)
    mkdir -p ~/.aws

    if [ ! -f ~/.aws/credentials ]; then
        cat > ~/.aws/credentials <<EOF
[default]
aws_access_key_id = test
aws_secret_access_key = test
EOF
        echo -e "${GREEN}✓ Created ~/.aws/credentials${NC}"
    fi

    if [ ! -f ~/.aws/config ]; then
        cat > ~/.aws/config <<EOF
[default]
region = us-east-1
output = json
EOF
        echo -e "${GREEN}✓ Created ~/.aws/config${NC}"
    fi

    # Set environment variables
    export AWS_ACCESS_KEY_ID=test
    export AWS_SECRET_ACCESS_KEY=test
    export AWS_DEFAULT_REGION=us-east-1
    export AWS_ENDPOINT_URL=http://localhost:4566

    echo ""
    echo "Environment variables set:"
    echo "  AWS_ENDPOINT_URL=http://localhost:4566"
    echo "  AWS_DEFAULT_REGION=us-east-1"
    echo ""
fi

# ============================================================================
# Run Tests
# ============================================================================

if [ "$RUN_TESTS" = true ]; then
    echo "🧪 Testing LocalStack services..."
    echo ""

    # Wait a bit for services to fully initialize
    sleep 5

    # Test S3
    echo "Testing S3..."
    if awslocal s3 mb s3://test-bucket-$TIMESTAMP 2>/dev/null; then
        echo -e "${GREEN}✓ S3: Created bucket${NC}"
        awslocal s3 ls | grep "test-bucket-$TIMESTAMP"
        awslocal s3 rb s3://test-bucket-$TIMESTAMP 2>/dev/null
    else
        echo -e "${RED}✗ S3: Failed${NC}"
    fi

    # Test Secrets Manager
    echo "Testing Secrets Manager..."
    if awslocal secretsmanager create-secret \
        --name test-secret-$TIMESTAMP \
        --secret-string "test123" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Secrets Manager: Created secret${NC}"
        awslocal secretsmanager delete-secret \
            --secret-id test-secret-$TIMESTAMP \
            --force-delete-without-recovery > /dev/null 2>&1
    else
        echo -e "${RED}✗ Secrets Manager: Failed${NC}"
    fi

    # Test KMS
    echo "Testing KMS..."
    if KEY_ID=$(awslocal kms create-key --description "Test key" --query 'KeyMetadata.KeyId' --output text 2>/dev/null); then
        echo -e "${GREEN}✓ KMS: Created key ($KEY_ID)${NC}"
        awslocal kms schedule-key-deletion --key-id "$KEY_ID" --pending-window-in-days 7 > /dev/null 2>&1
    else
        echo -e "${RED}✗ KMS: Failed${NC}"
    fi

    # Test IAM
    echo "Testing IAM..."
    if awslocal iam create-role \
        --role-name test-role-$TIMESTAMP \
        --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ IAM: Created role${NC}"
        awslocal iam delete-role --role-name test-role-$TIMESTAMP > /dev/null 2>&1
    else
        echo -e "${RED}✗ IAM: Failed${NC}"
    fi

    # Test CloudWatch Logs
    echo "Testing CloudWatch Logs..."
    if awslocal logs create-log-group --log-group-name /test/logs-$TIMESTAMP 2>/dev/null; then
        echo -e "${GREEN}✓ CloudWatch Logs: Created log group${NC}"
        awslocal logs delete-log-group --log-group-name /test/logs-$TIMESTAMP 2>/dev/null
    else
        echo -e "${RED}✗ CloudWatch Logs: Failed${NC}"
    fi

    echo ""
fi

# ============================================================================
# Summary
# ============================================================================

echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}✅ LocalStack Setup Complete${NC}"
echo ""
echo "Quick Reference:"
echo "  Start:   docker-compose -f $SCRIPT_DIR/docker-compose.localstack.yml up -d"
echo "  Stop:    docker-compose -f $SCRIPT_DIR/docker-compose.localstack.yml down"
echo "  Logs:    docker logs localstack-aws"
echo "  Health:  curl http://localhost:4566/_localstack/health"
echo ""
echo "Use 'awslocal' instead of 'aws' for all commands:"
echo "  awslocal s3 ls"
echo "  awslocal secretsmanager list-secrets"
echo "  awslocal rds describe-db-instances"
echo ""
echo "Next steps:"
echo "  1. Run AWS CLI scripts: cd ../2-aws-cli-scripts/"
echo "  2. Test Terraform modules: cd ../3-terraform-modules/"
echo "  3. Run migration scripts: cd ../4-migration-scripts/"
echo ""
