# Reusable AWS Components vs. SecureBank-Specific

**Analysis of:** `/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project`
**Target:** Bare metal → LocalStack → AWS migration

---

## 🎯 Current State Analysis

### What FINANCE-project Has:
- ✅ **Docker Compose** with LocalStack already configured
- ✅ **Terraform modules** for AWS infrastructure
- ✅ **Backend API** (Node.js/Express) with AWS SDK
- ✅ **Frontend** (React)
- ✅ **Database** (PostgreSQL)
- ✅ **Redis** (session storage)
- ✅ **Vault** (secrets management - local)
- ✅ **OPA** (policy enforcement)
- ✅ **Nginx** (reverse proxy)

### Architecture:
```
SecureBank Stack:
- Backend: Node.js/Express (payment API)
- Frontend: React (dashboard)
- Database: PostgreSQL 14
- Cache: Redis 7
- Secrets: Vault (local) + AWS Secrets Manager (AWS)
- Policy: OPA
- Proxy: Nginx
- AWS Emulation: LocalStack
```

---

## 🔄 Reusable Components (Any Project)

These components can be extracted into **Phase 4 reusable migration framework**:

### 1️⃣ **LocalStack Setup** 🔄 REUSABLE

**File:** `docker-compose.yml` (lines 12-36)

```yaml
localstack:
  image: localstack/localstack:3.0.2
  container_name: ${PROJECT_NAME}-localstack
  ports:
    - "4566:4566"
  environment:
    - SERVICES=s3,secretsmanager,cloudwatch,iam,rds,ec2,eks,ecr
    - PERSISTENCE=1
  volumes:
    - "localstack_data:/var/lib/localstack"
    - "/var/run/docker.sock:/var/run/docker.sock"
```

**Reusable for:** ANY project testing AWS migration locally

**Create:**
```
4-Cloud-Migration/1-localstack/
├── docker-compose.localstack.yml    # Standalone LocalStack config
├── setup-localstack.sh               # Start LocalStack
├── configure-aws-cli.sh              # Set up awslocal
└── test-services.sh                  # Verify S3, RDS, Secrets Manager
```

---

### 2️⃣ **Terraform Modules** 🔄 REUSABLE

**Files:** `infrastructure/terraform/*.tf`

These are **almost entirely reusable** with just variables changed:

#### A. **VPC Module** 🔄 REUSABLE
**File:** `vpc.tf` (4.4 KB)

**What's reusable:**
- VPC with public/private subnets
- NAT Gateway
- Internet Gateway
- Route tables
- VPC Flow Logs

**What's SecureBank-specific:**
- ❌ None! Entirely reusable

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-vpc/
├── main.tf
├── variables.tf
├── outputs.tf
└── README.md
```

**Variables to parameterize:**
- `vpc_cidr` (default: 10.0.0.0/16)
- `project_name`
- `environment`
- `enable_flow_logs` (default: true)

---

#### B. **S3 Module** 🔄 REUSABLE (with caution)
**File:** `s3.tf` (6.3 KB)

**What's reusable:**
- ✅ S3 bucket with encryption (KMS)
- ✅ Versioning enabled
- ✅ Access logging
- ✅ Lifecycle policies
- ✅ Public access block

**What's SecureBank-specific:**
- ⚠️ **Bucket name:** `payment-receipts` (business logic)
- ⚠️ **Lifecycle rules:** 90-day Glacier transition (PCI-DSS specific)
- ⚠️ **Tags:** "Contains: Payment Data"

**How to make reusable:**
```hcl
# Reusable module
module "secure_s3" {
  source = "../../GP-CONSULTING/4-Cloud-Migration/3-terraform-modules/secure-s3"

  bucket_name      = "payment-receipts"       # Variable
  purpose          = "Payment receipts"       # Variable
  contains_pii     = true                     # Variable
  lifecycle_days   = 90                       # Variable
  kms_key_id       = aws_kms_key.main.arn
}
```

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-s3/
├── main.tf                      # Bucket + encryption + versioning
├── variables.tf                 # Parameterized inputs
├── outputs.tf                   # Bucket ARN, ID, etc.
└── README.md                    # Usage examples
```

---

#### C. **RDS Module** 🔄 REUSABLE
**File:** `rds.tf` (3.5 KB)

**What's reusable:**
- ✅ RDS instance with encryption (KMS)
- ✅ SSL/TLS enforcement
- ✅ Automated backups (7-30 days)
- ✅ Multi-AZ (optional)
- ✅ Query logging enabled
- ✅ Enhanced monitoring

**What's SecureBank-specific:**
- ⚠️ **Database name:** `payment_db` (business logic)
- ⚠️ **Instance class:** `db.t3.micro` (size depends on workload)
- ⚠️ **Backup retention:** 30 days (PCI-DSS requires 30 days for payment data)

**How to make reusable:**
```hcl
module "secure_rds" {
  source = "../../GP-CONSULTING/4-Cloud-Migration/3-terraform-modules/secure-rds"

  identifier           = "payment-db"         # Variable
  engine               = "postgres"           # Variable
  engine_version       = "14.10"              # Variable
  instance_class       = "db.t3.micro"        # Variable
  allocated_storage    = 20                   # Variable
  backup_retention_days = 30                  # Variable (7-35)
  kms_key_id           = aws_kms_key.main.arn
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name = aws_db_subnet_group.main.name
}
```

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-rds/
├── main.tf                      # RDS instance + encryption + backups
├── variables.tf                 # Parameterized (engine, size, retention)
├── outputs.tf                   # Endpoint, port, ARN
└── README.md                    # Usage examples
```

---

#### D. **Secrets Manager Module** 🔄 REUSABLE
**File:** `secrets-manager.tf` (2.5 KB)

**What's reusable:**
- ✅ Secrets Manager secret with KMS encryption
- ✅ Automatic rotation (optional)
- ✅ Recovery window

**What's SecureBank-specific:**
- ⚠️ **Secret names:** `db-password`, `jwt-secret`, `admin-credentials` (app-specific)
- ⚠️ **Rotation lambda:** For database passwords (app-specific)

**How to make reusable:**
```hcl
module "secure_secret" {
  source = "../../GP-CONSULTING/4-Cloud-Migration/3-terraform-modules/secure-secrets-manager"

  secret_name       = "db-password"           # Variable
  description       = "RDS master password"   # Variable
  recovery_days     = 7                       # Variable
  enable_rotation   = true                    # Variable
  rotation_days     = 30                      # Variable
  kms_key_id        = aws_kms_key.main.arn
}
```

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-secrets-manager/
├── main.tf                      # Secret + KMS + rotation
├── variables.tf                 # Parameterized
├── outputs.tf                   # Secret ARN, name
└── rotation-lambda.py           # Generic rotation lambda (optional)
```

---

#### E. **KMS Module** 🔄 REUSABLE
**File:** `kms.tf` (2.9 KB)

**What's reusable:**
- ✅ KMS key with automatic rotation
- ✅ Key policy (least privilege)
- ✅ Key alias

**What's SecureBank-specific:**
- ❌ None! Entirely reusable

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-kms/
├── main.tf                      # KMS key + rotation + policy
├── variables.tf                 # Key description, alias
├── outputs.tf                   # Key ID, ARN
└── README.md                    # Usage
```

---

#### F. **IAM Module** 🔄 REUSABLE (with caution)
**Files:** `iam.tf`, `iam-least-privilege.tf` (10 KB total)

**What's reusable:**
- ✅ IAM role structure
- ✅ AssumeRole policy
- ✅ Least privilege approach

**What's SecureBank-specific:**
- ⚠️ **Role purposes:** `payment-api-role`, `admin-role` (app-specific)
- ⚠️ **Permissions:** S3 access to `payment-receipts/*` (app-specific)
- ⚠️ **Services:** RDS, Secrets Manager, S3 (depends on app architecture)

**How to make reusable:**
```hcl
module "api_role" {
  source = "../../GP-CONSULTING/4-Cloud-Migration/3-terraform-modules/secure-iam"

  role_name        = "payment-api-role"       # Variable
  trusted_service  = "ec2.amazonaws.com"      # Variable (EC2, ECS, Lambda, etc.)
  s3_buckets       = ["payment-receipts"]     # Variable (list)
  rds_databases    = ["payment-db"]           # Variable (list)
  secrets          = ["db-password", "jwt-secret"]  # Variable (list)
}
```

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-iam/
├── main.tf                      # IAM role + policies
├── variables.tf                 # Parameterized resources
├── outputs.tf                   # Role ARN, name
└── least-privilege-templates.json  # Policy templates
```

---

#### G. **Security Groups Module** 🔄 REUSABLE (with caution)
**File:** `security-groups.tf` (8.7 KB)

**What's reusable:**
- ✅ Security group structure
- ✅ Least privilege rules

**What's SecureBank-specific:**
- ⚠️ **Ports:** 3000 (API), 5432 (PostgreSQL), 6379 (Redis) (app-specific)
- ⚠️ **Ingress sources:** Depends on architecture

**How to make reusable:**
```hcl
module "api_sg" {
  source = "../../GP-CONSULTING/4-Cloud-Migration/3-terraform-modules/secure-sg"

  sg_name         = "api-sg"
  vpc_id          = aws_vpc.main.id
  ingress_rules   = [
    { port = 3000, cidr = "10.0.0.0/16" },  # Variable
    { port = 443, cidr = "0.0.0.0/0" }
  ]
}
```

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-sg/
├── main.tf                      # Security group + rules
├── variables.tf                 # Parameterized ports, CIDRs
├── outputs.tf                   # SG ID
└── README.md                    # Usage
```

---

#### H. **CloudWatch Module** 🔄 REUSABLE
**File:** `cloudwatch.tf` (737 bytes)

**What's reusable:**
- ✅ CloudWatch log groups
- ✅ Log retention policies
- ✅ CloudWatch alarms (CPU, memory, disk)

**What's SecureBank-specific:**
- ⚠️ **Log group names:** `/aws/rds/payment-db` (app-specific)
- ⚠️ **Alarm thresholds:** Depends on workload

**Extract to:**
```
4-Cloud-Migration/3-terraform-modules/secure-cloudwatch/
├── main.tf                      # Log groups + alarms
├── variables.tf                 # Parameterized thresholds
├── outputs.tf                   # Log group ARNs
└── README.md                    # Usage
```

---

### 3️⃣ **AWS CLI Scripts** 🔄 REUSABLE

**Currently:** SecureBank uses Terraform, but you want AWS CLI scripts too

**Create reusable scripts:**

```bash
4-Cloud-Migration/2-aws-cli-scripts/

s3/
├── create-bucket.sh             # 🔄 REUSABLE
│   awslocal s3 mb s3://BUCKET_NAME
│   awslocal s3api put-bucket-encryption --bucket BUCKET_NAME --kms-key KMS_ARN
│   awslocal s3api put-bucket-versioning --bucket BUCKET_NAME --enabled
│
├── set-bucket-policy.sh         # 🔄 REUSABLE (template)
│   awslocal s3api put-bucket-policy --bucket BUCKET_NAME --policy file://policy.json
│
└── sync-files.sh                # 🔄 REUSABLE
    awslocal s3 sync /local/path s3://BUCKET_NAME/

secrets-manager/
├── create-secret.sh             # 🔄 REUSABLE
│   awslocal secretsmanager create-secret --name SECRET_NAME --kms-key KMS_ARN
│
├── migrate-from-vault.sh        # 🔄 REUSABLE
│   # Extract from Vault
│   vault kv get -format=json secret/db-password
│   # Upload to Secrets Manager
│   awslocal secretsmanager create-secret --name db-password --secret-string "$VALUE"
│
└── rotate-secret.sh             # ⚠️ App-specific (needs rotation lambda)

rds/
├── create-db.sh                 # 🔄 REUSABLE (parameterized)
│   awslocal rds create-db-instance \
│     --db-instance-identifier DB_NAME \
│     --engine postgres \
│     --master-username admin \
│     --master-password "$DB_PASSWORD" \
│     --storage-encrypted
│
└── test-connection.sh           # 🔄 REUSABLE
    psql -h ENDPOINT -U admin -d DB_NAME

kms/
├── create-key.sh                # 🔄 REUSABLE
│   awslocal kms create-key --description "Encryption key for PROJECT_NAME"
│
└── create-alias.sh              # 🔄 REUSABLE
    awslocal kms create-alias --alias-name alias/PROJECT_NAME --target-key-id KEY_ID
```

**Variables to parameterize:**
- `PROJECT_NAME`
- `BUCKET_NAME`
- `SECRET_NAME`
- `DB_NAME`
- `KMS_KEY_ID`

---

### 4️⃣ **Migration Scripts** 🔄 REUSABLE (framework)

**Create generic migration framework:**

```bash
4-Cloud-Migration/4-migration-scripts/

1-pre-migration/
├── assess-current-state.sh      # 🔄 REUSABLE
│   # Inventory running services
│   docker ps -a > services.txt
│   docker images > images.txt
│   df -h > disk-usage.txt
│
├── dependency-mapper.py         # 🔄 REUSABLE
│   # Parse docker-compose.yml
│   # Extract service dependencies (db → api → frontend)
│   # Generate dependency graph
│
└── data-volume-calculator.sh   # 🔄 REUSABLE
    # Calculate database size
    # Calculate file storage size
    # Estimate migration time

2-data-migration/
├── database-migration.sh        # 🔄 REUSABLE (parameterized)
│   #!/bin/bash
│   # Export from local PostgreSQL
│   pg_dump -h localhost -U $DB_USER -d $DB_NAME > dump.sql
│
│   # Import to RDS
│   psql -h $RDS_ENDPOINT -U $DB_USER -d $DB_NAME < dump.sql
│
├── file-migration.sh            # 🔄 REUSABLE
│   # Sync files to S3
│   awslocal s3 sync /local/files s3://BUCKET_NAME/
│
│   # Verify checksums
│   md5sum /local/files/* > checksums.txt
│   awslocal s3 cp checksums.txt s3://BUCKET_NAME/
│
└── secrets-migration.sh         # 🔄 REUSABLE
    # Extract from Vault
    vault kv list secret/ | while read secret; do
      VALUE=$(vault kv get -field=value secret/$secret)
      awslocal secretsmanager create-secret --name $secret --secret-string "$VALUE"
    done

3-cutover/
├── cutover-plan.sh              # 🔄 REUSABLE (template)
│   # 1. Stop local services
│   docker-compose down
│
│   # 2. Final data sync
│   ./database-migration.sh
│   ./file-migration.sh
│
│   # 3. Update DNS (if applicable)
│   # 4. Start AWS services
│   # 5. Smoke tests
│
└── rollback-plan.sh             # 🔄 REUSABLE (template)
    # 1. Stop AWS services
    # 2. Revert DNS
    # 3. Start local services
    docker-compose up -d
```

---

### 5️⃣ **Validation Scripts** 🔄 REUSABLE

```bash
4-Cloud-Migration/5-validation/

├── api-tests.sh                 # ⚠️ App-specific endpoints
│   # Test API endpoints
│   curl http://localhost:3000/api/health
│   curl http://localhost:3000/api/merchants
│
├── database-tests.sh            # 🔄 REUSABLE (parameterized queries)
│   # Verify data migrated
│   COUNT_LOCAL=$(psql -h localhost -U postgres -d securebank -t -c "SELECT COUNT(*) FROM payments")
│   COUNT_AWS=$(psql -h $RDS_ENDPOINT -U admin -d securebank -t -c "SELECT COUNT(*) FROM payments")
│
│   if [ "$COUNT_LOCAL" -eq "$COUNT_AWS" ]; then
│     echo "✅ Data migrated successfully"
│   fi
│
└── performance-tests.sh         # 🔄 REUSABLE
    # Load testing with wrk/ab
    ab -n 1000 -c 10 http://localhost:3000/api/health
```

---

## 🏦 SecureBank-Specific Components

These are **tailored to FINANCE-project** and NOT reusable:

### 1. **Business Logic** 🏦 SECUREBANK-SPECIFIC

**Files:**
- `backend/controllers/payment.controller.js` - Payment processing logic
- `backend/controllers/merchant.controller.js` - Merchant management
- `backend/models/Payment.js` - Payment data model
- `backend/models/Merchant.js` - Merchant data model

**Why not reusable:**
- Payment processing is specific to SecureBank's business
- PCI-DSS compliance requirements (CVV/PIN handling)
- Merchant onboarding workflows

---

### 2. **PCI-DSS Compliance Requirements** 🏦 SECUREBANK-SPECIFIC

**Examples from Terraform:**
- ⚠️ **RDS backup retention:** 30 days (PCI-DSS 10.7)
- ⚠️ **S3 lifecycle:** 90-day Glacier transition (PCI-DSS 3.1)
- ⚠️ **CloudWatch logging:** All queries logged (PCI-DSS 10.1)
- ⚠️ **Encryption:** KMS for all data at rest (PCI-DSS 3.4)

**Why not reusable:**
- Other projects may not need PCI-DSS compliance
- Non-payment apps don't need 30-day backups
- Logging requirements vary by industry (HIPAA vs PCI-DSS)

**How to handle:**
```hcl
# Reusable module with compliance defaults
module "secure_rds" {
  source = "../../GP-CONSULTING/4-Cloud-Migration/3-terraform-modules/secure-rds"

  # Generic defaults
  backup_retention_days = var.compliance == "pci-dss" ? 30 : 7  # PCI-DSS requires 30

  # Variable
  enable_query_logging = var.compliance == "pci-dss" ? true : false
}
```

---

### 3. **API Endpoints** 🏦 SECUREBANK-SPECIFIC

**Routes:**
- `/api/payments` - Create/process payments
- `/api/merchants` - Manage merchants
- `/api/auth` - Authentication (JWT)

**Why not reusable:**
- Specific to SecureBank's payment platform
- Other apps have different endpoints (e.g., `/api/users`, `/api/products`)

---

### 4. **Frontend UI** 🏦 SECUREBANK-SPECIFIC

**Files:**
- `frontend/src/pages/Dashboard.tsx` - Payment dashboard
- `frontend/src/pages/Merchants.tsx` - Merchant management
- `frontend/src/components/PaymentForm.tsx` - Payment form

**Why not reusable:**
- UI specific to SecureBank branding
- Payment workflows specific to financial apps

---

### 5. **Database Schema** 🏦 SECUREBANK-SPECIFIC

**Tables:**
- `payments` - Payment transactions (CVV, PIN, card data)
- `merchants` - Merchant accounts
- `users` - Admin users

**Why not reusable:**
- Schema specific to payment processing
- Other apps have different data models

---

## 📊 Summary: Reusable vs. SecureBank-Specific

| Component | Reusable? | Notes |
|-----------|-----------|-------|
| **LocalStack setup** | ✅ 100% | Any project can use |
| **Terraform: VPC** | ✅ 100% | Fully parameterized |
| **Terraform: S3** | ✅ 90% | Just change bucket name, lifecycle rules |
| **Terraform: RDS** | ✅ 90% | Just change instance size, retention |
| **Terraform: KMS** | ✅ 100% | Fully reusable |
| **Terraform: Secrets Manager** | ✅ 95% | Just change secret names |
| **Terraform: IAM** | ✅ 70% | Need to customize permissions per app |
| **Terraform: Security Groups** | ✅ 60% | Ports/rules vary by app |
| **Terraform: CloudWatch** | ✅ 90% | Just change log group names |
| **AWS CLI: S3 scripts** | ✅ 100% | Parameterize bucket name |
| **AWS CLI: Secrets Manager** | ✅ 100% | Parameterize secret name |
| **AWS CLI: RDS scripts** | ✅ 100% | Parameterize DB name |
| **Migration: Database** | ✅ 95% | Works for any PostgreSQL/MySQL |
| **Migration: Files** | ✅ 100% | S3 sync is generic |
| **Migration: Secrets** | ✅ 100% | Vault → Secrets Manager (generic) |
| **Migration: Cutover** | ✅ 90% | Template with app-specific steps |
| **Validation: API tests** | ❌ 0% | App-specific endpoints |
| **Validation: DB tests** | ✅ 80% | Parameterize table names |
| **Business Logic** | ❌ 0% | Payment processing is SecureBank-specific |
| **PCI-DSS compliance** | ⚠️ 50% | Compliance rules vary by industry |
| **Frontend UI** | ❌ 0% | SecureBank branding/workflows |
| **Database schema** | ❌ 0% | Payment-specific tables |

---

## 🎯 Action Plan: Extract Reusable Components

### Step 1: Create Reusable Terraform Modules
```bash
4-Cloud-Migration/3-terraform-modules/
├── secure-vpc/          # ✅ 100% reusable
├── secure-s3/           # ✅ 90% reusable (parameterize lifecycle)
├── secure-rds/          # ✅ 90% reusable (parameterize retention)
├── secure-kms/          # ✅ 100% reusable
├── secure-secrets-manager/  # ✅ 95% reusable
├── secure-iam/          # ✅ 70% reusable (template policies)
├── secure-sg/           # ✅ 60% reusable (parameterize ports)
└── secure-cloudwatch/   # ✅ 90% reusable
```

**Variables for SecureBank:**
```hcl
# variables.tfvars (SecureBank-specific)
project_name          = "securebank"
environment           = "production"
compliance_framework  = "pci-dss"
backup_retention_days = 30              # PCI-DSS requirement
lifecycle_glacier_days = 90             # PCI-DSS requirement
```

---

### Step 2: Create Reusable AWS CLI Scripts
```bash
4-Cloud-Migration/2-aws-cli-scripts/
├── s3/create-bucket.sh              # ✅ 100% reusable
├── secrets-manager/create-secret.sh # ✅ 100% reusable
├── rds/create-db.sh                 # ✅ 100% reusable
└── kms/create-key.sh                # ✅ 100% reusable
```

**Usage for SecureBank:**
```bash
# SecureBank-specific values
PROJECT_NAME="securebank"
BUCKET_NAME="payment-receipts"
DB_NAME="payment-db"

# Call reusable scripts
./create-bucket.sh "$BUCKET_NAME"
./create-db.sh "$DB_NAME" "postgres" "14.10"
```

---

### Step 3: Create Reusable Migration Framework
```bash
4-Cloud-Migration/4-migration-scripts/
├── database-migration.sh            # ✅ 95% reusable (parameterize)
├── file-migration.sh                # ✅ 100% reusable
├── secrets-migration.sh             # ✅ 100% reusable (Vault → AWS)
└── cutover-plan.sh                  # ✅ 90% reusable (template)
```

---

### Step 4: Keep SecureBank-Specific in GP-PROJECTS
```bash
GP-PROJECTS/FINANCE-project/
├── backend/                         # ❌ SecureBank business logic
├── frontend/                        # ❌ SecureBank UI
├── infrastructure/securebank.tfvars # ⚠️ SecureBank-specific config
└── docs/                            # ⚠️ SecureBank documentation
```

---

## ✅ Final Recommendation

**Extract these to reusable Phase 4 framework:**
1. ✅ LocalStack setup (100% reusable)
2. ✅ Terraform modules (70-100% reusable with variables)
3. ✅ AWS CLI scripts (100% reusable with parameters)
4. ✅ Migration scripts (90-100% reusable)
5. ✅ Validation framework (80% reusable)

**Keep these in FINANCE-project:**
1. ❌ Payment processing logic
2. ❌ SecureBank UI
3. ❌ PCI-DSS specific compliance (make it a variable instead)
4. ❌ Database schema
5. ❌ API endpoints

**Result:**
- **Reusable framework** (Phase 4) can migrate ANY project (e-commerce, SaaS, IoT, etc.)
- **FINANCE-project** just provides SecureBank-specific values (bucket names, retention, etc.)

---

**Created:** 2025-10-14
**Status:** ✅ Analysis Complete
**Next:** Extract reusable components to Phase 4 framework
