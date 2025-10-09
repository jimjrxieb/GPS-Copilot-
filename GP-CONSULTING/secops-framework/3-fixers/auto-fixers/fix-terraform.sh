#!/bin/bash
set -e

echo "🔧 Auto-Fixer: Terraform Security Violations"
echo "═══════════════════════════════════════════════"

TF_DIR="../../../../infrastructure/terraform"

echo ""
echo "→ Enabling RDS encryption..."
sed -i 's/storage_encrypted[[:space:]]*=[[:space:]]*false/storage_encrypted = true/g' "$TF_DIR/rds.tf"
echo "✅ RDS encryption enabled"

echo ""
echo "→ Making RDS private..."
sed -i 's/publicly_accessible[[:space:]]*=[[:space:]]*true/publicly_accessible = false/g' "$TF_DIR/rds.tf"
echo "✅ RDS set to private"

echo ""
echo "→ Enabling S3 encryption..."
# Add server_side_encryption_configuration to S3 buckets
if ! grep -q "server_side_encryption_configuration" "$TF_DIR/s3.tf"; then
  sed -i '/resource "aws_s3_bucket" /,/^}/ {
    /^}/i \
\
  server_side_encryption_configuration {\
    rule {\
      apply_server_side_encryption_by_default {\
        sse_algorithm = "aws:kms"\
        kms_master_key_id = aws_kms_key.securebank.arn\
      }\
    }\
  }
  }' "$TF_DIR/s3.tf"
fi
echo "✅ S3 encryption enabled"

echo ""
echo "→ Blocking S3 public access..."
if ! grep -q "aws_s3_bucket_public_access_block" "$TF_DIR/s3.tf"; then
  cat >> "$TF_DIR/s3.tf" << 'EOF'

resource "aws_s3_bucket_public_access_block" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
EOF
fi
echo "✅ S3 public access blocked"

echo ""
echo "→ Enabling VPC flow logs..."
if ! grep -q "aws_flow_log" "$TF_DIR/vpc.tf"; then
  cat >> "$TF_DIR/vpc.tf" << 'EOF'

resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  name              = "/aws/vpc/securebank-flow-logs"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.securebank.arn
}

resource "aws_iam_role" "flow_logs" {
  name = "securebank-vpc-flow-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
}
EOF
fi
echo "✅ VPC flow logs enabled"

echo ""
echo "→ Enabling EKS private endpoint..."
sed -i 's/endpoint_public_access[[:space:]]*=[[:space:]]*true/endpoint_public_access = false/g' "$TF_DIR/eks.tf"
sed -i 's/endpoint_private_access[[:space:]]*=[[:space:]]*false/endpoint_private_access = true/g' "$TF_DIR/eks.tf"
echo "✅ EKS private endpoint enabled"

echo ""
echo "→ Enabling CloudWatch log encryption..."
if grep -q 'resource "aws_cloudwatch_log_group"' "$TF_DIR/cloudwatch.tf"; then
  sed -i '/resource "aws_cloudwatch_log_group"/,/^}/ {
    /^}/i \  kms_key_id = aws_kms_key.securebank.arn
  }' "$TF_DIR/cloudwatch.tf"
fi
echo "✅ CloudWatch log encryption enabled"

echo ""
echo "✅ Terraform auto-fixes complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: cd $TF_DIR && git diff"
echo "   2. Plan changes: terraform plan"
echo "   3. Apply changes: terraform apply"
