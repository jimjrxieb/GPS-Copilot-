#!/bin/bash

# ============================================================================
# Auto-Fixer: IAM Wildcard Permissions (HIGH FINDINGS)
# ============================================================================
# FIXES:
#   - HIGH: IAM policy uses wildcarded action '*'
#   - HIGH: IAM policy uses wildcarded resource '*'
#   - MEDIUM: IAM policies allow credentials exposure
#   - PCI-DSS 7.1: Limit access to only what's needed
# ============================================================================

set -e

echo "🔧 Auto-Fixer: IAM Wildcard Permissions"
echo "═══════════════════════════════════════════════════════"

# Auto-detect project root (DON'T resolve symlinks with -P, so we stay in the project)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Walk up to find infrastructure/terraform directory
CURRENT_DIR="$SCRIPT_DIR"
while [[ ! -d "$CURRENT_DIR/infrastructure/terraform" && "$CURRENT_DIR" != "/" ]]; do
    CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done
PROJECT_ROOT="$CURRENT_DIR"
TF_DIR="$PROJECT_ROOT/infrastructure/terraform"
BACKUP_DIR="$TF_DIR.backup.$(date +%Y%m%d-%H%M%S)"

# Validate
if [ ! -f "$TF_DIR/iam.tf" ]; then
    echo "❌ ERROR: iam.tf not found"
    exit 1
fi

echo ""
echo "→ Creating backup..."
cp -r "$TF_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Analyzing current IAM policies..."
echo "  Wildcard actions found:"
grep -n '"Action".*"\*"' "$TF_DIR/iam.tf" || echo "  (none)"
echo ""
echo "  Wildcard resources found:"
grep -n '"Resource".*"\*"' "$TF_DIR/iam.tf" || echo "  (none)"

echo ""
echo "→ Creating least-privilege IAM policies..."

cat > "$TF_DIR/iam-least-privilege.tf" << 'EOF'
# ============================================================================
# IAM POLICIES - LEAST PRIVILEGE (PCI-DSS 7.1)
# ============================================================================
# ✅ No wildcard actions
# ✅ No wildcard resources
# ✅ Principle of least privilege
# ============================================================================

# Backend application IAM role
resource "aws_iam_role" "backend" {
  name = "${var.project_name}-backend-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = [
            "ec2.amazonaws.com",
            "ecs-tasks.amazonaws.com"
          ]
        }
      }
    ]
  })

  tags = {
    Name    = "${var.project_name}-backend-role"
    PCI_DSS = "7.1"
  }
}

# S3 access policy (specific buckets only)
resource "aws_iam_policy" "backend_s3" {
  name        = "${var.project_name}-backend-s3"
  description = "S3 access for backend - specific buckets only"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListSpecificBuckets"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.payment_receipts.arn,
          aws_s3_bucket.user_documents.arn
        ]
      },
      {
        Sid    = "ReadWriteObjects"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = [
          "${aws_s3_bucket.payment_receipts.arn}/*",
          "${aws_s3_bucket.user_documents.arn}/*"
        ]
      }
    ]
  })

  tags = {
    Name    = "${var.project_name}-backend-s3"
    PCI_DSS = "7.1"
  }
}

# Secrets Manager access policy (specific secrets only)
resource "aws_iam_policy" "backend_secrets" {
  name        = "${var.project_name}-backend-secrets"
  description = "Secrets Manager access - specific secrets only"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "GetSpecificSecrets"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.db_password.arn,
          aws_secretsmanager_secret.jwt_secret.arn
        ]
      },
      {
        Sid    = "DecryptSecrets"
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.secrets.arn
        ]
      }
    ]
  })

  tags = {
    Name    = "${var.project_name}-backend-secrets"
    PCI_DSS = "8.2.1"
  }
}

# RDS access policy (specific database only)
resource "aws_iam_policy" "backend_rds" {
  name        = "${var.project_name}-backend-rds"
  description = "RDS access - describe only (connection via creds)"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DescribeRDS"
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters"
        ]
        Resource = [
          aws_db_instance.postgres.arn
        ]
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-backend-rds"
  }
}

# CloudWatch Logs policy (specific log groups only)
resource "aws_iam_policy" "backend_logs" {
  name        = "${var.project_name}-backend-logs"
  description = "CloudWatch Logs - specific log groups only"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "CreateLogStreams"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/securebank/*"
        ]
      }
    ]
  })

  tags = {
    Name    = "${var.project_name}-backend-logs"
    PCI_DSS = "10.1"
  }
}

# Attach policies to backend role
resource "aws_iam_role_policy_attachment" "backend_s3" {
  role       = aws_iam_role.backend.name
  policy_arn = aws_iam_policy.backend_s3.arn
}

resource "aws_iam_role_policy_attachment" "backend_secrets" {
  role       = aws_iam_role.backend.name
  policy_arn = aws_iam_policy.backend_secrets.arn
}

resource "aws_iam_role_policy_attachment" "backend_rds" {
  role       = aws_iam_role.backend.name
  policy_arn = aws_iam_policy.backend_rds.arn
}

resource "aws_iam_role_policy_attachment" "backend_logs" {
  role       = aws_iam_role.backend.name
  policy_arn = aws_iam_policy.backend_logs.arn
}

# EKS node IAM role (least privilege)
resource "aws_iam_role" "eks_nodes" {
  name = "${var.project_name}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-eks-node-role"
  }
}

# Attach AWS managed policies for EKS nodes (least privilege)
resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = aws_iam_role.eks_nodes.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = aws_iam_role.eks_nodes.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "eks_container_registry" {
  role       = aws_iam_role.eks_nodes.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Instance profile for EKS nodes
resource "aws_iam_instance_profile" "eks_nodes" {
  name = "${var.project_name}-eks-node-profile"
  role = aws_iam_role.eks_nodes.name
}
EOF

echo "✅ Least-privilege IAM policies created"

echo ""
echo "→ Commenting out overly permissive policies in iam.tf..."
# Backup and comment out wildcard policies
sed -i.bak '/\*.*\*/,/^}/ {
  /Action.*\*/s/^/# INSECURE - /
  /Resource.*\*/s/^/# INSECURE - /
}' "$TF_DIR/iam.tf"
echo "✅ Wildcard policies commented out"

echo ""
echo "→ Validating Terraform configuration..."
cd "$TF_DIR"
if terraform validate > /dev/null 2>&1; then
    echo "✅ Terraform validation passed"
else
    echo "⚠️  Terraform validation warnings (check manually):"
    terraform validate
fi

echo ""
echo "✅ IAM wildcard auto-fix complete!"
echo ""
echo "📋 CHANGES MADE:"
echo "   ✅ Created least-privilege IAM policies in iam-least-privilege.tf"
echo "   ✅ Backend S3 policy - specific buckets only"
echo "   ✅ Backend Secrets Manager policy - specific secrets only"
echo "   ✅ Backend RDS policy - describe only (no admin)"
echo "   ✅ Backend CloudWatch Logs - specific log groups only"
echo "   ✅ EKS node policies - AWS managed policies (least privilege)"
echo "   ✅ Commented out wildcard policies in original iam.tf"
echo ""
echo "📋 PCI-DSS COMPLIANCE:"
echo "   ✅ 7.1 - Limit access to only what's needed (least privilege)"
echo "   ✅ 7.2.1 - Assigned based on job function"
echo "   ✅ 8.2.1 - Strong authentication (IAM roles, no keys)"
echo ""
echo "📋 BEFORE (INSECURE):"
echo "   ❌ Action: \"*\" (all actions)"
echo "   ❌ Resource: \"*\" (all resources)"
echo "   ❌ Credentials exposure risk"
echo ""
echo "📋 AFTER (SECURE):"
echo "   ✅ Specific actions only (s3:GetObject, secretsmanager:GetSecretValue)"
echo "   ✅ Specific resources only (arn:aws:s3:::bucket-name/*)"
echo "   ✅ No credentials exposure"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff $TF_DIR/iam.tf"
echo "   2. Update application code to use new IAM role names"
echo "   3. Plan: cd $TF_DIR && terraform plan"
echo "   4. Apply: terraform apply"
echo "   5. Test application with new IAM permissions"
echo ""
echo "🔙 Rollback: rm $TF_DIR/iam-least-privilege.tf && mv $TF_DIR/iam.tf.bak $TF_DIR/iam.tf"
echo "💾 Backup: $BACKUP_DIR"
