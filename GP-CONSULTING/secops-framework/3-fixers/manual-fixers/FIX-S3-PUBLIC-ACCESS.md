# Manual Fix Guide: S3 Public Access

## Problem

**PCI-DSS Violation:** S3 bucket containing payment receipts is publicly accessible
- **Requirement:** PCI-DSS 1.2.1 - Restrict inbound/outbound traffic
- **Risk:** CRITICAL - Sensitive payment data exposed to internet
- **Current State:** Public ACL enabled, no bucket policy restrictions

## Solution Overview

Block all public access to S3 bucket and implement secure access via CloudFront CDN with signed URLs.

## Prerequisites

- [x] AWS CLI configured with admin access
- [x] CloudFront distribution available (or will create)
- [x] List of authorized users/applications
- [x] Backup of current bucket policy

## Step-by-Step Instructions

### Step 1: Audit Current Public Access

```bash
# Check current bucket ACL
aws s3api get-bucket-acl \
  --bucket securebank-payment-receipts \
  --region us-east-1

# Check bucket policy
aws s3api get-bucket-policy \
  --bucket securebank-payment-receipts \
  --region us-east-1 || echo "No bucket policy"

# List objects to understand scope
aws s3 ls s3://securebank-payment-receipts/ --recursive | wc -l
```

### Step 2: Enable S3 Block Public Access

```bash
# Block ALL public access (recommended for PCI-DSS)
aws s3api put-public-access-block \
  --bucket securebank-payment-receipts \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
  --region us-east-1

echo "✅ Public access blocked"

# Verify settings
aws s3api get-public-access-block \
  --bucket securebank-payment-receipts \
  --region us-east-1
```

### Step 3: Remove Public ACLs

```bash
# Set bucket ACL to private
aws s3api put-bucket-acl \
  --bucket securebank-payment-receipts \
  --acl private \
  --region us-east-1

# Remove any object-level public ACLs
aws s3api list-objects-v2 \
  --bucket securebank-payment-receipts \
  --region us-east-1 \
  --query 'Contents[].Key' \
  --output text | \
  xargs -I {} aws s3api put-object-acl \
    --bucket securebank-payment-receipts \
    --key {} \
    --acl private \
    --region us-east-1

echo "✅ All ACLs set to private"
```

### Step 4: Create Restrictive Bucket Policy

```bash
# Create bucket policy allowing only CloudFront and backend service
cat > /tmp/bucket-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::securebank-payment-receipts/*",
      "Condition": {
        "StringNotEquals": {
          "aws:SourceVpc": "vpc-xxxxx"
        }
      }
    },
    {
      "Sid": "AllowCloudFrontAccess",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::securebank-payment-receipts/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
        }
      }
    },
    {
      "Sid": "AllowBackendServiceAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:role/securebank-backend-role"
      },
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::securebank-payment-receipts/*"
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::securebank-payment-receipts/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    }
  ]
}
EOF

# Apply bucket policy
aws s3api put-bucket-policy \
  --bucket securebank-payment-receipts \
  --policy file:///tmp/bucket-policy.json \
  --region us-east-1

echo "✅ Restrictive bucket policy applied"
```

### Step 5: Create CloudFront Distribution (Secure Access)

```bash
# Create Origin Access Identity for CloudFront
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
  --cloud-front-origin-access-identity-config \
    CallerReference=$(date +%s),Comment="SecureBank S3 access" \
  --query 'CloudFrontOriginAccessIdentity.Id' \
  --output text)

echo "CloudFront OAI created: $OAI_ID"

# Create CloudFront distribution config
cat > /tmp/cloudfront-config.json << EOF
{
  "CallerReference": "$(date +%s)",
  "Comment": "SecureBank Payment Receipts CDN",
  "Enabled": true,
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-securebank-payment-receipts",
        "DomainName": "securebank-payment-receipts.s3.us-east-1.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/$OAI_ID"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-securebank-payment-receipts",
    "ViewerProtocolPolicy": "https-only",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "TrustedSigners": {
      "Enabled": true,
      "Quantity": 1,
      "Items": ["self"]
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000,
    "Compress": true
  },
  "ViewerCertificate": {
    "CloudFrontDefaultCertificate": true
  }
}
EOF

# Create distribution
DISTRIBUTION_ID=$(aws cloudfront create-distribution \
  --distribution-config file:///tmp/cloudfront-config.json \
  --query 'Distribution.Id' \
  --output text)

echo "✅ CloudFront distribution created: $DISTRIBUTION_ID"
```

### Step 6: Generate Signed URLs in Backend

```javascript
// backend/services/s3.service.js

const AWS = require('aws-sdk');
const cloudFront = new AWS.CloudFront.Signer(
  process.env.CLOUDFRONT_KEY_PAIR_ID,
  process.env.CLOUDFRONT_PRIVATE_KEY
);

/**
 * Generate signed CloudFront URL for payment receipt
 * @param {string} receiptKey - S3 object key
 * @param {number} expirationMinutes - URL validity in minutes
 * @returns {string} Signed CloudFront URL
 */
function generateSignedReceiptUrl(receiptKey, expirationMinutes = 60) {
  const url = `https://${process.env.CLOUDFRONT_DOMAIN}/${receiptKey}`;
  const expiration = new Date(Date.now() + expirationMinutes * 60 * 1000);

  const signedUrl = cloudFront.getSignedUrl({
    url: url,
    expires: Math.floor(expiration.getTime() / 1000),
  });

  return signedUrl;
}

// Usage in payment controller
router.get('/receipts/:id', async (req, res) => {
  const payment = await Payment.findByPk(req.params.id);

  if (!payment || !payment.receipt_key) {
    return res.status(404).json({ error: 'Receipt not found' });
  }

  // Generate signed URL (valid for 1 hour)
  const signedUrl = generateSignedReceiptUrl(payment.receipt_key, 60);

  res.json({
    receipt_url: signedUrl,
    expires_at: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
  });
});

module.exports = { generateSignedReceiptUrl };
```

### Step 7: Update Backend Upload Logic

```javascript
// backend/services/aws.service.js

const AWS = require('aws-sdk');
const s3 = new AWS.S3();

/**
 * Upload payment receipt to S3 (encrypted, private)
 */
async function uploadReceipt(fileBuffer, fileName, metadata) {
  const params = {
    Bucket: 'securebank-payment-receipts',
    Key: `receipts/${Date.now()}-${fileName}`,
    Body: fileBuffer,
    ContentType: 'application/pdf',
    ServerSideEncryption: 'aws:kms',  // ✅ Enforce KMS encryption
    SSEKMSKeyId: process.env.KMS_KEY_ID,
    ACL: 'private',  // ✅ Explicitly private
    Metadata: metadata,
  };

  const result = await s3.upload(params).promise();
  return result.Key;  // Return S3 key for database storage
}

module.exports = { uploadReceipt };
```

### Step 8: Update Terraform Configuration

```hcl
# infrastructure/terraform/s3.tf

resource "aws_s3_bucket" "payment_receipts" {
  bucket = "securebank-payment-receipts"

  tags = {
    Name        = "securebank-payment-receipts"
    Environment = "production"
    Compliance  = "PCI-DSS"
  }
}

# Block ALL public access ✅
resource "aws_s3_bucket_public_access_block" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Server-side encryption ✅
resource "aws_s3_bucket_server_side_encryption_configuration" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.arn
    }
  }
}

# Versioning for compliance ✅
resource "aws_s3_bucket_versioning" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Lifecycle policy ✅
resource "aws_s3_bucket_lifecycle_configuration" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  rule {
    id     = "delete-old-receipts"
    status = "Enabled"

    expiration {
      days = 2555  # 7 years (PCI-DSS requirement)
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}

# Access logging ✅
resource "aws_s3_bucket_logging" "payment_receipts" {
  bucket = aws_s3_bucket.payment_receipts.id

  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access-logs/"
}
```

## Validation

### Test Public Access is Blocked

```bash
# Try to access object without authentication (should fail)
curl -I https://securebank-payment-receipts.s3.amazonaws.com/receipts/test.pdf

# Expected: 403 Forbidden
```

### Test Signed URL Access

```bash
# Generate signed URL from backend
SIGNED_URL=$(curl -s http://localhost:5000/api/receipts/1 | jq -r '.receipt_url')

# Access via signed URL (should succeed)
curl -I "$SIGNED_URL"

# Expected: 200 OK
```

### Run Compliance Scan

```bash
# Check S3 public access with Checkov
checkov -d infrastructure/terraform/ --check CKV_AWS_20,CKV_AWS_21

# Expected: PASSED for both checks
```

## Rollback Plan

```bash
# If issues occur, temporarily allow public access (NOT RECOMMENDED)
aws s3api delete-public-access-block \
  --bucket securebank-payment-receipts \
  --region us-east-1

# Restore previous bucket policy
aws s3api put-bucket-policy \
  --bucket securebank-payment-receipts \
  --policy file://backup-bucket-policy.json \
  --region us-east-1
```

## Estimated Time

- **Total Duration:** 2 hours
- **Downtime:** 0 minutes (seamless migration)
- **Best performed:** During business hours (to test signed URLs immediately)

## Cost Impact

- **CloudFront:** $0.085/GB + $0.01/10,000 requests
- **Data Transfer:** Reduced (CloudFront edge caching)
- **Total:** ~$10-50/month (depending on traffic)

## Compliance Impact

**Before:**
- ❌ PCI-DSS 1.2.1 - FAIL
- ❌ SOC2 CC6.6 - FAIL
- ❌ CIS 2.1.1 - FAIL

**After:**
- ✅ PCI-DSS 1.2.1 - PASS
- ✅ SOC2 CC6.6 - PASS
- ✅ CIS 2.1.1 - PASS

## References

- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [CloudFront Signed URLs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-signed-urls.html)
- [PCI-DSS Requirement 1.2.1](https://www.pcisecuritystandards.org/)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-08
**Severity:** CRITICAL
**Estimated Effort:** 2 hours
