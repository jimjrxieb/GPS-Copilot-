# Phase 3: Infrastructure Hardening

**Purpose:** Secure infrastructure, deployment configs, and runtime environment

---

## Overview

Phase 3 focuses on **CD-level security hardening** - securing infrastructure and deployment:

- **IaC misconfigurations** → Fix Terraform/CloudFormation
- **Kubernetes security** → Pod security policies, RBAC, network policies
- **Container hardening** → Read-only filesystems, non-root users
- **Secrets management** → Vault, AWS Secrets Manager integration
- **Policy enforcement** → OPA Gatekeeper admission control

---

## Directory Structure

```
3-Hardening/
├── fixers/                    # CD-level auto-fixers
│   ├── fix-s3-encryption.sh
│   ├── fix-rds-ssl.sh
│   ├── fix-kubernetes-security.sh
│   ├── fix-k8s-hardcoded-secrets.sh
│   ├── fix-vpc-flow-logs.sh
│   ├── fix-cloudwatch-logs.sh
│   └── fix-eks-security.sh
├── mutators/                  # OPA Gatekeeper admission control
│   ├── gatekeeper-constraints/
│   │   ├── deny-privileged-pods.yaml
│   │   ├── require-resource-limits.yaml
│   │   └── enforce-pod-security.yaml
│   └── deploy-gatekeeper.sh
├── policies/                  # Centralized security policies (enforcement layer)
│   ├── opa/                   # OPA/Rego enforcement policies (12 policies)
│   │   ├── terraform-security.rego       # Terraform IaC validation
│   │   ├── kubernetes.rego               # K8s resource validation
│   │   ├── pod-security.rego            # Pod Security Standards
│   │   ├── network-policies.rego        # Network policy enforcement
│   │   ├── rbac.rego                    # RBAC validation
│   │   ├── secrets-management.rego      # Secrets handling
│   │   ├── image-security.rego          # Container image security
│   │   ├── cicd-security.rego           # CI/CD pipeline security
│   │   ├── compliance-controls.rego     # Cross-framework compliance
│   │   ├── security-policy.rego         # General security rules
│   │   ├── security.rego                # Core security controls
│   │   └── network.rego                 # Network security
│   ├── gatekeeper/            # Kubernetes admission control
│   │   ├── templates/         # ConstraintTemplate definitions
│   │   │   └── pod-security-template.yaml
│   │   └── constraints/       # Constraint instances
│   │       └── production/
│   │           └── pod-security-constraint.yaml
│   └── securebank/            # SecureBank PCI-DSS policy suite
│       ├── README.md
│       ├── opa-conftest/      # Terraform validation policies
│       │   ├── vpc-security.rego
│       │   ├── s3-security.rego
│       │   └── iam-security.rego
│       ├── opa-gatekeeper/    # K8s admission control
│       │   ├── constraint-templates.yaml
│       │   ├── constraints.yaml
│       │   └── mutations.yaml
│       └── aws-policy-as-code/
│           ├── iam-policies.json
│           ├── s3-bucket-policies.json
│           └── secrets-manager-setup.sh
└── secrets-management/        # Vault/Secrets Manager integration
    ├── vault-setup.sh
    └── secrets-migration.sh
```

---

## Automated Fixers

### 1. S3 Encryption Fixer
**File:** `fixers/fix-s3-encryption.sh`

**What it fixes:**
- S3 buckets without server-side encryption
- Missing bucket versioning
- Public access not blocked
- No lifecycle policies

**Usage:**
```bash
cd fixers/
bash fix-s3-encryption.sh /path/to/terraform
```

**Changes applied:**
```hcl
# Adds to S3 bucket resources
server_side_encryption_configuration {
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

versioning {
  enabled = true
}

public_access_block {
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

---

### 2. RDS SSL Enforcement Fixer
**File:** `fixers/fix-rds-ssl.sh`

**What it fixes:**
- RDS instances without SSL/TLS enforcement
- Unencrypted storage
- Backups not encrypted
- No deletion protection

**Usage:**
```bash
bash fix-rds-ssl.sh /path/to/terraform
```

**Changes applied:**
```hcl
# Adds to RDS parameter group
parameter {
  name  = "rds.force_ssl"
  value = "1"
}

# Enables encryption
storage_encrypted = true
kms_key_id       = aws_kms_key.rds.arn

# Enables deletion protection
deletion_protection = true
```

---

### 3. Kubernetes Security Fixer
**File:** `fixers/fix-kubernetes-security.sh`

**What it fixes:**
- Privileged containers
- Missing resource limits
- No security context
- Running as root
- No network policies

**Usage:**
```bash
bash fix-kubernetes-security.sh /path/to/k8s
```

**Changes applied:**
```yaml
# Adds to all Deployments
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault

  containers:
  - securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]

    resources:
      limits:
        cpu: "1"
        memory: "512Mi"
      requests:
        cpu: "100m"
        memory: "128Mi"
```

---

### 4. Kubernetes Secrets Fixer
**File:** `fixers/fix-k8s-hardcoded-secrets.sh`

**What it fixes:**
- Hardcoded secrets in K8s manifests
- Plain-text ConfigMaps with sensitive data
- Unencrypted Secrets

**Usage:**
```bash
bash fix-k8s-hardcoded-secrets.sh /path/to/k8s
```

**How it works:**
1. Extracts hardcoded secrets from manifests
2. Creates Kubernetes Secret resources
3. Replaces hardcoded values with `secretKeyRef`
4. Optionally encrypts with Sealed Secrets

**Example:**
```yaml
# Before
env:
- name: DATABASE_PASSWORD
  value: "admin123"

# After
env:
- name: DATABASE_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-credentials
      key: password
```

---

## Centralized Security Policies

Phase 3 contains the **centralized policy enforcement layer** used across all phases:

### Policy Organization

```
policies/
├── opa/               # OPA/Rego policies (12 files) - Referenced by Phase 1 scanners
├── gatekeeper/        # Kubernetes admission control - Deployed in Phase 3
└── securebank/        # PCI-DSS policy suite - SecureBank project
```

### OPA Policies (`policies/opa/`)

**12 Rego policies** for infrastructure and application security:

| Policy | Purpose | Used By |
|--------|---------|---------|
| `terraform-security.rego` | Terraform IaC validation | Phase 1 (scanner), Phase 4 (pre-deploy) |
| `kubernetes.rego` | K8s resource validation | Phase 1 (scanner), Phase 3 (enforcement) |
| `pod-security.rego` | Pod Security Standards | Phase 3 (Gatekeeper), Phase 5 (audit) |
| `network-policies.rego` | Network policy enforcement | Phase 1 (scanner), Phase 3 (enforcement) |
| `rbac.rego` | RBAC validation | Phase 1 (scanner), Phase 5 (audit) |
| `secrets-management.rego` | Secrets handling | Phase 1 (scanner), Phase 3 (enforcement) |
| `image-security.rego` | Container image security | Phase 1 (scanner), Phase 6 (CI/CD) |
| `cicd-security.rego` | CI/CD pipeline security | Phase 6 (automation) |
| `compliance-controls.rego` | Cross-framework compliance | Phase 5 (compliance audit) |
| `security-policy.rego` | General security rules | All phases |
| `security.rego` | Core security controls | All phases |
| `network.rego` | Network security | Phase 1 (scanner), Phase 3 (enforcement) |

**Multi-Phase Usage:**

```bash
# Phase 1: OPA as scanner (discover violations)
cd ../1-Security-Assessment/cd-scanners
./scan-opa-conftest.sh  # References: ../../3-Hardening/policies/opa/

# Phase 3: OPA policies deployed with Gatekeeper (enforce violations)
kubectl apply -f policies/gatekeeper/templates/
kubectl apply -f policies/gatekeeper/constraints/

# Phase 4: OPA validates AWS resources pre-deploy
opa eval --data policies/opa/ --input terraform.tfplan

# Phase 5: OPA generates compliance evidence
cd ../5-Compliance-Audit
./compliance_validator.py --policies ../3-Hardening/policies/opa/

# Phase 6: OPA in CI/CD pipelines (continuous enforcement)
conftest test terraform/ --policy GP-CONSULTING/3-Hardening/policies/opa/
```

### Gatekeeper Policies (`policies/gatekeeper/`)

**Kubernetes admission control** for runtime policy enforcement:

**Templates** (`templates/`):
- `pod-security-template.yaml` - ConstraintTemplate for Pod Security Standards

**Constraints** (`constraints/production/`):
- `pod-security-constraint.yaml` - Enforces pod security requirements

**Deploy Gatekeeper:**
```bash
# Install Gatekeeper (if not already installed)
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml

# Deploy templates
kubectl apply -f policies/gatekeeper/templates/

# Deploy constraints
kubectl apply -f policies/gatekeeper/constraints/production/

# Verify deployment
kubectl get constrainttemplates
kubectl get constraints
```

### SecureBank Policy Suite (`policies/securebank/`)

**PCI-DSS 4.0 compliant** policy suite for payment platform:

**OPA/Conftest Policies** (`opa-conftest/`):
- `vpc-security.rego` - VPC configuration validation (PCI Requirement 1.x)
- `s3-security.rego` - S3 encryption and access (PCI Requirements 3.x, 10.x)
- `iam-security.rego` - Least privilege IAM (PCI Requirement 7.x)

**Gatekeeper Policies** (`opa-gatekeeper/`):
- `constraint-templates.yaml` - K8s admission control templates
- `constraints.yaml` - PCI-specific constraints (no CVV/PIN storage)
- `mutations.yaml` - Auto-injection of security settings

**AWS Policy-as-Code** (`aws-policy-as-code/`):
- `iam-policies.json` - Least privilege IAM policies
- `s3-bucket-policies.json` - S3 bucket policies with encryption
- `secrets-manager-setup.sh` - AWS Secrets Manager configuration

**SecureBank Usage:**
```bash
# Validate Terraform with SecureBank policies
conftest test infrastructure/terraform/ \
  --policy GP-CONSULTING/3-Hardening/policies/securebank/opa-conftest/

# Deploy K8s Gatekeeper constraints
kubectl apply -f GP-CONSULTING/3-Hardening/policies/securebank/opa-gatekeeper/

# Setup AWS Secrets Manager
bash GP-CONSULTING/3-Hardening/policies/securebank/aws-policy-as-code/secrets-manager-setup.sh
```

**See**: [securebank/README.md](policies/securebank/README.md) for detailed PCI-DSS mapping

---

## Policy Enforcement (OPA Gatekeeper)

### Deploy Gatekeeper

```bash
cd mutators/
bash deploy-gatekeeper.sh
```

This installs OPA Gatekeeper as a Kubernetes admission controller.

### Available Constraints

| Constraint | Purpose | Enforcement |
|------------|---------|-------------|
| `deny-privileged-pods.yaml` | Block privileged containers | DENY |
| `require-resource-limits.yaml` | Enforce CPU/memory limits | DENY |
| `enforce-pod-security.yaml` | Require security context | DENY |
| `block-latest-tag.yaml` | Block `:latest` image tags | DENY |
| `require-labels.yaml` | Enforce labeling standards | WARN |

### Apply Constraints

```bash
kubectl apply -f mutators/gatekeeper-constraints/
```

---

## OPA Policies

Located in `policies/opa/`, these policies validate infrastructure-as-code:

### Terraform Security Policy
**File:** `policies/opa/terraform-security.rego`

**Checks:**
- S3 buckets are encrypted
- RDS instances use SSL
- Security groups not open to 0.0.0.0/0
- IAM policies follow least privilege

**Usage:**
```bash
opa eval -d policies/opa/terraform-security.rego \
         -i infrastructure/terraform/ \
         "data.terraform.deny"
```

---

### Kubernetes Security Policy
**File:** `policies/opa/k8s-security.rego`

**Checks:**
- Pods not running as root
- No privileged containers
- Resource limits defined
- Network policies exist

**Usage:**
```bash
opa eval -d policies/opa/k8s-security.rego \
         -i infrastructure/k8s/ \
         "data.kubernetes.deny"
```

---

## Secrets Management

### Vault Setup
**File:** `secrets-management/vault-setup.sh`

Sets up HashiCorp Vault for centralized secrets management:

```bash
cd secrets-management/
bash vault-setup.sh
```

**What it does:**
1. Installs Vault in Kubernetes
2. Configures Kubernetes auth backend
3. Creates secret paths for applications
4. Sets up dynamic database credentials

### Migrate Secrets
**File:** `secrets-management/secrets-migration.sh`

Migrates hardcoded secrets to Vault:

```bash
bash secrets-migration.sh /path/to/project
```

**Example integration:**
```python
# Before
db_password = "admin123"

# After
import hvac
vault_client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
db_password = vault_client.read('secret/data/db')['data']['data']['password']
```

---

## Usage Workflow

### Step 1: Apply Infrastructure Fixes
```bash
cd fixers/
bash fix-s3-encryption.sh ../../GP-PROJECTS/FINANCE-project/infrastructure/terraform
bash fix-rds-ssl.sh ../../GP-PROJECTS/FINANCE-project/infrastructure/terraform
bash fix-kubernetes-security.sh ../../GP-PROJECTS/FINANCE-project/infrastructure/k8s
```

### Step 2: Validate with OPA
```bash
cd ../policies/opa/
opa test . -v
```

### Step 3: Deploy Gatekeeper
```bash
cd ../../mutators/
bash deploy-gatekeeper.sh
kubectl apply -f gatekeeper-constraints/
```

### Step 4: Setup Secrets Management
```bash
cd ../secrets-management/
bash vault-setup.sh
bash secrets-migration.sh ../../GP-PROJECTS/FINANCE-project
```

---

## Validation

Re-scan infrastructure after hardening:

```bash
cd ../../1-Security-Assessment/cd-scanners/
python3 checkov_scanner.py --target ../../GP-PROJECTS/FINANCE-project/infrastructure/terraform
python3 trivy_scanner.py --mode config --target ../../GP-PROJECTS/FINANCE-project/infrastructure
```

---

**Next Phase:** [Phase 4: Cloud Migration](../4-Cloud-Migration/README.md) - Secure AWS deployment patterns
