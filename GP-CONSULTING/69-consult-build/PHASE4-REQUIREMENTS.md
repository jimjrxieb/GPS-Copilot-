# Phase 4: Cloud Migration - Complete Requirements

**Purpose:** Migrate bare metal applications to AWS (LocalStack for testing) with security-first approach

**Source:** Bare metal / Local environment
**Target:** AWS (LocalStack for testing, real AWS for production)
**Data Output:** `/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/4-migration`

---

## 🎯 What You Have (Phases 1-3)

### ✅ Phase 1: Security Assessment
- All vulnerabilities discovered
- Saved to: `GP-DATA/active/1-findings/`
- Format: JSON (bandit, semgrep, gitleaks, checkov, trivy, OPA)

### ✅ Phase 2: App-Sec Fixes
- Application-level vulnerabilities fixed
- Fix loop agents (re-scan until clean)
- Saved to: `GP-DATA/active/2-fixes/`
- Format: JSON (before/after comparison)

### ✅ Phase 3: Hardening
- Infrastructure vulnerabilities fixed
- IaC/Kubernetes/OPA errors resolved
- Best practices applied (from OPA eval)
- Deployment monitoring, rollback, escalation
- Saved to: `GP-DATA/active/3-hardening/`

---

## 🚀 What Phase 4 Needs (Migration to AWS/LocalStack)

### Current State: ❌ EMPTY
- `migration-scripts/` - Empty
- `terraform-modules/` - Empty
- `aws-fixers/` - Empty

### Required Components:

---

## 1️⃣ **Migration Scripts** (Bare Metal → AWS/LocalStack)

### What's Missing:

#### A. **Pre-Migration Assessment**
```bash
migration-scripts/
├── 1-pre-migration/
│   ├── assess-current-state.sh          # Inventory bare metal resources
│   ├── dependency-mapper.py             # Map service dependencies
│   ├── data-volume-calculator.sh        # Calculate data migration time
│   └── cost-estimator.py                # Estimate AWS costs
```

**Purpose:**
- Inventory: What's running on bare metal?
- Dependencies: Which services depend on each other?
- Data: How much data to migrate? (databases, files, volumes)
- Cost: What will it cost in AWS?

---

#### B. **LocalStack Setup & Validation**
```bash
migration-scripts/
├── 2-localstack-setup/
│   ├── install-localstack.sh            # Install LocalStack Docker
│   ├── configure-aws-cli.sh             # Configure awslocal
│   ├── test-localstack-services.sh      # Verify S3, EC2, RDS, etc.
│   └── seed-test-data.sh                # Seed with test data
```

**Purpose:**
- Test migration locally before touching real AWS
- Validate scripts work against LocalStack
- No AWS costs during development

**Example:**
```bash
# Install LocalStack
docker-compose up -d localstack

# Configure awslocal (LocalStack AWS CLI)
pip install awscli-local
awslocal s3 mb s3://test-bucket

# Test S3 operations
awslocal s3 ls
```

---

#### C. **Data Migration Scripts**
```bash
migration-scripts/
├── 3-data-migration/
│   ├── database-migration.sh            # PostgreSQL/MySQL → RDS
│   │   - Schema migration
│   │   - Data migration (incremental)
│   │   - Validation queries
│   │   - Rollback plan
│   │
│   ├── file-migration.sh                # Files → S3
│   │   - Sync files to S3
│   │   - Preserve permissions/metadata
│   │   - Verify checksums
│   │   - Handle large files (multipart)
│   │
│   ├── secrets-migration.sh             # Vault → Secrets Manager
│   │   - Extract from Vault
│   │   - Upload to AWS Secrets Manager
│   │   - Update app configs
│   │   - Rotate secrets post-migration
│   │
│   └── volume-migration.sh              # Disk volumes → EBS/EFS
│       - Snapshot volumes
│       - Create EBS volumes
│       - Attach to EC2/EKS
```

**What you're missing:**
- **Database migration strategy** (schema + data)
- **File migration to S3** (with validation)
- **Secrets migration** (Vault → Secrets Manager)
- **Volume migration** (local disks → EBS/EFS)

---

#### D. **Infrastructure Deployment (AWS CLI + Terraform)**
```bash
migration-scripts/
├── 4-infrastructure/
│   ├── aws-cli/
│   │   ├── create-vpc.sh                # aws ec2 create-vpc
│   │   ├── create-s3-buckets.sh         # aws s3 mb, policies
│   │   ├── create-rds.sh                # aws rds create-db-instance
│   │   ├── create-secrets.sh            # aws secretsmanager create-secret
│   │   ├── create-iam-roles.sh          # aws iam create-role
│   │   └── create-kms-keys.sh           # aws kms create-key
│   │
│   └── terraform/
│       ├── main.tf                      # Terraform orchestration
│       ├── vpc.tf                       # VPC module
│       ├── rds.tf                       # RDS module
│       ├── s3.tf                        # S3 module
│       ├── eks.tf                       # EKS module (if K8s)
│       └── secrets.tf                   # Secrets Manager
```

**What you're missing:**
- **AWS CLI scripts** for creating resources
- **S3 bucket creation** with proper policies (you mentioned this!)
- **RDS setup** (encrypted, backup enabled)
- **Secrets Manager integration** (you mentioned this!)
- **IAM roles** for services
- **KMS keys** for encryption

---

#### E. **Application Containerization**
```bash
migration-scripts/
├── 5-containerization/
│   ├── dockerize-app.sh                 # Create Dockerfiles
│   ├── build-images.sh                  # Build Docker images
│   ├── push-to-ecr.sh                   # Push to AWS ECR
│   ├── scan-images.sh                   # Trivy scan before deploy
│   └── deploy-to-ecs-eks.sh             # Deploy to ECS/EKS
```

**What you're missing:**
- Containerization scripts (if bare metal apps aren't containerized)
- ECR integration
- ECS/EKS deployment

---

#### F. **API & Endpoint Migration**
```bash
migration-scripts/
├── 6-api-migration/
│   ├── update-api-endpoints.sh          # Update API URLs
│   ├── test-api-calls.sh                # Validate API calls work
│   ├── migrate-load-balancers.sh        # Nginx/HAProxy → ALB/NLB
│   └── update-dns.sh                    # Route53 DNS updates
```

**What you're missing:**
- **API endpoint validation** (you mentioned "making sure api calls are correct")
- Load balancer migration
- DNS updates

---

#### G. **Cutover & Rollback**
```bash
migration-scripts/
├── 7-cutover/
│   ├── cutover-plan.sh                  # Step-by-step cutover
│   │   - Stop bare metal services
│   │   - Final data sync
│   │   - Update DNS
│   │   - Start AWS services
│   │   - Smoke tests
│   │
│   ├── rollback-plan.sh                 # Rollback to bare metal
│   │   - Stop AWS services
│   │   - Reverse DNS changes
│   │   - Start bare metal services
│   │   - Sync data back (if needed)
│   │
│   ├── validation-suite.sh              # Post-migration validation
│   │   - Health checks
│   │   - API tests
│   │   - Database queries
│   │   - Performance tests
│   │
│   └── parallel-run.sh                  # Run both environments
│       - Dual-write to both
│       - Compare results
│       - Gradual traffic shift
```

**What you're missing:**
- **Cutover plan** (step-by-step migration day plan)
- **Rollback plan** (if migration fails)
- **Validation suite** (prove migration worked)
- **Parallel run** (run both environments, compare)

---

## 2️⃣ **Terraform Modules** (Reusable AWS Resources)

### What's Missing:

```bash
terraform-modules/
├── secure-vpc/
│   ├── main.tf                          # VPC with Flow Logs
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
│
├── secure-s3/
│   ├── main.tf                          # S3 with encryption, versioning
│   ├── variables.tf
│   ├── outputs.tf
│   └── bucket-policy.json
│
├── secure-rds/
│   ├── main.tf                          # RDS with encryption, SSL
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
│
├── secure-secrets-manager/
│   ├── main.tf                          # Secrets Manager with rotation
│   ├── variables.tf
│   ├── outputs.tf
│   └── rotation-lambda.py
│
├── secure-eks/
│   ├── main.tf                          # EKS with Pod Security
│   ├── variables.tf
│   ├── outputs.tf
│   └── README.md
│
└── secure-iam/
    ├── main.tf                          # IAM roles/policies
    ├── variables.tf
    ├── outputs.tf
    └── least-privilege-policies.json
```

**Each module should:**
- Follow Phase 3 best practices (from `3-Hardening/best-practices/`)
- Be validated by Phase 3 OPA policies (from `3-Hardening/policies/opa/`)
- Include encryption by default
- Include monitoring/logging
- Include backup/disaster recovery

---

## 3️⃣ **AWS CLI Scripts** (Direct AWS Operations)

### What's Missing:

```bash
aws-cli-scripts/
├── s3/
│   ├── create-bucket.sh                 # Create S3 with encryption
│   ├── set-bucket-policy.sh             # Apply least-privilege policy
│   ├── enable-versioning.sh             # Enable versioning
│   ├── configure-lifecycle.sh           # Auto-expire old objects
│   └── sync-files.sh                    # Sync local → S3
│
├── secrets-manager/
│   ├── create-secret.sh                 # Create secret
│   ├── rotate-secret.sh                 # Rotate secret
│   ├── migrate-from-vault.sh            # Import from Vault
│   └── update-app-config.sh             # Update app to use Secrets Manager
│
├── rds/
│   ├── create-db.sh                     # Create RDS with encryption
│   ├── create-read-replica.sh           # Create read replicas
│   ├── enable-backup.sh                 # Configure backups
│   └── test-connection.sh               # Validate DB connectivity
│
├── kms/
│   ├── create-key.sh                    # Create KMS key
│   ├── create-alias.sh                  # Create key alias
│   ├── set-key-policy.sh                # Least-privilege key policy
│   └── enable-rotation.sh               # Enable automatic rotation
│
├── iam/
│   ├── create-role.sh                   # Create IAM role
│   ├── attach-policy.sh                 # Attach policies
│   ├── create-instance-profile.sh       # For EC2
│   └── test-permissions.sh              # Validate permissions
│
└── monitoring/
    ├── enable-cloudtrail.sh             # Enable CloudTrail
    ├── enable-cloudwatch.sh             # Create CloudWatch alarms
    ├── enable-guardduty.sh              # Enable GuardDuty
    └── create-dashboards.sh             # CloudWatch dashboards
```

---

## 4️⃣ **LocalStack Testing Framework**

### What's Missing:

```bash
localstack-tests/
├── setup-localstack.sh                  # Start LocalStack container
├── test-s3.sh                           # Test S3 operations
├── test-rds.sh                          # Test RDS operations
├── test-secrets-manager.sh              # Test Secrets Manager
├── test-iam.sh                          # Test IAM roles
├── test-kms.sh                          # Test KMS encryption
├── test-api-gateway.sh                  # Test API Gateway (if used)
└── cleanup-localstack.sh                # Clean up test resources
```

**Purpose:**
- Test all AWS CLI commands against LocalStack first
- Validate Terraform modules work with LocalStack
- No AWS costs during development
- Fast iteration

**Example:**
```bash
# Start LocalStack
./setup-localstack.sh

# Test S3 bucket creation
awslocal s3 mb s3://test-bucket
awslocal s3 ls

# Test Secrets Manager
awslocal secretsmanager create-secret \
  --name db-password \
  --secret-string "test123"

# Test RDS (LocalStack Pro)
awslocal rds create-db-instance \
  --db-instance-identifier test-db \
  --engine postgres
```

---

## 5️⃣ **Migration Validation & Testing**

### What's Missing:

```bash
validation/
├── pre-migration-tests.sh               # Run before migration
│   - Check all services running on bare metal
│   - Validate data integrity
│   - Document current state
│
├── during-migration-tests.sh            # Run during migration
│   - Monitor data sync progress
│   - Check for errors
│   - Validate partial migration
│
├── post-migration-tests.sh              # Run after migration
│   - Health checks (all services up?)
│   - API tests (all endpoints working?)
│   - Database queries (data migrated?)
│   - Performance tests (latency acceptable?)
│   - Security tests (Phase 1 scanners)
│
└── comparison-tests.sh                  # Compare bare metal vs AWS
    - Compare API responses
    - Compare database data
    - Compare performance metrics
```

---

## 6️⃣ **Disaster Recovery & Business Continuity**

### What's Missing:

```bash
disaster-recovery/
├── backup-strategy.md                   # Backup plan (RPO/RTO)
├── backup-automation.sh                 # Automated backups
│   - RDS snapshots
│   - S3 versioning
│   - EBS snapshots
│   - Configuration backups
│
├── restore-procedures.sh                # Restore from backups
│   - Restore RDS from snapshot
│   - Restore S3 from versioning
│   - Restore EBS volumes
│
└── multi-region-replication.sh          # Cross-region replication
    - S3 replication
    - RDS read replicas
    - Disaster recovery region
```

---

## 7️⃣ **Cost Optimization**

### What's Missing:

```bash
cost-optimization/
├── right-sizing.sh                      # Analyze and right-size instances
├── reserved-instances.sh                # Calculate RI savings
├── spot-instances.sh                    # Use spot for non-critical
├── lifecycle-policies.sh                # Auto-expire old data
└── cost-monitoring.sh                   # CloudWatch cost alarms
```

---

## 8️⃣ **Networking & Connectivity**

### What's Missing:

```bash
networking/
├── vpc-setup.sh                         # Create VPC (aws cli)
├── subnet-setup.sh                      # Public/private subnets
├── security-groups.sh                   # Least-privilege SGs
├── vpc-peering.sh                       # If multi-VPC
├── vpn-setup.sh                         # If hybrid (bare metal + AWS)
└── dns-setup.sh                         # Route53 configuration
```

---

## 9️⃣ **Monitoring & Observability**

### What's Missing:

```bash
monitoring/
├── cloudwatch-setup.sh                  # CloudWatch logs/metrics
├── cloudtrail-setup.sh                  # Audit trail
├── guardduty-setup.sh                   # Threat detection
├── security-hub-setup.sh                # Compliance dashboard
├── xray-setup.sh                        # Distributed tracing
└── dashboards.sh                        # CloudWatch dashboards
```

---

## 🔟 **Compliance & Governance**

### What's Missing:

```bash
compliance/
├── config-setup.sh                      # AWS Config (compliance)
├── compliance-rules.sh                  # Config rules
├── remediation.sh                       # Auto-remediation
└── audit-reports.sh                     # Generate compliance reports
```

---

## 📊 What You're Missing (Summary)

| Component | Status | Priority |
|-----------|--------|----------|
| **LocalStack setup** | ❌ Missing | 🔴 Critical |
| **S3 bucket creation (AWS CLI)** | ❌ Missing | 🔴 Critical |
| **Secrets Manager integration** | ❌ Missing | 🔴 Critical |
| **API validation scripts** | ❌ Missing | 🔴 Critical |
| **Database migration** | ❌ Missing | 🔴 Critical |
| **File migration to S3** | ❌ Missing | 🔴 Critical |
| **Cutover plan** | ❌ Missing | 🔴 Critical |
| **Rollback plan** | ❌ Missing | 🔴 Critical |
| **Terraform modules** | ❌ Missing | 🟡 High |
| **Pre-migration assessment** | ❌ Missing | 🟡 High |
| **Validation suite** | ❌ Missing | 🟡 High |
| **Monitoring setup** | ❌ Missing | 🟡 High |
| **Cost optimization** | ❌ Missing | 🟢 Medium |
| **Disaster recovery** | ❌ Missing | 🟢 Medium |

---

## 🎯 Phase 4 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BARE METAL                                │
│  - Application servers                                           │
│  - PostgreSQL/MySQL databases                                    │
│  - File storage                                                  │
│  - Vault secrets                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [PHASE 4 MIGRATION]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 AWS (LocalStack for testing)                     │
│                                                                  │
│  Applications:                                                   │
│  - ECS/EKS containers ← Dockerized apps                         │
│  - Lambda functions ← Serverless components                      │
│                                                                  │
│  Data:                                                           │
│  - RDS (encrypted) ← Database migration                          │
│  - S3 (versioned) ← File migration                              │
│  - DynamoDB ← NoSQL (if applicable)                             │
│                                                                  │
│  Secrets:                                                        │
│  - Secrets Manager ← Vault migration                             │
│  - KMS encryption ← All secrets encrypted                        │
│                                                                  │
│  Networking:                                                     │
│  - VPC (Flow Logs) ← Secure network                             │
│  - ALB/NLB ← Load balancing                                      │
│  - API Gateway ← API management                                  │
│                                                                  │
│  Security:                                                       │
│  - IAM roles (least privilege) ← From Phase 3 policies          │
│  - Security Groups (restrictive) ← From Phase 3 fixers           │
│  - CloudTrail ← Audit logging                                    │
│  - GuardDuty ← Threat detection                                  │
│                                                                  │
│  Monitoring:                                                     │
│  - CloudWatch ← Logs, metrics, alarms                            │
│  - X-Ray ← Distributed tracing                                   │
│  - Security Hub ← Compliance dashboard                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Recommended Implementation Order

### Week 1: LocalStack Setup & Testing
1. Install LocalStack
2. Create AWS CLI scripts (S3, Secrets Manager, RDS)
3. Test scripts against LocalStack
4. Validate API calls work

### Week 2: Terraform Modules
1. Create secure-vpc module
2. Create secure-s3 module
3. Create secure-rds module
4. Create secure-secrets-manager module
5. Test modules with LocalStack

### Week 3: Migration Scripts
1. Pre-migration assessment
2. Database migration scripts
3. File migration scripts (to S3)
4. Secrets migration (Vault → Secrets Manager)

### Week 4: Validation & Testing
1. Post-migration validation suite
2. API testing framework
3. Performance testing
4. Security scanning (Phase 1)

### Week 5: Cutover Planning
1. Cutover plan (step-by-step)
2. Rollback plan
3. Disaster recovery procedures
4. Monitoring/alerting setup

---

## 📁 Proposed Phase 4 Structure

```
4-Cloud-Migration/
├── README.md
├── PHASE4-REQUIREMENTS.md               # This file
│
├── 1-localstack/                        # ✨ NEW
│   ├── docker-compose.yml               # LocalStack container
│   ├── setup-localstack.sh
│   ├── test-services.sh
│   └── cleanup.sh
│
├── 2-aws-cli-scripts/                   # ✨ NEW
│   ├── s3/
│   ├── secrets-manager/
│   ├── rds/
│   ├── kms/
│   ├── iam/
│   └── monitoring/
│
├── 3-terraform-modules/                 # ✨ POPULATE
│   ├── secure-vpc/
│   ├── secure-s3/
│   ├── secure-rds/
│   ├── secure-secrets-manager/
│   └── secure-eks/
│
├── 4-migration-scripts/                 # ✨ NEW
│   ├── 1-pre-migration/
│   ├── 2-data-migration/
│   ├── 3-infrastructure/
│   ├── 4-containerization/
│   ├── 5-api-migration/
│   └── 6-cutover/
│
├── 5-validation/                        # ✨ NEW
│   ├── pre-migration-tests.sh
│   ├── post-migration-tests.sh
│   ├── api-tests.sh
│   └── comparison-tests.sh
│
├── 6-disaster-recovery/                 # ✨ NEW
│   ├── backup-strategy.md
│   ├── backup-automation.sh
│   └── restore-procedures.sh
│
├── cloud-patterns/                      # ✅ ALREADY EXISTS (moved from Phase 3)
│
└── GP-DATA/active/4-migration/          # ✨ Output directory
    ├── pre-migration-inventory.json
    ├── migration-progress.json
    ├── post-migration-validation.json
    └── cost-analysis.json
```

---

**Status:** 🔴 Incomplete - Needs implementation
**Next Steps:** Create LocalStack setup, AWS CLI scripts, migration automation
