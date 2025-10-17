# GP-CONSULTING: Phase-Based Security Engagement Framework

**Organized by client engagement workflow - From assessment to automation**

---

## 🎯 Framework Overview

```
CLIENT ENGAGEMENT PHASES:
1. Assessment    → Discover vulnerabilities (scanners)
2. App Fixes     → Fix code-level issues (CI fixers)
3. Hardening     → Secure infrastructure (CD fixers + policies)
4. Cloud Migration → Move to AWS securely (Terraform)
5. Compliance    → Validate and report (audits)
6. Automation    → Continuous security (AI agents)
```

---

## 📁 Directory Structure Tags And Labels


```
GP-CONSULTING/
├── 1-Security-Assessment/     # Phase 1: Vulnerability discovery
│   ├── ci-scanners/           # Bandit, Semgrep, Gitleaks
│   ├── cd-scanners/           # Checkov, Trivy
│   └── runtime-scanners/      # AWS Config, CloudTrail
│
├── 2-App-Sec-Fixes/           # Phase 2: Application security fixes
│   ├── fixers/                # CI-level auto-fixers
│   ├── remediation/           # Fix recommendations database
│   └── validation/            # Verify fixes work
│
├── 3-Hardening/               # Phase 3: Infrastructure hardening
│   ├── fixers/                # CD-level auto-fixers
│   ├── mutators/              # Gatekeeper admission control
│   ├── policies/              # Centralized security policies (used by all phases)
│   │   ├── opa/               # 12 OPA/Rego enforcement policies
│   │   ├── gatekeeper/        # Kubernetes admission control
│   │   └── securebank/        # PCI-DSS policy suite
│   └── secrets-management/    # Vault, Secrets Manager integration
│
├── 4-Cloud-Migration/         # Phase 4: AWS migration
│   ├── terraform-modules/     # Secure Terraform modules
│   ├── migration-scripts/     # Migration automation
│   └── templates/             # AWS security patterns
│
├── 5-Compliance-Audit/        # Phase 5: Compliance validation
│   ├── validators/            # Before/after comparison
│   ├── reports/               # Compliance report generators
│   ├── frameworks/            # PCI-DSS, HIPAA, NIST mappings
│   └── standards/             # GuidePoint security standards
│
├── 6-Auto-Agents/             # Phase 6: Continuous automation
│   ├── agents/                # 14 AI agents
│   ├── workflows/             # Orchestration
│   ├── cicd-templates/        # GitHub Actions, GitLab CI
│   └── monitoring/            # Alerting and incident response
│
└── shared-library/            # Shared code across phases
    ├── base-classes/          # Scanner/Fixer base classes
    ├── utils/                 # Helper functions
    └── configs/               # Shared configurations
```

---

## 🚀 Quick Start Example: FINANCE Project

```bash
# Phase 1: Assessment
cd 1-Security-Assessment/ci-scanners/
python3 bandit_scanner.py --target GP-PROJECTS/FINANCE-project

# Phase 2: Fix Application Code
cd ../../2-App-Sec-Fixes/fixers/
bash fix-hardcoded-secrets.sh GP-PROJECTS/FINANCE-project

# Phase 3: Harden Infrastructure
cd ../../3-Hardening/fixers/
bash fix-kubernetes-security.sh GP-PROJECTS/FINANCE-project

# Phase 5: Generate Compliance Report
cd ../../5-Compliance-Audit/reports/
python3 generate_compliance_report.py --framework pci-dss
```

---

## 🔒 Centralized Security Policies (Phase 3)

**Phase 3 contains centralized enforcement policies** referenced across all phases:

```
3-Hardening/policies/
├── opa/               # 12 OPA/Rego policies - Used by Phases 1,3,4,5,6
├── gatekeeper/        # Kubernetes admission control - Phase 3 deployment
└── securebank/        # PCI-DSS policy suite - SecureBank project
```

### Multi-Phase Policy Usage

| Phase | OPA Usage | Purpose |
|-------|-----------|---------|
| **Phase 1** | Scanner (read policies) | Discover policy violations in IaC |
| **Phase 3** | Enforcer (deploy policies) | Block non-compliant deployments |
| **Phase 4** | Validator (pre-deploy) | Validate AWS resources before apply |
| **Phase 5** | Evidence generator | Prove compliance with audit trail |
| **Phase 6** | CI/CD automation | Continuous policy enforcement |

**Example: Same policies, different purposes**

```bash
# Phase 1: OPA discovers violations (scanning)
cd 1-Security-Assessment/cd-scanners
./scan-opa-conftest.sh  # Uses: ../../3-Hardening/policies/opa/

# Phase 3: OPA blocks violations (enforcement)
kubectl apply -f 3-Hardening/policies/gatekeeper/

# Phase 5: OPA proves compliance (evidence)
cd 5-Compliance-Audit
./compliance_validator.py --policies ../3-Hardening/policies/opa/

# Phase 6: OPA in CI/CD (automation)
conftest test terraform/ --policy 3-Hardening/policies/opa/
```

**See**: [3-Hardening/README.md#centralized-security-policies](3-Hardening/README.md#centralized-security-policies) for complete policy documentation

---

## 📚 Phase Documentation

- [Phase 1: Security Assessment](1-Security-Assessment/README.md)
- [Phase 2: App Security Fixes](2-App-Sec-Fixes/README.md)
- [Phase 3: Hardening](3-Hardening/README.md)
- [Phase 4: Cloud Migration](4-Cloud-Migration/README.md)
- [Phase 5: Compliance Audit](5-Compliance-Audit/README.md)
- [Phase 6: Auto-Agents](6-Auto-Agents/README.md)

---

**Framework Version:** 2.0 (Phase-Based)
**Last Updated:** 2025-10-14
