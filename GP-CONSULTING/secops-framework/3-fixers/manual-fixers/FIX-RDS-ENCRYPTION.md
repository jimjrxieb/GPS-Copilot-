# Manual Fix Guide: RDS Encryption

## Problem

**PCI-DSS Violation:** RDS instance stores unencrypted payment data
- **Requirement:** PCI-DSS 3.4 - Render PAN unreadable (encryption at rest)
- **Risk:** High - Data breach exposure
- **Current State:** `storage_encrypted = false`

## Solution Overview

Enable RDS encryption at rest using AWS KMS. This requires creating a new encrypted instance and migrating data.

## Prerequisites

- [x] AWS CLI configured with admin access
- [x] Database backup completed
- [x] Maintenance window scheduled (30-60 minutes downtime)
- [x] KMS key created (or use AWS managed key)

## Step-by-Step Instructions

### Step 1: Create KMS Key for Encryption

```bash
# Create customer-managed KMS key
aws kms create-key \
  --description "SecureBank RDS encryption key" \
  --key-policy '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "Enable IAM User Permissions",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::ACCOUNT_ID:root"
        },
        "Action": "kms:*",
        "Resource": "*"
      },
      {
        "Sid": "Allow RDS to use the key",
        "Effect": "Allow",
        "Principal": {
          "Service": "rds.amazonaws.com"
        },
        "Action": [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:CreateGrant"
        ],
        "Resource": "*"
      }
    ]
  }' \
  --region us-east-1

# Create alias
aws kms create-alias \
  --alias-name alias/securebank-rds \
  --target-key-id <KEY_ID> \
  --region us-east-1
```

### Step 2: Create Snapshot of Existing Database

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier securebank-db \
  --db-snapshot-identifier securebank-db-pre-encryption-$(date +%Y%m%d) \
  --region us-east-1

# Wait for snapshot to complete
aws rds wait db-snapshot-completed \
  --db-snapshot-identifier securebank-db-pre-encryption-$(date +%Y%m%d) \
  --region us-east-1

echo "✅ Snapshot created successfully"
```

### Step 3: Copy Snapshot with Encryption

```bash
# Copy snapshot with encryption enabled
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier securebank-db-pre-encryption-$(date +%Y%m%d) \
  --target-db-snapshot-identifier securebank-db-encrypted-$(date +%Y%m%d) \
  --kms-key-id alias/securebank-rds \
  --region us-east-1

# Wait for encrypted snapshot
aws rds wait db-snapshot-completed \
  --db-snapshot-identifier securebank-db-encrypted-$(date +%Y%m%d) \
  --region us-east-1

echo "✅ Encrypted snapshot created"
```

### Step 4: Restore from Encrypted Snapshot

```bash
# Restore encrypted RDS instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier securebank-db-encrypted \
  --db-snapshot-identifier securebank-db-encrypted-$(date +%Y%m%d) \
  --db-instance-class db.t3.medium \
  --publicly-accessible false \
  --storage-encrypted \
  --kms-key-id alias/securebank-rds \
  --vpc-security-group-ids sg-xxxxxxxx \
  --db-subnet-group-name securebank-db-subnet-group \
  --region us-east-1

# Wait for new instance
aws rds wait db-instance-available \
  --db-instance-identifier securebank-db-encrypted \
  --region us-east-1

echo "✅ Encrypted RDS instance created"
```

### Step 5: Update Application Connection String

```bash
# Get new endpoint
NEW_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier securebank-db-encrypted \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text \
  --region us-east-1)

echo "New RDS endpoint: $NEW_ENDPOINT"

# Update Kubernetes secret
kubectl create secret generic db-credentials \
  --from-literal=host=$NEW_ENDPOINT \
  --from-literal=port=5432 \
  --from-literal=database=securebank \
  --from-literal=username=securebank_user \
  --from-literal=password='CHANGE_ME' \
  --namespace securebank \
  --dry-run=client -o yaml | kubectl apply -f -

# Or update AWS Secrets Manager
aws secretsmanager update-secret \
  --secret-id securebank/db/credentials \
  --secret-string '{
    "host": "'$NEW_ENDPOINT'",
    "port": 5432,
    "database": "securebank",
    "username": "securebank_user",
    "password": "CHANGE_ME"
  }' \
  --region us-east-1
```

### Step 6: Test Application Connectivity

```bash
# Test connection from backend pod
kubectl exec -it deployment/securebank-backend -n securebank -- \
  psql -h $NEW_ENDPOINT -U securebank_user -d securebank -c "SELECT 1;"

# Run application health check
curl -f http://localhost:5000/health

# Run integration tests
npm run test:integration
```

### Step 7: Delete Old Unencrypted Instance

```bash
# IMPORTANT: Only after verifying new instance works!

# Create final backup snapshot
aws rds create-db-snapshot \
  --db-instance-identifier securebank-db \
  --db-snapshot-identifier securebank-db-final-backup-$(date +%Y%m%d) \
  --region us-east-1

# Delete old unencrypted instance
aws rds delete-db-instance \
  --db-instance-identifier securebank-db \
  --skip-final-snapshot \
  --region us-east-1

echo "✅ Old unencrypted instance deleted"
```

### Step 8: Update Terraform Configuration

```hcl
# infrastructure/terraform/rds.tf

resource "aws_db_instance" "securebank" {
  identifier             = "securebank-db-encrypted"
  engine                 = "postgres"
  engine_version         = "14.7"
  instance_class         = "db.t3.medium"
  allocated_storage      = 100
  storage_type           = "gp3"
  storage_encrypted      = true  # ✅ FIXED
  kms_key_id            = aws_kms_key.securebank_rds.arn  # ✅ ADDED

  db_name                = "securebank"
  username               = "securebank_user"
  password               = random_password.db_password.result

  publicly_accessible    = false  # ✅ FIXED
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.securebank.name

  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  deletion_protection    = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "securebank-db-final-snapshot"

  tags = {
    Name        = "securebank-db-encrypted"
    Environment = "production"
    Compliance  = "PCI-DSS"
  }
}

resource "aws_kms_key" "securebank_rds" {
  description             = "SecureBank RDS encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "securebank-rds-kms"
  }
}

resource "aws_kms_alias" "securebank_rds" {
  name          = "alias/securebank-rds"
  target_key_id = aws_kms_key.securebank_rds.key_id
}
```

## Validation

### Verify Encryption Status

```bash
# Check encryption status
aws rds describe-db-instances \
  --db-instance-identifier securebank-db-encrypted \
  --query 'DBInstances[0].[DBInstanceIdentifier,StorageEncrypted,KmsKeyId]' \
  --output table \
  --region us-east-1

# Expected output:
# -----------------------------------------------------------
# |                   DescribeDBInstances                   |
# +--------------------------+-------+----------------------+
# |  securebank-db-encrypted |  True | arn:aws:kms:...     |
# +--------------------------+-------+----------------------+
```

### Verify PCI-DSS Compliance

```bash
# Run Checkov to verify encryption
checkov -d infrastructure/terraform/ --check CKV_AWS_16

# Expected: PASSED for CKV_AWS_16 (RDS encryption)
```

## Rollback Plan

If issues occur, rollback to the original unencrypted instance:

```bash
# Restore from pre-encryption snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier securebank-db-rollback \
  --db-snapshot-identifier securebank-db-pre-encryption-$(date +%Y%m%d) \
  --region us-east-1

# Update connection string back to original
```

## Estimated Time

- **Total Duration:** 45-60 minutes
- **Downtime:** 15-30 minutes (during connection string update)
- **Best performed:** During off-peak hours

## Cost Impact

- **KMS Key:** $1/month
- **Storage:** No additional cost (encryption is free)
- **Total:** ~$1/month additional cost

## Compliance Impact

**Before:**
- ❌ PCI-DSS 3.4 - FAIL
- ❌ SOC2 CC6.1 - FAIL
- ❌ CIS 2.3.1 - FAIL

**After:**
- ✅ PCI-DSS 3.4 - PASS
- ✅ SOC2 CC6.1 - PASS
- ✅ CIS 2.3.1 - PASS

## References

- [AWS RDS Encryption](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html)
- [PCI-DSS Requirement 3.4](https://www.pcisecuritystandards.org/)
- [AWS KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-08
**Severity:** HIGH
**Estimated Effort:** 1 hour
