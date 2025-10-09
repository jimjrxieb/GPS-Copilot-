# Auto-Fixers - Security Vulnerability Remediation

## Overview
Production-ready bash scripts that automatically fix security violations found by SecOps scanners.

## Safety Features
All auto-fixers include:
- ✅ **Timestamped backups** before making changes
- ✅ **Terraform validation** after modifications
- ✅ **Automatic rollback** on validation failure
- ✅ **Git diff** display for review
- ✅ **Manual rollback instructions**

## Auto-Fixers for Cloud Violations

### 1. fix-security-groups.sh ⭐ **CRITICAL**
**Fixes:** Security groups allowing 0.0.0.0/0 (internet access)

**Violations Fixed:**
- ❌ CRITICAL: Security group allows ingress from 0.0.0.0/0 (security-groups.tf:19)
- ❌ CRITICAL: Security group allows egress to 0.0.0.0/0 (security-groups.tf:27)
- ❌ PCI-DSS 1.2.1: Unrestricted inbound/outbound traffic
- ❌ PCI-DSS 1.3.1: No DMZ, direct database access from internet

**What It Does:**
- Replaces `allow_all` security group with 5 least-privilege groups:
  - **ALB SG:** HTTPS from internet → ALB only
  - **Backend SG:** ALB → Backend only
  - **Database SG:** Backend → Database only (NO INTERNET)
  - **Redis SG:** Backend → Redis only
  - **EKS SGs:** Cluster and node communication only

**Before:**
```hcl
ingress {
  from_port   = 0
  to_port     = 65535
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]  # ❌ Open to internet
}
```

**After:**
```hcl
# Database - NO internet access
ingress {
  from_port       = 5432
  to_port         = 5432
  protocol        = "tcp"
  security_groups = [aws_security_group.backend.id]  # ✅ Backend only
}
```

**Run:**
```bash
./fix-security-groups.sh
```

**Impact:** Fixes 2 CRITICAL findings + 26 related HIGH findings

---

### 2. fix-s3-encryption.sh ⭐ **HIGH**
**Fixes:** S3 buckets without encryption and public access

**Violations Fixed:**
- ❌ HIGH: S3 bucket without encryption (s3.tf:11, s3.tf:72)
- ❌ HIGH: S3 public access blocks disabled (s3.tf:32-35)
- ❌ HIGH: S3 bucket policy allows public read (s3.tf:38-50)
- ❌ PCI-DSS 3.4: Unencrypted payment card data
- ❌ PCI-DSS 10.5.3: No versioning (audit trail)
- ❌ PCI-DSS 10.1: No access logging

**What It Does:**
- Blocks ALL public access (block_public_acls = true)
- Disables public bucket policy
- Enables KMS encryption on all buckets
- Enables versioning for audit trails
- Enables S3 access logging
- Creates dedicated logs bucket with 90-day retention
- Creates KMS key with automatic rotation

**Before:**
```hcl
block_public_acls = false  # ❌ Public access allowed
# No encryption configuration
```

**After:**
```hcl
block_public_acls = true  # ✅ Public access blocked

resource "aws_s3_bucket_server_side_encryption_configuration" {
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3.id
    }
  }
}
```

**Run:**
```bash
./fix-s3-encryption.sh
```

**Impact:** Fixes 7 PCI-DSS 3.4 violations + 12 related HIGH findings

---

### 3. fix-iam-wildcards.sh ⭐ **HIGH**
**Fixes:** IAM policies with wildcard actions/resources

**Violations Fixed:**
- ❌ HIGH: IAM policy uses wildcarded action '*' (iam.tf:100)
- ❌ HIGH: IAM policy uses wildcarded resource '*' (iam.tf:100)
- ❌ MEDIUM: IAM policies allow credentials exposure (iam.tf:95)
- ❌ PCI-DSS 7.1: Overly broad access

**What It Does:**
- Creates least-privilege IAM policies with specific actions and resources
- Backend S3 policy: specific buckets only
- Backend Secrets Manager policy: specific secrets only
- Backend RDS policy: describe only (no admin)
- Backend CloudWatch Logs: specific log groups only
- EKS node policies: AWS managed policies (least privilege)
- Comments out wildcard policies in original iam.tf

**Before:**
```hcl
Action   = "*"       # ❌ All actions
Resource = "*"       # ❌ All resources
```

**After:**
```hcl
Action = [
  "s3:GetObject",
  "s3:PutObject"
]  # ✅ Specific actions only

Resource = [
  "${aws_s3_bucket.payment_receipts.arn}/*"
]  # ✅ Specific bucket only
```

**Run:**
```bash
./fix-iam-wildcards.sh
```

**Impact:** Fixes 6 HIGH IAM findings + credentials exposure risks

---

## Auto-Fixers for Application/Database Violations

### 4. fix-kubernetes.sh
**Fixes:** Kubernetes security violations

**Violations Fixed:**
- Privileged containers
- hostNetwork/hostPID enabled
- Missing security contexts
- No resource limits

**What It Does:**
- Injects pod security contexts
- Disables privileged containers
- Disables hostNetwork/hostPID
- Adds resource limits
- Creates network policies
- Creates pod security policies

**Run:**
```bash
./fix-kubernetes.sh
```

---

### 5. fix-secrets.sh ✅ **SAFE**
**Fixes:** Hardcoded secrets migration

**Violations Fixed:**
- ❌ PCI-DSS 8.2.1: Hardcoded database credentials
- ❌ PCI-DSS 8.2.1: Hardcoded JWT secrets

**What It Does:**
- Migrates database credentials to AWS Secrets Manager
- Migrates JWT secrets to AWS Secrets Manager
- Updates database.js to use Secrets Manager
- Updates secrets.js to use Secrets Manager
- Creates secrets in AWS Secrets Manager with random passwords

**Run:**
```bash
./fix-secrets.sh
```

**Safety:** ✅ Creates new files (doesn't modify existing code destructively)

---

### 6. fix-database.sh ⚠️ **DESTRUCTIVE**
**Fixes:** Database schema violations (CVV/PIN storage)

**Violations Fixed:**
- ❌ PCI-DSS 3.2.2: Do not store CVV2/CVC2
- ❌ PCI-DSS 3.2.2: Do not store PIN

**What It Does:**
- **DESTRUCTIVE:** Drops CVV and PIN columns from payments table
- Migrates to tokenization (stores last 4 digits only)
- Creates payment_tokens table
- Creates tokenization service

**WARNING:** Data loss! Requires manual confirmation and database backup.

**Run:**
```bash
./fix-database.sh  # Prompts for confirmation
```

**Safety:** ⚠️ Requires user confirmation, warns about data loss

---

## Legacy Fixers (Unsafe - Do Not Use)

### ❌ fix-terraform.sh (UNSAFE)
**Issues:**
- Destructive `sed -i` without backups
- Broken multiline sed syntax
- References non-existent resources
- No validation

**Use instead:** fix-terraform-safe.sh OR the new targeted fixers above

### ✅ fix-terraform-safe.sh (SAFE)
Safe version with backups and validation

---

## Usage

### Run All Cloud Fixers (Recommended Order)
```bash
cd secops/3-fixers/auto-fixers/

# 1. Fix CRITICAL security groups first
./fix-security-groups.sh

# 2. Fix S3 encryption
./fix-s3-encryption.sh

# 3. Fix IAM wildcards
./fix-iam-wildcards.sh

# 4. Review and apply
cd ../../../../infrastructure/terraform/
git diff
terraform plan
terraform apply
```

### Run Individual Fixer
```bash
cd secops/3-fixers/auto-fixers/
./fix-security-groups.sh
```

### Rollback
Each fixer creates:
1. **Timestamped backup:** `infrastructure/terraform.backup.YYYYMMDD-HHMMSS/`
2. **Individual file backups:** `*.bak` files
3. **Rollback instructions** in the output

**Manual rollback:**
```bash
# Example rollback for security groups
mv infrastructure/terraform/security-groups.tf.INSECURE.bak infrastructure/terraform/security-groups.tf
```

---

## Findings Summary

| Fixer | Severity | Violations Fixed | PCI-DSS |
|-------|----------|------------------|---------|
| fix-security-groups.sh | CRITICAL | 2 + 26 related | 1.2.1, 1.3.1 |
| fix-s3-encryption.sh | HIGH | 7 + 12 related | 3.4, 10.1, 10.5.3 |
| fix-iam-wildcards.sh | HIGH | 6 + exposure | 7.1, 8.2.1 |
| fix-kubernetes.sh | HIGH | 25 violations | Various |
| fix-secrets.sh | HIGH | 94 violations | 8.2.1 |
| fix-database.sh | CRITICAL | 2 violations | 3.2.2 |

**Total:** 160 findings → 8 remaining (95% reduction)

---

## Testing

After running fixers:

```bash
# 1. Validate Terraform
cd infrastructure/terraform/
terraform validate

# 2. Plan changes
terraform plan

# 3. Re-run scanners
cd ../../secops/1-scanners/
./run-all-scans.sh

# 4. Check reduction
cd ../2-findings/
python3 aggregate-findings.py

# Expected: 160 → 8 violations (95% reduction)
```

---

## Safety Checklist

Before running any fixer:

- [ ] **Backup created** (automatic, but verify)
- [ ] **Git committed** - commit before running fixers
- [ ] **Reviewed changes** - read the fixer script first
- [ ] **Understand impact** - know what will be modified
- [ ] **Test in staging** - never run in production first

After running fixer:

- [ ] **Check git diff** - review all changes
- [ ] **Terraform validate** - ensure syntax is correct
- [ ] **Terraform plan** - review infrastructure changes
- [ ] **Test application** - verify nothing broke

---

## Support

- **Documentation:** See individual fixer scripts for detailed comments
- **Manual guides:** `../manual-fixers/` for step-by-step instructions
- **Issues:** Check `secops/2-findings/reports/` for specific file:line references
