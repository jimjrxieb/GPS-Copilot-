# Phase 1: Security Assessment

**Purpose:** Initial vulnerability discovery, risk analysis, and security baseline establishment

**When to use:** At the beginning of every engagement to understand the current security posture

---

## 🎯 Overview

Phase 1 provides comprehensive security scanning across three critical layers:

1. **CI Layer (Code)** - Find vulnerabilities in source code before commit
2. **CD Layer (Infrastructure)** - Validate IaC security before deployment
3. **Runtime Layer (Cloud)** - Assess live AWS security posture

**Clean, production-ready scanner suite with zero duplication.**

---

## 📁 Directory Structure (Clean)

```
1-Security-Assessment/
├── ci-scanners/                    # 5 files - Code-level security
│   ├── bandit_scanner.py           # Python SAST (CWE detection)
│   ├── semgrep_scanner.py          # Multi-language SAST
│   ├── gitleaks_scanner.py         # Hardcoded secrets detection
│   ├── BANDIT-README.md            # Bandit documentation
│   └── BANDIT-COMPLETION-REPORT.md # Production validation report
│
├── cd-scanners/                    # 6 files - Infrastructure security
│   ├── checkov_scanner.py          # IaC compliance (500+ checks)
│   ├── trivy_scanner.py            # Container & IaC vulnerabilities
│   ├── scan-iac.sh                 # Terraform/CloudFormation orchestrator
│   ├── scan-kubernetes.sh          # K8s manifest validation
│   ├── scan-opa-conftest.sh        # Pre-deployment policy gate
│   └── opa-policies/               # Rego policies for conftest
│       ├── network.rego            # Network security rules
│       ├── rbac.rego               # K8s RBAC validation
│       └── security.rego           # General security policies
│
├── runtime-scanners/               # 8 files - Cloud pattern validation
│   ├── cloud_patterns_scanner.py   # Validates 7 cloud security patterns
│   ├── ddos_validator.py           # DDoS resilience checks
│   ├── zero_trust_sg_validator.py  # Zero-trust networking
│   ├── query-aws-config.sh         # AWS Config compliance queries
│   ├── query-cloudtrail.sh         # CloudTrail event analysis
│   ├── query-cloudwatch.sh         # CloudWatch logs/metrics
│   ├── query-guardduty.sh          # GuardDuty findings
│   └── query-securityhub.sh        # Security Hub aggregation
│
└── tools/                          # 1 file - Orchestration
    └── run_all_scanners.py         # Multi-project batch scanner
```

**Total: 20 files in 4 directories** (cleaned from 34 files)

---

## 🚀 Quick Start

### Option 1: Use gp-security CLI (Recommended)

```bash
# Full assessment (all layers)
gp-security assess /path/to/project

# CI layer only (fast)
gp-security assess /path/to/project --ci

# CD layer only (IaC validation)
gp-security assess /path/to/project --cd

# Runtime layer only (cloud patterns)
gp-security assess /path/to/project --runtime
```

### Option 2: Run Individual Scanners

```bash
# CI Layer - Code Security
cd ci-scanners/
python3 bandit_scanner.py --target /path/to/project
python3 semgrep_scanner.py --target /path/to/project
python3 gitleaks_scanner.py --target /path/to/project

# CD Layer - Infrastructure Security
cd ../cd-scanners/
python3 checkov_scanner.py --target /path/to/project
python3 trivy_scanner.py --target /path/to/project
./scan-opa-conftest.sh  # Pre-deployment policy gate

# Runtime Layer - Cloud Security
cd ../runtime-scanners/
python3 cloud_patterns_scanner.py --target /path/to/project
./query-aws-config.sh
./query-cloudtrail.sh
```

---

## 🔍 Scanner Details

### CI Scanners (Code-Level Security)

| Scanner | Purpose | Technology | Severity Levels | CWE Mapping |
|---------|---------|------------|-----------------|-------------|
| **Bandit** | Python SAST | AST analysis | LOW, MEDIUM, HIGH | ✅ Full CWE |
| **Semgrep** | Multi-language SAST | Pattern matching | INFO, WARNING, ERROR | ✅ OWASP Top 10 |
| **Gitleaks** | Hardcoded secrets | Regex + entropy | CRITICAL only | ✅ CWE-798 |

**Detects:**
- SQL Injection (CWE-89)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- Hardcoded credentials (CWE-798)
- Insecure cryptography (CWE-327)
- 100+ other vulnerability patterns

**Output:** `GP-DATA/active/1-sec-assessment/ci-findings/{scanner}_{timestamp}.json`

---

### CD Scanners (Infrastructure Security)

| Scanner | Purpose | Coverage | Compliance |
|---------|---------|----------|------------|
| **Checkov** | IaC compliance | 500+ checks | PCI-DSS, HIPAA, CIS, NIST |
| **Trivy** | Container/IaC vulns | CVE + misconfigs | CRITICAL/HIGH CVEs |
| **OPA/Conftest** | Policy enforcement | Custom Rego | Pre-deployment gate |

**Orchestrators:**

1. **scan-iac.sh** - Terraform/CloudFormation validation
   - Runs Checkov + Trivy on IaC files
   - Blocks terraform apply if violations found

2. **scan-kubernetes.sh** - K8s manifest security
   - Validates deployments, services, pods
   - Checks RBAC, network policies, security contexts

3. **scan-opa-conftest.sh** - Pre-deployment policy gate
   - Uses centralized policies from Phase 3
   - Blocks deployment if policy violations exist
   - **Location:** `../../3-Hardening/policies/opa/`

**Policies validated:**
- Network security (isolation, egress)
- RBAC least privilege
- Pod security standards
- Resource limits
- Image security

**Output:** `GP-DATA/active/1-sec-assessment/cd-findings/{scanner}_{timestamp}.json`

---

### Runtime Scanners (Cloud Pattern Validation)

| Scanner | Purpose | AWS Services | Cost |
|---------|---------|--------------|------|
| **cloud_patterns_scanner.py** | Validates 7 patterns | VPC, SG, WAF, Shield | Varies |
| **ddos_validator.py** | DDoS resilience | Shield, WAF, CloudFront | $3K/mo |
| **zero_trust_sg_validator.py** | Zero-trust networking | Security Groups, NACLs | Free |

**AWS Query Scripts:**

1. **query-aws-config.sh** - Compliance queries
   - Retrieves AWS Config rules and compliance status
   - Checks resource configuration compliance

2. **query-cloudtrail.sh** - Audit log analysis
   - Recent API calls and security events
   - IAM changes, S3 access, console logins

3. **query-cloudwatch.sh** - Logs and metrics
   - Log groups and retention policies
   - Security-related metrics

4. **query-guardduty.sh** - Threat detection
   - Active GuardDuty findings
   - Severity breakdown

5. **query-securityhub.sh** - Security aggregation
   - Consolidated security findings
   - Compliance framework status

**7 Cloud Patterns Validated:**

| Pattern | Compliance | Cost | Purpose |
|---------|------------|------|---------|
| VPC Isolation | CIS 5.1-5.4 | $160/mo | Network segmentation |
| Zero-Trust SG | CIS 5.2-5.3 | Free | Least-privilege networking |
| Private Cloud Access | PCI-DSS 1.2 | Free | No direct internet |
| DDoS Resilience | NIST CSF PR.PT-5 | $3K/mo | Layer 3/4/7 protection |
| WAF Multi-Layer | OWASP Top 10 | $50/mo | Application firewall |
| Logging Everywhere | PCI-DSS 10.x | $100/mo | Audit trail |
| Data At Rest Encryption | PCI-DSS 3.4 | Free | KMS encryption |

**Output:** `GP-DATA/active/1-sec-assessment/runtime-findings/{scanner}_{timestamp}.json`

---

## 📊 Output Locations

All scan results follow standardized naming:

```
GP-DATA/active/1-sec-assessment/
├── ci-findings/
│   ├── bandit_20251014_153022.json
│   ├── semgrep_20251014_153045.json
│   └── gitleaks_20251014_153102.json
│
├── cd-findings/
│   ├── checkov_20251014_153130.json
│   ├── trivy_20251014_153215.json
│   └── conftest-security_20251014_153245.json
│
└── runtime-findings/
    ├── cloud-patterns_20251014_153310.json
    ├── aws-config_20251014_153330.json
    └── cloudtrail-events_20251014_153350.json
```

**Standardized JSON Format:**

```json
{
  "findings": [
    {
      "id": "scanner_1",
      "scanner": "bandit",
      "severity": "HIGH",
      "cwe": ["CWE-89"],
      "title": "SQL Injection vulnerability",
      "description": "User input used in SQL query without sanitization",
      "file": "backend/api/users.py",
      "line": 42,
      "recommendation": "Use parameterized queries or ORM",
      "compliance_impact": ["PCI-DSS 6.5.1", "OWASP A03:2021"]
    }
  ],
  "metadata": {
    "scanner": "bandit",
    "scan_timestamp": "2025-10-14T15:30:22Z",
    "target": "/path/to/project",
    "issue_count": 1,
    "severity_breakdown": {
      "CRITICAL": 0,
      "HIGH": 1,
      "MEDIUM": 0,
      "LOW": 0
    }
  }
}
```

---

## 🔗 Integration with Later Phases

### → Phase 2: App-Sec-Fixes
**Input:** CI findings (bandit, semgrep, gitleaks)
**Purpose:** Fix code-level vulnerabilities
**Priority:** CRITICAL → HIGH → MEDIUM

```bash
# After Phase 1 CI scan
cd ../2-App-Sec-Fixes/fixers/
./fix-hardcoded-secrets.sh /path/to/project
python3 sql_injection_fixer.py --findings ../../GP-DATA/active/1-sec-assessment/ci-findings/
```

### → Phase 3: Hardening
**Input:** CD findings (checkov, trivy, OPA)
**Purpose:** Secure infrastructure configurations
**Applies:** Runtime enforcement (Gatekeeper)

```bash
# After Phase 1 CD scan
cd ../3-Hardening/fixers/
./fix-kubernetes-security.sh /path/to/project
kubectl apply -f ../policies/gatekeeper/  # Runtime enforcement
```

### → Phase 5: Compliance-Audit
**Input:** All Phase 1 findings (CI + CD + Runtime)
**Purpose:** Generate compliance reports, track remediation

```bash
# After complete Phase 1 assessment
cd ../5-Compliance-Audit/validators/
python3 compare-results.py --before GP-DATA/active/1-sec-assessment/ --after GP-DATA/active/3-hardening/
./generate-compliance-report.sh --framework pci-dss
```

### → Phase 6: Auto-Agents
**Input:** Phase 1 scanner outputs
**Purpose:** Continuous security automation

```bash
# Automated scanning in CI/CD
cd ../6-Auto-Agents/cicd-templates/github-actions/
cat security-scan.yml  # Uses Phase 1 scanners in GitHub Actions
```

---

## 🎯 Best Practices

### 1. Always Run Phase 1 First
Establishes security baseline for all subsequent work.

### 2. Run All Three Layers
- **CI** - Catches issues before commit
- **CD** - Validates before deployment
- **Runtime** - Verifies live environment

### 3. Save All Results
Required for before/after comparison and compliance evidence.

### 4. Re-scan After Fixes
**Phase 1 → Phase 2 → Phase 1 again** to verify remediation.

### 5. Use OPA Pre-Deployment Gate
`scan-opa-conftest.sh` blocks deployments with policy violations.

### 6. Document False Positives
Create `.gitleaks.toml`, `.bandit`, `.semgrepignore` files.

### 7. Automate with gp-security
```bash
# Complete workflow
gp-security workflow /path/to/project
```

---

## 🛠️ Troubleshooting

### Scanner Not Found

**Problem:** `gitleaks: command not found`

**Solution:**
```bash
# Check GP-copilot binaries
ls ~/linkops-industries/GP-copilot/bin/

# Or install
# Gitleaks
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
tar -xzf gitleaks*.tar.gz && sudo mv gitleaks /usr/local/bin/

# Conftest
wget https://github.com/open-policy-agent/conftest/releases/download/v0.45.0/conftest_0.45.0_Linux_x86_64.tar.gz
tar -xzf conftest*.tar.gz && sudo mv conftest /usr/local/bin/
```

### Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'base_scanner'`

**Solution:**
```bash
# Check shared library path
export PYTHONPATH=/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/shared-library/base-classes:$PYTHONPATH

# Or run from GP-CONSULTING root
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING
python3 1-Security-Assessment/ci-scanners/bandit_scanner.py --target GP-PROJECTS/FINANCE-project
```

### OPA Policies Not Found

**Problem:** `ERROR: OPA policy directory not found`

**Solution:**
```bash
# OPA policies are in Phase 3 (centralized)
ls -la /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/3-Hardening/policies/opa/

# Conftest auto-detects Phase 3 policies
cd cd-scanners/
./scan-opa-conftest.sh  # Uses ../../3-Hardening/policies/opa/
```

### No Output Files

**Problem:** Scan runs but no JSON files created

**Solution:**
```bash
# Check GP-DATA directory exists
mkdir -p ~/linkops-industries/GP-copilot/GP-DATA/active/1-sec-assessment/{ci-findings,cd-findings,runtime-findings}

# Run with verbose mode
python3 bandit_scanner.py --target /path/to/project --verbose
```

---

## 📖 Example: Complete Phase 1 Assessment

```bash
# Set up environment
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/1-Security-Assessment
export TARGET="/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project"

# Step 1: CI Layer (Code Security)
echo "→ Scanning code-level security..."
cd ci-scanners/
python3 bandit_scanner.py --target "$TARGET"
python3 semgrep_scanner.py --target "$TARGET"
python3 gitleaks_scanner.py --target "$TARGET"

# Step 2: CD Layer (Infrastructure Security)
echo "→ Scanning infrastructure security..."
cd ../cd-scanners/
python3 checkov_scanner.py --target "$TARGET"
python3 trivy_scanner.py --target "$TARGET"
./scan-opa-conftest.sh  # Pre-deployment gate

# Step 3: Runtime Layer (Cloud Patterns)
echo "→ Scanning cloud security patterns..."
cd ../runtime-scanners/
python3 cloud_patterns_scanner.py --target "$TARGET"
./query-aws-config.sh
./query-cloudtrail.sh
./query-guardduty.sh

# Step 4: Review Results
echo "→ Assessment complete!"
ls -lh ~/linkops-industries/GP-copilot/GP-DATA/active/1-sec-assessment/*/

# Step 5: Proceed to Phase 2
echo "→ Next: Fix code vulnerabilities in Phase 2"
cd ../../2-App-Sec-Fixes/
```

---

## 🔐 Security Notes

### Secrets in Output Files

- **Gitleaks masks secrets** in output (first 4 + last 4 chars only)
- **Never commit findings** to git (add `GP-DATA/` to `.gitignore`)
- **Restrict findings access** (contains sensitive security info)

### AWS Credentials

Runtime scanners require AWS credentials:

```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_REGION="us-east-1"

# Option 2: AWS CLI profile
aws configure --profile security-scanner
export AWS_PROFILE=security-scanner

# Option 3: IAM role (recommended for EC2/ECS)
# No credentials needed - uses instance metadata
```

**Required IAM permissions:**
- `config:DescribeConfigRules`
- `cloudtrail:LookupEvents`
- `guardduty:ListFindings`
- `securityhub:GetFindings`
- `cloudwatch:DescribeLogGroups`

---

## 📚 Additional Documentation

- **[Bandit Scanner Deep Dive](ci-scanners/BANDIT-README.md)** - CWE mappings, severity levels
- **[Bandit Production Validation](ci-scanners/BANDIT-COMPLETION-REPORT.md)** - Test results
- **[OPA Policy Reference](cd-scanners/opa-policies/)** - Rego policy documentation
- **[Cloud Patterns Guide](../3-Hardening/cloud-patterns/)** - 7 security patterns

---

## 🔄 Next Phase

Once Phase 1 assessment is complete with findings saved:

**→ [Phase 2: App-Sec-Fixes](../2-App-Sec-Fixes/README.md)** - Fix code-level vulnerabilities discovered in CI scans

**→ [Phase 3: Hardening](../3-Hardening/README.md)** - Secure infrastructure based on CD/Runtime findings

**→ [Phase 5: Compliance-Audit](../5-Compliance-Audit/README.md)** - Generate compliance reports from all findings

---

**Phase 1 Version:** 2.0 (Clean)
**Last Updated:** 2025-10-14
**Files:** 20 (cleaned from 34)
**Status:** ✅ Production-Ready
