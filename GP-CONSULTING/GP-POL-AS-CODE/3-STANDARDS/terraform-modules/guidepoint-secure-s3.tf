# GuidePoint Security Standards - Secure S3 Bucket Module
# Implements "No public S3 buckets" and "All data encrypted" requirements
# Reference: GuidePoint Security Standards v2.0

# =============================================================================
# GuidePoint Standard: No public S3 buckets (CRITICAL)
# All buckets must be private with explicit deny for public access
# =============================================================================

resource "aws_s3_bucket" "guidepoint_secure" {
  bucket = var.bucket_name

  # GuidePoint Standard: Data classification tags required
  tags = {
    Name               = var.bucket_name
    DataClassification = var.data_classification  # Confidential/Internal/Public
    Compliance         = "GuidePoint-Security-Standards"
    EncryptionEnabled  = "true"
    PublicAccess       = "false"
    ManagedBy          = "GuidePoint-Security"
    Owner              = var.owner_email
    Environment        = var.environment
  }
}

# GuidePoint Standard: Block ALL public access (CRITICAL)
resource "aws_s3_bucket_public_access_block" "guidepoint_secure" {
  bucket = aws_s3_bucket.guidepoint_secure.id

  # GuidePoint Standard: All public access blocked
  block_public_acls       = true  # MUST be true
  block_public_policy     = true  # MUST be true
  ignore_public_acls      = true  # MUST be true
  restrict_public_buckets = true  # MUST be true
}

# =============================================================================
# GuidePoint Standard: All data encrypted at rest (CRITICAL)
# Default encryption with KMS required
# =============================================================================

# KMS key for S3 encryption (GuidePoint Standard)
resource "aws_kms_key" "s3_encryption" {
  description             = "GuidePoint S3 bucket encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true  # GuidePoint Standard: Key rotation

  tags = {
    Name               = "GuidePoint-S3-Encryption-Key"
    DataClassification = var.data_classification
    ManagedBy          = "GuidePoint-Security"
  }
}

resource "aws_kms_alias" "s3_encryption" {
  name          = "alias/guidepoint-s3-${var.bucket_name}"
  target_key_id = aws_kms_key.s3_encryption.key_id
}

# GuidePoint Standard: Default encryption with KMS
resource "aws_s3_bucket_server_side_encryption_configuration" "guidepoint_secure" {
  bucket = aws_s3_bucket.guidepoint_secure.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_encryption.arn
    }
    bucket_key_enabled = true  # Cost optimization with KMS
  }
}

# =============================================================================
# GuidePoint Standard: Versioning enabled for data protection
# =============================================================================
resource "aws_s3_bucket_versioning" "guidepoint_secure" {
  bucket = aws_s3_bucket.guidepoint_secure.id

  versioning_configuration {
    status = "Enabled"  # GuidePoint Standard: Versioning required
  }
}

# =============================================================================
# GuidePoint Standard: Logging enabled for audit trail
# =============================================================================
resource "aws_s3_bucket_logging" "guidepoint_secure" {
  bucket = aws_s3_bucket.guidepoint_secure.id

  target_bucket = var.logging_bucket_id
  target_prefix = "s3-access-logs/${var.bucket_name}/"
}

# =============================================================================
# GuidePoint Standard: Lifecycle policies for cost optimization
# =============================================================================
resource "aws_s3_bucket_lifecycle_configuration" "guidepoint_secure" {
  bucket = aws_s3_bucket.guidepoint_secure.id

  rule {
    id     = "guidepoint-intelligent-tiering"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "INTELLIGENT_TIERING"
    }

    transition {
      days          = 365
      storage_class = "GLACIER"
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

# =============================================================================
# GuidePoint Standard: Bucket policy with least privilege
# =============================================================================
data "aws_iam_policy_document" "guidepoint_bucket_policy" {
  # GuidePoint Standard: Deny unencrypted uploads
  statement {
    sid    = "DenyUnencryptedObjectUploads"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.guidepoint_secure.arn}/*"]
    condition {
      test     = "StringNotEquals"
      variable = "s3:x-amz-server-side-encryption"
      values   = ["aws:kms"]
    }
  }

  # GuidePoint Standard: Deny insecure transport
  statement {
    sid    = "DenyInsecureTransport"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.guidepoint_secure.arn,
      "${aws_s3_bucket.guidepoint_secure.arn}/*"
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }

  # GuidePoint Standard: Allow only authorized principals
  statement {
    sid    = "AllowAuthorizedAccess"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = var.authorized_principals
    }
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]
    resources = ["${aws_s3_bucket.guidepoint_secure.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "guidepoint_secure" {
  bucket = aws_s3_bucket.guidepoint_secure.id
  policy = data.aws_iam_policy_document.guidepoint_bucket_policy.json
}

# =============================================================================
# GuidePoint Standard: CORS configuration (if needed for web apps)
# =============================================================================
resource "aws_s3_bucket_cors_configuration" "guidepoint_secure" {
  count  = var.enable_cors ? 1 : 0
  bucket = aws_s3_bucket.guidepoint_secure.id

  cors_rule {
    allowed_headers = var.cors_allowed_headers
    allowed_methods = var.cors_allowed_methods
    allowed_origins = var.cors_allowed_origins
    max_age_seconds = 3600
  }
}

# =============================================================================
# Variables
# =============================================================================
variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
}

variable "data_classification" {
  description = "Data classification level (Confidential, Internal, Public)"
  type        = string
  validation {
    condition     = contains(["Confidential", "Internal", "Public"], var.data_classification)
    error_message = "Data classification must be Confidential, Internal, or Public per GuidePoint standards."
  }
}

variable "environment" {
  description = "Environment (production, staging, development)"
  type        = string
}

variable "owner_email" {
  description = "Owner email for tagging"
  type        = string
}

variable "logging_bucket_id" {
  description = "S3 bucket ID for access logs"
  type        = string
}

variable "authorized_principals" {
  description = "IAM principals authorized to access bucket"
  type        = list(string)
}

variable "enable_cors" {
  description = "Enable CORS configuration"
  type        = bool
  default     = false
}

variable "cors_allowed_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = []
}

variable "cors_allowed_methods" {
  description = "Allowed CORS methods"
  type        = list(string)
  default     = ["GET", "HEAD"]
}

variable "cors_allowed_headers" {
  description = "Allowed CORS headers"
  type        = list(string)
  default     = ["*"]
}

# =============================================================================
# Outputs
# =============================================================================
output "bucket_id" {
  description = "S3 bucket ID"
  value       = aws_s3_bucket.guidepoint_secure.id
}

output "bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.guidepoint_secure.arn
}

output "kms_key_id" {
  description = "KMS key ID for bucket encryption"
  value       = aws_kms_key.s3_encryption.id
}

output "bucket_regional_domain_name" {
  description = "S3 bucket regional domain name"
  value       = aws_s3_bucket.guidepoint_secure.bucket_regional_domain_name
}

# =============================================================================
# GUIDEPOINT SECURITY STANDARDS COMPLIANCE CHECKLIST
# =============================================================================
# ✓ No public S3 buckets - All public access blocked
# ✓ All data encrypted at rest - KMS encryption enforced
# ✓ All data encrypted in transit - HTTPS/TLS required
# ✓ Versioning enabled - Data protection and recovery
# ✓ Logging enabled - Audit trail for compliance
# ✓ Lifecycle policies - Cost optimization
# ✓ Bucket policy enforces encryption - Deny unencrypted uploads
# ✓ Secure transport only - Deny HTTP access
# ✓ Least privilege access - Explicit principal authorization
# ✓ Proper tagging - DataClassification, Owner, Environment
# ✓ Key rotation enabled - KMS key rotation
#
# This module is 100% compliant with GuidePoint Security Standards v2.0
# Contact: security@guidepoint.com for questions
# =============================================================================
