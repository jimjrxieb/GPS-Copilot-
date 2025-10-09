#!/bin/bash

# ============================================================================
# Auto-Fixer: S3 Encryption & Public Access (HIGH FINDINGS)
# ============================================================================
# FIXES:
#   - HIGH: S3 buckets without encryption (PCI-DSS 3.4)
#   - HIGH: S3 buckets with public access blocks disabled
#   - HIGH: S3 buckets without versioning (PCI-DSS 10.5.3)
#   - HIGH: S3 buckets without logging (PCI-DSS 10.1)
# ============================================================================

set -e

echo "🔧 Auto-Fixer: S3 Encryption & Public Access"
echo "═══════════════════════════════════════════════════════"

TF_DIR="../../../../infrastructure/terraform"
BACKUP_DIR="$TF_DIR.backup.$(date +%Y%m%d-%H%M%S)"

# Validate
if [ ! -f "$TF_DIR/s3.tf" ]; then
    echo "❌ ERROR: s3.tf not found"
    exit 1
fi

echo ""
echo "→ Creating backup..."
cp -r "$TF_DIR" "$BACKUP_DIR"
echo "✅ Backup created: $BACKUP_DIR"

echo ""
echo "→ Fixing S3 public access blocks (CRITICAL)..."
sed -i.bak 's/block_public_acls[[:space:]]*=[[:space:]]*false/block_public_acls       = true/g' "$TF_DIR/s3.tf"
sed -i.bak 's/block_public_policy[[:space:]]*=[[:space:]]*false/block_public_policy     = true/g' "$TF_DIR/s3.tf"
sed -i.bak 's/ignore_public_acls[[:space:]]*=[[:space:]]*false/ignore_public_acls      = true/g' "$TF_DIR/s3.tf"
sed -i.bak 's/restrict_public_buckets[[:space:]]*=[[:space:]]*false/restrict_public_buckets = true/g' "$TF_DIR/s3.tf"
echo "✅ S3 public access blocked"

echo ""
echo "→ Removing public bucket policy..."
# Comment out the public bucket policy
sed -i.bak '/resource "aws_s3_bucket_policy" "payment_receipts_public"/,/^}/ s/^/# /' "$TF_DIR/s3.tf"
echo "✅ Public bucket policy disabled"

echo ""
echo "→ Adding S3 server-side encryption..."

# Create encryption configuration file
cat > "$TF_DIR/s3-encryption.tf" << 'EOF'
# ============================================================================
# S3 ENCRYPTION CONFIGURATION (PCI-DSS 3.4)
# ============================================================================

# Server-side encryption for payment receipts bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.id
    }
    bucket_key_enabled = true
  }
}

# Server-side encryption for user documents bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "user_documents" {
  bucket = aws_s3_bucket.user_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.id
    }
    bucket_key_enabled = true
  }
}

# Versioning for payment receipts (PCI-DSS 10.5.3 - audit trail)
resource "aws_s3_bucket_versioning" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Versioning for user documents
resource "aws_s3_bucket_versioning" "user_documents" {
  bucket = aws_s3_bucket.user_documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Access logging for payment receipts (PCI-DSS 10.1)
resource "aws_s3_bucket_logging" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access-logs/payment-receipts/"
}

# Access logging for user documents
resource "aws_s3_bucket_logging" "user_documents" {
  bucket = aws_s3_bucket.user_documents.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access-logs/user-documents/"
}

# Logs bucket (for access logs)
resource "aws_s3_bucket" "logs" {
  bucket        = "${var.project_name}-logs-${var.environment}"
  force_destroy = false  # Never delete logs

  tags = {
    Name        = "Access Logs"
    PCI_DSS     = "10.1"
    Description = "S3 access logs"
  }
}

# Block public access to logs bucket
resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Encrypt logs bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"  # Logs don't need KMS
    }
  }
}

# Lifecycle policy for logs (retain 90 days for PCI-DSS)
resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "delete-old-logs"
    status = "Enabled"

    expiration {
      days = 90
    }
  }
}

# KMS key for S3 encryption
resource "aws_kms_key" "s3" {
  description             = "${var.project_name} S3 encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name    = "${var.project_name}-s3-kms"
    PCI_DSS = "3.4"
  }
}

resource "aws_kms_alias" "s3" {
  name          = "alias/${var.project_name}-s3"
  target_key_id = aws_kms_key.s3.key_id
}

# KMS key policy to allow S3 service
resource "aws_kms_key_policy" "s3" {
  key_id = aws_kms_key.s3.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow S3 to use the key"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })
}
EOF

echo "✅ S3 encryption configuration created"

echo ""
echo "→ Validating Terraform configuration..."
cd "$TF_DIR"
if terraform validate > /dev/null 2>&1; then
    echo "✅ Terraform validation passed"
else
    echo "❌ Terraform validation failed!"
    echo ""
    echo "Common issues:"
    echo "  - Check if aws_caller_identity data source exists"
    echo "  - Verify bucket names match your s3.tf"
    echo ""
    terraform validate
    exit 1
fi

echo ""
echo "→ Showing changes..."
git diff "$TF_DIR/s3.tf" "$TF_DIR/s3-encryption.tf" 2>/dev/null | head -50 || echo "  (git not available)"

echo ""
echo "✅ S3 encryption auto-fix complete!"
echo ""
echo "📋 CHANGES MADE:"
echo "   ✅ Blocked ALL public access (block_public_acls = true)"
echo "   ✅ Disabled public bucket policy"
echo "   ✅ Enabled KMS encryption on payment_receipts bucket"
echo "   ✅ Enabled KMS encryption on user_documents bucket"
echo "   ✅ Enabled versioning (PCI-DSS 10.5.3 - audit trail)"
echo "   ✅ Enabled access logging (PCI-DSS 10.1)"
echo "   ✅ Created logs bucket with 90-day retention"
echo "   ✅ KMS key with automatic rotation"
echo ""
echo "📋 PCI-DSS COMPLIANCE:"
echo "   ✅ 3.4 - Render PAN unreadable (KMS encryption)"
echo "   ✅ 10.1 - Implement audit trails (access logging)"
echo "   ✅ 10.5.3 - Protect audit trails (versioning + logs)"
echo ""
echo "📋 Next steps:"
echo "   1. Review changes: git diff $TF_DIR/s3.tf"
echo "   2. Plan: cd $TF_DIR && terraform plan"
echo "   3. Apply: terraform apply"
echo "   4. Update application to use HTTPS (not HTTP) for S3 URLs"
echo "   5. Grant KMS permissions to backend IAM role"
echo ""
echo "🔙 Rollback: rm $TF_DIR/s3-encryption.tf && mv $TF_DIR/s3.tf.bak $TF_DIR/s3.tf"
echo "💾 Backup: $BACKUP_DIR"
