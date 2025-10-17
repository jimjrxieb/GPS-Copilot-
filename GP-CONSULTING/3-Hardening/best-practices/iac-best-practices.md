# Infrastructure as Code (IaC) Best Practices

**Applies to:** Terraform, CloudFormation, Pulumi, CDK

---

## Critical Rules (Must Follow)

### 1. State Management ✅

**Terraform:**
```hcl
# backend.tf - ALWAYS use remote state
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "projects/${var.project_name}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true                    # ✅ REQUIRED
    dynamodb_table = "terraform-state-lock"  # ✅ Prevents concurrent modifications
    kms_key_id     = "arn:aws:kms:..."      # ✅ Encryption at rest
  }
}
```

**Why:**
- Prevents state conflicts in team environments
- Enables state locking
- Encrypted at rest (compliance requirement)

**CloudFormation:**
```yaml
# Use StackSets for multi-account deployments
# Enable termination protection
Resources:
  MyStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://s3.amazonaws.com/${TemplateBucket}/stack.yaml'
      Parameters:
        Environment: !Ref Environment
```

---

### 2. Never Hardcode Secrets ❌

**WRONG:**
```hcl
resource "aws_db_instance" "main" {
  username = "admin"                    # ❌ DON'T
  password = "SuperSecret123!"          # ❌ NEVER DO THIS
}
```

**CORRECT:**
```hcl
# Option 1: Use Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "rds-master-password"
}

resource "aws_db_instance" "main" {
  username = var.db_username            # ✅ From tfvars
  password = data.aws_secretsmanager_secret_version.db_password.secret_string  # ✅ From Secrets Manager
}

# Option 2: Use environment variables
# TF_VAR_db_password=... terraform apply
```

**Validate:**
```bash
# Scan for hardcoded secrets BEFORE committing
cd ../../1-Security-Assessment/ci-scanners/
./scan-secrets.py /path/to/terraform
```

---

### 3. Use Modules (DRY Principle) ✅

**WRONG:**
```hcl
# Duplicating VPC code in every project ❌
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  # 50 lines of VPC config...
}
```

**CORRECT:**
```hcl
# Use reusable modules ✅
module "vpc" {
  source  = "../../4-Cloud-Migration/terraform-modules/secure-vpc"
  version = "1.2.0"

  project_name = var.project_name
  environment  = var.environment
  cidr_block   = var.vpc_cidr
}
```

**Benefits:**
- Consistency across projects
- Easier updates (update module once)
- Enforces security best practices

---

### 4. Resource Tagging (Required) ✅

**ALWAYS tag:**
```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.team_email
    CostCenter  = var.cost_center
    Compliance  = "PCI-DSS"              # For compliance tracking
    DataClass   = "Confidential"          # For data classification
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "${var.project_name}-data"
  tags   = merge(local.common_tags, {
    Purpose = "Application data storage"
  })
}
```

**Why:**
- Cost allocation
- Compliance audits
- Resource ownership
- Automated cleanup

---

### 5. Environment Separation ✅

**Use workspaces or separate state files:**

```bash
# Option 1: Terraform workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new production

terraform workspace select production
terraform apply  # Only affects production
```

```hcl
# Use workspace in resource names
locals {
  environment = terraform.workspace
  name_prefix = "${var.project_name}-${local.environment}"
}

resource "aws_instance" "app" {
  instance_type = local.environment == "production" ? "m5.xlarge" : "t3.medium"
  tags = {
    Name = "${local.name_prefix}-app"
  }
}
```

**Option 2: Separate directories:**
```
terraform/
├── environments/
│   ├── dev/
│   │   ├── backend.tf       # Points to dev state
│   │   ├── terraform.tfvars
│   │   └── main.tf
│   ├── staging/
│   └── production/
└── modules/
```

---

### 6. Always Run `terraform plan` ✅

**NEVER skip planning:**
```bash
# WRONG ❌
terraform apply -auto-approve  # Dangerous!

# CORRECT ✅
terraform plan -out=tfplan
terraform show -json tfplan | jq  # Review changes

# Validate with OPA policies
conftest test tfplan.json --policy ../../3-Hardening/policies/opa/

# If approved, apply
terraform apply tfplan
```

**In CI/CD:**
```yaml
# GitHub Actions example
- name: Terraform Plan
  run: terraform plan -out=tfplan

- name: Validate with OPA
  run: conftest test tfplan --policy policies/

- name: Require manual approval
  uses: actions/github-script@v7
  # Wait for human review before apply
```

---

### 7. Immutable Infrastructure ✅

**Prefer `create_before_destroy`:**
```hcl
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true  # ✅ Creates new, then destroys old
  }
}
```

**Why:**
- Zero-downtime deployments
- Easy rollback (old resource still exists temporarily)
- Safer than in-place updates

---

### 8. Pin Versions ✅

**ALWAYS pin provider and module versions:**
```hcl
terraform {
  required_version = ">= 1.5.0"  # ✅ Specific Terraform version

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"          # ✅ Pin to major version
    }
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.2"               # ✅ Exact version (most secure)
}
```

**Why:**
- Prevents breaking changes
- Reproducible deployments
- Security (avoid supply chain attacks)

---

### 9. Enable Encryption Everywhere ✅

**S3:**
```hcl
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"     # ✅ Use KMS (not AES256)
      kms_master_key_id = aws_kms_key.s3.arn
    }
    bucket_key_enabled = true           # ✅ Reduces KMS costs
  }
}
```

**RDS:**
```hcl
resource "aws_db_instance" "main" {
  engine               = "postgres"
  storage_encrypted    = true           # ✅ REQUIRED
  kms_key_id          = aws_kms_key.rds.arn

  # Also encrypt backups
  backup_retention_period = 7
  # Backups automatically encrypted if storage_encrypted = true
}
```

**EBS:**
```hcl
resource "aws_ebs_volume" "data" {
  availability_zone = "us-east-1a"
  size              = 100
  encrypted         = true              # ✅ REQUIRED
  kms_key_id       = aws_kms_key.ebs.arn
}
```

---

### 10. Least Privilege IAM ✅

**WRONG:**
```hcl
resource "aws_iam_policy" "app" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = "*"                    # ❌ NEVER use wildcard actions
      Resource = "*"                    # ❌ NEVER use wildcard resources
    }]
  })
}
```

**CORRECT:**
```hcl
resource "aws_iam_policy" "app" {
  policy = jsonencode({
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",               # ✅ Specific actions only
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.data.arn}/*" # ✅ Specific resource ARN
        ]
      },
      {
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.data.arn]
      }
    ]
  })
}
```

**Auto-fix:**
```bash
cd ../fixers/
./fix-iam-wildcards.sh /path/to/terraform
```

---

## Validation Workflow

**Before every deployment:**

```bash
#!/bin/bash
# pre-deploy-validation.sh

set -e

PROJECT_ROOT=$1

echo "1. Format check..."
terraform fmt -check

echo "2. Validate syntax..."
terraform validate

echo "3. Security scan..."
cd /path/to/GP-CONSULTING/1-Security-Assessment/cd-scanners/
./scan-iac.py "$PROJECT_ROOT"

echo "4. Policy validation..."
terraform plan -out=tfplan
conftest test tfplan --policy /path/to/GP-CONSULTING/3-Hardening/policies/opa/

echo "5. Check for secrets..."
cd /path/to/GP-CONSULTING/1-Security-Assessment/ci-scanners/
./scan-secrets.py "$PROJECT_ROOT"

echo "✅ All validations passed"
```

---

## Common Mistakes to Avoid

### ❌ 1. Destroying Data Accidentally
```hcl
resource "aws_s3_bucket" "critical_data" {
  bucket = "company-critical-data"

  lifecycle {
    prevent_destroy = true  # ✅ Prevents accidental deletion
  }
}
```

### ❌ 2. Not Using Data Sources
```hcl
# WRONG: Hardcoding AMI IDs ❌
resource "aws_instance" "app" {
  ami = "ami-0abcdef1234567890"  # Breaks in other regions
}

# CORRECT: Use data sources ✅
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "app" {
  ami = data.aws_ami.amazon_linux.id  # ✅ Works everywhere
}
```

### ❌ 3. No Backup/Restore Plan
```hcl
resource "aws_db_instance" "main" {
  backup_retention_period = 7           # ✅ Required: 7-35 days
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  skip_final_snapshot       = false     # ✅ Create snapshot on destroy
  final_snapshot_identifier = "${var.project_name}-final-${formatdate("YYYY-MM-DD", timestamp())}"
}
```

### ❌ 4. Not Enabling Logging
```hcl
# VPC Flow Logs ✅
resource "aws_flow_log" "main" {
  vpc_id          = aws_vpc.main.id
  traffic_type    = "ALL"
  iam_role_arn   = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
}

# S3 Access Logging ✅
resource "aws_s3_bucket_logging" "data" {
  bucket        = aws_s3_bucket.data.id
  target_bucket = aws_s3_bucket.logs.id
  target_prefix = "s3-access-logs/"
}

# RDS Logging ✅
resource "aws_db_instance" "main" {
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]  # ✅ For RDS Postgres
}
```

---

## Compliance Mappings

| Best Practice | PCI-DSS | HIPAA | CIS AWS | NIST 800-53 |
|---------------|---------|-------|---------|-------------|
| Encrypt at rest | 3.4 | §164.312(a)(2)(iv) | 2.1.1 | SC-28 |
| State encryption | 3.4 | §164.312(a)(2)(iv) | - | SC-28 |
| Least privilege IAM | 7.1, 7.2 | §164.308(a)(3) | 1.16 | AC-6 |
| No hardcoded secrets | 8.2.1 | §164.308(a)(5)(ii)(D) | - | IA-5 |
| Enable logging | 10.2, 10.3 | §164.312(b) | 3.1-3.4 | AU-2, AU-3 |
| Backup retention | 12.10 | §164.308(a)(7)(ii)(A) | - | CP-9 |

---

## Auto-Fixers

Phase 3 provides auto-fixers for common IaC issues:

```bash
cd ../fixers/

# Fix IAM wildcards
./fix-iam-wildcards.sh /path/to/terraform

# Fix missing S3 encryption
./fix-s3-encryption.sh /path/to/terraform

# Fix CloudWatch logging
./fix-cloudwatch-security.sh /path/to/terraform

# Fix network security
./fix-network-security.sh /path/to/terraform
```

---

## Pre-Deployment Checklist

See: [checklists/pre-deployment-checklist.md](checklists/pre-deployment-checklist.md)

- [ ] All secrets in Secrets Manager/Vault
- [ ] All resources tagged
- [ ] Encryption enabled everywhere
- [ ] IAM policies use least privilege
- [ ] Logging/monitoring enabled
- [ ] Backup retention configured
- [ ] `terraform plan` reviewed
- [ ] OPA policies passing
- [ ] Security scan clean
- [ ] Rollback plan documented

---

**Status:** ✅ Production-Ready
**Last Updated:** 2025-10-14
**Compliance:** PCI-DSS, HIPAA, CIS AWS, NIST 800-53
