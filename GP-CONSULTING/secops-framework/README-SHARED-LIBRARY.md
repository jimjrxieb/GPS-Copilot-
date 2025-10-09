# SecOps Framework - Shared Library

## Overview
Centralized security operations framework used across all GP-Copilot projects. This shared library eliminates code duplication and provides consistent security scanning, compliance mapping, and remediation across FINANCE, HEALTHCARE, and DEFENSE projects.

## Architecture

```
GP-CONSULTING/
├── secops-framework/          # Shared SecOps library (THIS)
│   ├── 1-scanners/           # Security scanners
│   ├── 2-findings/           # Aggregation & compliance mapping
│   ├── 3-fixers/             # Auto-fixers & manual guides
│   ├── 4-mutators/           # OPA policies & K8s webhooks
│   ├── 5-validators/         # Before/after validation
│   ├── 6-reports/            # Compliance reports
│   └── run-secops.sh         # Main orchestrator
│
└── GP-POL-AS-CODE/
    └── cloud-security-patterns/   # Terraform + OPA patterns
        ├── vpc-isolation/
        ├── zero-trust-sg/
        ├── private-cloud-access/
        └── ...

GP-PROJECTS/
├── FINANCE-project/
│   ├── secops -> ../../GP-CONSULTING/secops-framework/  # Symlink
│   ├── policies -> ../../GP-CONSULTING/GP-POL-AS-CODE/  # Symlink
│   └── secops-config.yaml    # Project-specific config
│
├── HEALTHCARE-project/
│   ├── secops -> ../../GP-CONSULTING/secops-framework/
│   ├── policies -> ../../GP-CONSULTING/GP-POL-AS-CODE/
│   └── secops-config.yaml
│
└── DEFENSE-project/
    ├── secops -> ../../GP-CONSULTING/secops-framework/
    ├── policies -> ../../GP-CONSULTING/GP-POL-AS-CODE/
    └── secops-config.yaml
```

## Usage

### From Any Project

```bash
cd GP-PROJECTS/FINANCE-project/

# Run SecOps with project config
./secops/run-secops-with-config.sh

# Or use original runner
./secops/run-secops.sh
```

### Project Configuration

Each project has a `secops-config.yaml` that defines:

**FINANCE (PCI-DSS):**
```yaml
project:
  name: "SecureBank"
  industry: "financial-services"
  compliance_frameworks: ["PCI-DSS-3.2.1", "SOC2-Type-II"]

policies:
  opa_policies:
    - "cloud-security-patterns/vpc-isolation"
    - "cloud-security-patterns/zero-trust-sg"
    - "compliance-frameworks/pci-dss"
```

**HEALTHCARE (HIPAA):**
```yaml
project:
  name: "HealthVault"
  industry: "healthcare"
  compliance_frameworks: ["HIPAA", "HITECH"]

policies:
  opa_policies:
    - "cloud-security-patterns/vpc-isolation"
    - "cloud-security-patterns/private-cloud-access"  # No internet egress
    - "compliance-frameworks/hipaa"

encryption:
  require_kms: true  # HIPAA requirement
```

**DEFENSE (FedRAMP):**
```yaml
project:
  name: "TacticalNet"
  industry: "defense"
  compliance_frameworks: ["FedRAMP-Moderate", "CMMC-Level-3"]

policies:
  opa_policies:
    - "cloud-security-patterns/incident-evidence"
    - "compliance-frameworks/fedramp"

  air_gapped: true
  use_local_llm: true

aws:
  cloud: "govcloud"
  region: "us-gov-west-1"
```

## Benefits

### 1. Code Reusability (DRY Principle)
- **Before:** 3 copies of SecOps framework (one per project)
- **After:** 1 shared library, 3 symlinks
- **Maintenance:** Fix once, applies to all projects

### 2. Industry-Specific Compliance
- **FINANCE:** PCI-DSS focused (payment card security)
- **HEALTHCARE:** HIPAA focused (PHI protection, no internet egress)
- **DEFENSE:** FedRAMP focused (GovCloud, air-gapped, zero-tolerance)

### 3. Cloud Security Patterns
- 7 production-ready Terraform patterns
- OPA enforcement policies
- Compliance mappings (CIS, PCI-DSS, HIPAA, FedRAMP)

### 4. Consistent Scanning
- Same scanners across all projects
- Project-specific thresholds
- Unified reporting

## Security Scanners

| Scanner | Language/Type | Compliance |
|---------|--------------|------------|
| tfsec | Terraform | CIS, PCI-DSS |
| Checkov | Terraform/K8s | CIS, HIPAA, SOC2 |
| Bandit | Python SAST | OWASP Top 10 |
| Trivy | Container CVE | PCI-DSS 6.2 |
| Gitleaks | Secret detection | PCI-DSS 8.2.1 |
| Semgrep | Multi-language SAST | OWASP, CWE |
| OPA | Policy-as-code | Custom compliance |

## Cloud Security Patterns

See [cloud-security-patterns/README.md](../GP-POL-AS-CODE/cloud-security-patterns/README.md) for details.

| Pattern | Flashcard | Cost |
|---------|-----------|------|
| VPC Isolation | Multi-AZ VPC with public/private subnets | ~$160/mo |
| Zero-Trust SG | SG referencing SG (no 0.0.0.0/0) | Free |
| Private Cloud Access | S3/DynamoDB via VPC Endpoint | ~$7/mo |
| Centralized Egress | NAT Gateway + Egress Firewall | ~$350/mo |
| DDoS Resilience | CloudFront + Shield Advanced | ~$3,000/mo |
| Visibility | VPC Flow Logs + GuardDuty | ~$250/mo |
| Incident Evidence | Archive Flow Logs with SHA256 | ~$5/mo |

## Workflow

```
1. AUDIT    → Run 7 security scanners
2. REPORT   → Aggregate findings, map to compliance
3. FIX      → Auto-fixers + manual guides
4. MUTATE   → OPA policies prevent future violations
5. VALIDATE → Compare before/after
6. DOCUMENT → Executive summary + compliance reports
```

## Time Savings

- **Manual audit:** 13 hours
- **Automated audit:** 40 minutes
- **Savings:** 95% time reduction
- **ROI:** $4,933 per engagement

## Updating the Shared Library

Changes to the shared library automatically apply to all projects via symlinks:

```bash
cd GP-CONSULTING/secops-framework/

# Update scanner
vim 1-scanners/scan-iac.sh

# Update applies to FINANCE, HEALTHCARE, DEFENSE immediately
# No need to update each project separately
```

## Testing

```bash
# Test in FINANCE project
cd GP-PROJECTS/FINANCE-project/
./secops/run-secops.sh

# Test in HEALTHCARE project
cd ../HEALTHCARE-project/
./secops/run-secops.sh

# Test in DEFENSE project
cd ../DEFENSE-project/
./secops/run-secops.sh
```

## Support

- **Framework docs:** [README.md](README.md) (original)
- **Pattern docs:** [cloud-security-patterns/README.md](../GP-POL-AS-CODE/cloud-security-patterns/README.md)
- **Issues:** Open GitHub issue
- **Compliance questions:** See pattern `compliance-mapping.md` files
