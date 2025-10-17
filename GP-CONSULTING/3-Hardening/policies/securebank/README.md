# SecureBank Security Policies

**Policy-as-Code for SecureBank Payment Platform**

---

## Overview

This directory contains all security policies for SecureBank:
- **OPA/Conftest** (CD): Pre-deployment Terraform validation
- **OPA Gatekeeper** (Runtime): Kubernetes admission control
- **AWS Policy-as-Code**: IAM policies, S3 bucket policies, Secrets Manager

---

## Directory Structure

```
policies/securebank/
├── opa-conftest/               # CD-layer Terraform validation
│   ├── vpc-security.rego       # VPC compliance (CIS AWS 5.x, PCI-DSS 1.x)
│   ├── s3-security.rego        # S3 compliance (CIS AWS 2.x, PCI-DSS 3.4)
│   └── iam-security.rego       # IAM compliance (CIS AWS 1.x, PCI-DSS 7.1)
│
├── opa-gatekeeper/             # Runtime Kubernetes admission control
│   ├── constraint-templates.yaml  # Reusable Rego templates
│   ├── constraints.yaml           # Policy enforcement (deny mode)
│   └── mutations.yaml             # Auto-inject security context
│
└── aws-policy-as-code/         # AWS IAM and resource policies
    ├── secrets-manager-setup.sh   # Create secrets in Secrets Manager
    ├── iam-policies.json          # Least-privilege IAM policies
    └── s3-bucket-policies.json    # S3 bucket policies
```

---

## OPA/Conftest (CD Layer)

**Purpose:** Validate Terraform files BEFORE `terraform apply`

**Usage:**
```bash
# Run OPA/Conftest scanner
cd secops/1-scanners/cd
./scan-opa-conftest.sh

# Results saved to:
secops/2-findings/raw/opa-conftest-results.json
```

**Policies:**
1. **vpc-security.rego**
   - VPC Flow Logs (CIS AWS 3.9, PCI-DSS 10.1)
   - Security groups (PCI-DSS 1.2.1)
   - Public database exposure
   - Private subnets for RDS

2. **s3-security.rego**
   - S3 encryption (PCI-DSS 3.4, CIS AWS 2.1.1)
   - Versioning (PCI-DSS 10.5.3, CIS AWS 2.1.3)
   - Public access blocks
   - Logging enabled

3. **iam-security.rego**
   - Wildcard actions (PCI-DSS 7.1, CIS AWS 1.16)
   - Wildcard resources
   - IAM user access keys (prefer roles)
   - Root account usage

---

## OPA Gatekeeper (Runtime Layer)

**Purpose:** Enforce policies DURING `kubectl apply` via admission webhooks

**Installation:**
```bash
# 1. Install Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.14.0/deploy/gatekeeper.yaml

# 2. Deploy SecureBank policies
kubectl apply -f policies/securebank/opa-gatekeeper/constraint-templates.yaml
kubectl apply -f policies/securebank/opa-gatekeeper/constraints.yaml
kubectl apply -f policies/securebank/opa-gatekeeper/mutations.yaml

# 3. Verify
kubectl get constrainttemplates
kubectl get constraints
```

**Constraint Templates:**
1. **k8srequirenonroot** - Enforces `runAsNonRoot: true`
2. **k8sblockprivileged** - Blocks `privileged: true` containers
3. **k8sblockcvvpin** - Detects CVV/PIN in ConfigMaps/Secrets

**Constraints (Enforcement):**
- `require-non-root` (deny mode)
- `block-privileged-containers` (deny mode)
- `block-cvv-pin-in-configmaps` (deny mode)

**Mutations (Auto-Fix):**
- Automatically adds `securityContext` to pods:
  ```yaml
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  ```

**Verification:**
```bash
# Check constraints
kubectl get constraints

# Verify auto-injection
kubectl get pod -n securebank -l app=securebank \
  -o jsonpath='{.items[0].spec.securityContext}' | jq .
```

---

## AWS Policy-as-Code

### 1. Secrets Manager Setup

**Purpose:** Store credentials securely (PCI-DSS 8.2.1)

**Usage:**
```bash
# LocalStack (demo)
export LOCALSTACK_ENDPOINT=http://localhost:4566
./policies/securebank/aws-policy-as-code/secrets-manager-setup.sh

# Real AWS
export LOCALSTACK_ENDPOINT=""
export AWS_REGION=us-east-1
./policies/securebank/aws-policy-as-code/secrets-manager-setup.sh
```

**Secrets Created:**
- `securebank/database` - Database credentials
- `securebank/stripe-api-key` - Payment processor API key
- `securebank/jwt-secret` - JWT signing key
- `securebank/encryption-key` - Application encryption key

### 2. IAM Policies

**File:** `iam-policies.json`

**Policies:**
1. **SecureBankLeastPrivilege**
   - Secrets Manager read (securebank/* only)
   - S3 read (payment receipts)
   - CloudWatch Logs write
   - KMS decrypt (via S3/Secrets Manager only)

2. **SecureBankEKSNodePolicy**
   - EKS node permissions
   - ECR image pull

3. **SecureBankDenyDangerousActions**
   - Deny public S3 access changes
   - Deny unencrypted S3 uploads
   - Deny secret deletion

**Apply to Terraform:**
```hcl
data "local_file" "securebank_policies" {
  filename = "${path.module}/../../policies/securebank/aws-policy-as-code/iam-policies.json"
}

locals {
  securebank_policies = jsondecode(data.local_file.securebank_policies.content)
}

resource "aws_iam_policy" "securebank_least_privilege" {
  name   = "SecureBankLeastPrivilege"
  policy = jsonencode(local.securebank_policies.SecureBankLeastPrivilege)
}
```

### 3. S3 Bucket Policies

**File:** `s3-bucket-policies.json`

**Policies:**
1. **PaymentReceiptsBucketPolicy**
   - Deny unencrypted uploads
   - Deny insecure transport (enforce HTTPS)
   - Allow SecureBank backend role only
   - Require KMS encryption

2. **AuditLogsBucketPolicy**
   - Deny unencrypted uploads
   - Deny insecure transport
   - Allow CloudWatch Logs service
   - **Deny deletion** (immutable audit logs)

**Apply:**
```bash
# Attach to S3 bucket
aws s3api put-bucket-policy \
  --bucket securebank-payment-receipts-prod \
  --policy file://policies/securebank/aws-policy-as-code/s3-bucket-policies.json \
  --query PaymentReceiptsBucketPolicy
```

---

## Compliance Mappings

### PCI-DSS 4.0
- **1.2.1** - Security groups (VPC policy, Gatekeeper)
- **2.2.1** - No privileged containers (Gatekeeper)
- **2.2.4** - Non-root containers (Gatekeeper)
- **3.2.2/3.2.3** - No CVV/PIN storage (Gatekeeper)
- **3.4** - S3 encryption (S3 policy, OPA/Conftest)
- **7.1** - Least privilege IAM (IAM policy, OPA/Conftest)
- **8.2.1** - Secrets Manager (AWS policy-as-code)
- **10.1** - VPC Flow Logs (VPC policy, OPA/Conftest)
- **10.5.3** - S3 versioning (S3 policy, OPA/Conftest)

### CIS Benchmarks
- **CIS AWS 1.x** - IAM policies
- **CIS AWS 2.x** - S3 policies
- **CIS AWS 3.x** - VPC policies
- **CIS AWS 5.x** - VPC security
- **CIS Kubernetes 5.x** - Pod Security (Gatekeeper)

---

## Integration with SecOps Framework

### CI/CD/Runtime Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ CI (Pre-commit)                                             │
│ - Bandit, Semgrep, Gitleaks, Trivy                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ CD (Pre-deployment)                                         │
│ - OPA/Conftest validates Terraform                         │
│ - Policies: vpc-security.rego, s3-security.rego, iam       │
│ - Blocks: Public S3, wildcard IAM, no encryption           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Runtime (Production)                                        │
│ - OPA Gatekeeper enforces K8s admission control            │
│ - Auto-mutation: Adds securityContext                      │
│ - Admission denial: Blocks privileged/root/CVV             │
└─────────────────────────────────────────────────────────────┘
```

### Scanner Integration

```bash
# CD scanner uses these policies
secops/1-scanners/cd/scan-opa-conftest.sh
  └── Uses: policies/securebank/opa-conftest/*.rego

# Runtime enforcement
kubectl apply -f infrastructure/k8s/deployment.yaml
  └── Gatekeeper enforces: policies/securebank/opa-gatekeeper/*.yaml
```

---

## Demo Script

### Show OPA/Conftest (CD)
```bash
# 1. Run Terraform validation
cd secops/1-scanners/cd
./scan-opa-conftest.sh

# 2. Show violations detected
cat secops/2-findings/raw/opa-conftest-results.json | jq '.failures[] | {policy: .filename, message: .msg}'
```

### Show OPA Gatekeeper (Runtime)
```bash
# 1. Check constraint status
kubectl get constraints

# 2. Show auto-injection
kubectl get pod -n securebank -l app=securebank \
  -o jsonpath='{.spec.securityContext}' | jq .

# 3. Try to deploy privileged pod (will be DENIED)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: test-privileged
  namespace: securebank
spec:
  containers:
  - name: test
    image: nginx
    securityContext:
      privileged: true
EOF
```

### Show AWS Policy-as-Code
```bash
# 1. Create secrets
./policies/securebank/aws-policy-as-code/secrets-manager-setup.sh

# 2. Show IAM policies
cat policies/securebank/aws-policy-as-code/iam-policies.json | jq '.SecureBankLeastPrivilege'

# 3. Show S3 policies
cat policies/securebank/aws-policy-as-code/s3-bucket-policies.json | jq '.PaymentReceiptsBucketPolicy'
```

---

## Files

- **3 Rego policies** (OPA/Conftest)
- **3 ConstraintTemplates** (Gatekeeper)
- **3 Constraints** (Gatekeeper)
- **2 Mutations** (Gatekeeper)
- **1 Secrets setup script** (AWS)
- **3 IAM policies** (AWS)
- **2 S3 bucket policies** (AWS)

**Total:** 17 policy-as-code artifacts

---

**Last Updated:** 2025-10-09
**Compliance:** PCI-DSS 4.0, CIS AWS, CIS Kubernetes
**Status:** ✅ Production-ready
