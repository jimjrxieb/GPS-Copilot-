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

## 📁 Directory Structure with Tags & Labels

### **Legend:**
- 🔍 **[SCAN]** = Discovers issues (read-only, no modifications)
- 🔧 **[FIX]** = Remediates issues (writes/modifies files)
- 📋 **[POLICY]** = Policy definitions (OPA .rego files, Gatekeeper constraints)
- 🛡️ **[ENFORCE]** = Policy enforcement (deploys/enables policies)
- 📊 **[REPORT]** = Generates documentation/reports
- 🤖 **[AGENT]** = AI-driven automation
- 🔄 **[WORKFLOW]** = Orchestration/multi-tool execution
- 📚 **[LIBRARY]** = Reusable code/configs

---
```
GP-CONSULTING/
│
├── 1-Security-Assessment/              # Phase 1: Vulnerability Discovery
│   │
│   ├── ci-scanners/                    # 🔍 [SCAN] Code-level security
│   │   ├── bandit_scanner.py          # 🔍 [SCAN] Python SAST
│   │   ├── semgrep_scanner.py         # 🔍 [SCAN] Multi-language SAST
│   │   ├── gitleaks_scanner.py        # 🔍 [SCAN] Secrets detection
│   │   └── quality/                   # 🔍 [SCAN] Code quality (pylint, flake8)
│   │
│   ├── cd-scanners/                    # 🔍 [SCAN] Infrastructure security
│   │   ├── checkov_scanner.py         # 🔍 [SCAN] IaC security (Terraform, K8s)
│   │   ├── trivy_scanner.py           # 🔍 [SCAN] Container/config vulnerabilities
│   │   └── tfsec_scanner.py           # 🔍 [SCAN] Terraform-specific security
│   │
│   ├── opa-scanners/                   # 🔍 [SCAN] Policy violation detection
│   │   ├── opa_scanner.py             # 🔍 [SCAN] OPA policy evaluation
│   │   ├── conftest_gate_agent.py     # 🔍 [SCAN] Conftest wrapper
│   │   └── scan-policies/             # 📋 [POLICY] Policies used for scanning
│   │       ├── terraform-scan.rego    # 📋 [POLICY] Terraform validation
│   │       ├── kubernetes-scan.rego   # 📋 [POLICY] K8s manifest validation
│   │       └── docker-scan.rego       # 📋 [POLICY] Dockerfile validation
│   │
│   ├── runtime-scanners/               # 🔍 [SCAN] Live system security
│   │   ├── query-aws-config.sh        # 🔍 [SCAN] AWS Config compliance
│   │   ├── query-cloudtrail.sh        # 🔍 [SCAN] CloudTrail audit logs
│   │   └── query-guardduty.sh         # 🔍 [SCAN] GuardDuty threat detection
│   │
│   ├── tools/                          # 🔄 [WORKFLOW] Orchestration
│   │   ├── run-all-scanners.sh        # 🔄 [WORKFLOW] Run all Phase 1 scanners
│   │   └── generate-assessment-report.py # 📊 [REPORT] Assessment summary
│   │
│   └── README.md                       # Documentation
│
├── 2-App-Sec-Fixes/                    # Phase 2: Application-Level Fixes
│   │
│   ├── fixers/                         # 🔧 [FIX] CI-level auto-fixers
│   │   ├── fix-hardcoded-secrets.sh   # 🔧 [FIX] Remove secrets from code
│   │   ├── fix-sql-injection.sh       # 🔧 [FIX] Parameterized queries
│   │   └── manual/                    # 📊 [REPORT] Manual fix guides
│   │       └── FIX-HARDCODED-SECRETS.md
│   │
│   ├── remediation/                    # 📚 [LIBRARY] Fix recommendation DB
│   │   ├── remediation_db.py          # 📚 [LIBRARY] Fix pattern database
│   │   └── security_advisor.py        # 🤖 [AGENT] Fix recommendations
│   │
│   └── validation/                     # 🔍 [SCAN] Verify fixes work
│       └── test-fixes.py              # 🔍 [SCAN] Post-fix validation
│
├── 3-Hardening/                        # Phase 3: Infrastructure Hardening
│   │
│   ├── fixers/                         # 🔧 [FIX] CD-level auto-fixers
│   │   ├── fix-kubernetes-security.sh # 🔧 [FIX] K8s security hardening
│   │   ├── fix-s3-encryption.sh       # 🔧 [FIX] S3 encryption
│   │   ├── fix-security-groups.sh     # 🔧 [FIX] AWS security groups
│   │   └── fix-iam-wildcards.sh       # 🔧 [FIX] IAM least privilege
│   │
│   ├── policies/                       # 📋 [POLICY] Policy definitions
│   │   │
│   │   ├── opa/                        # 📋 [POLICY] OPA policy files
│   │   │   ├── kubernetes.rego        # 📋 [POLICY] K8s admission policies
│   │   │   ├── terraform-security.rego # 📋 [POLICY] Terraform validation
│   │   │   ├── network.rego           # 📋 [POLICY] Network policies
│   │   │   ├── secrets-management.rego # 📋 [POLICY] Secrets handling
│   │   │   ├── rbac.rego              # 📋 [POLICY] RBAC policies
│   │   │   └── image-security.rego    # 📋 [POLICY] Container image policies
│   │   │
│   │   └── gatekeeper/                 # 📋 [POLICY] Gatekeeper K8s policies
│   │       ├── templates/             # 📋 [POLICY] Constraint templates
│   │       │   └── pod-security-template.yaml
│   │       └── constraints/           # 📋 [POLICY] Constraint instances
│   │           └── production/
│   │               └── pod-security-constraint.yaml
│   │
│   ├── opa-fixers/                     # 🔧 [FIX] OPA-based auto-remediation
│   │   ├── opa_fixer.py               # 🔧 [FIX] Apply fixes from OPA violations
│   │   └── opa_policy_generator.py    # 🔧 [FIX] Generate policies from violations
│   │
│   ├── mutators/                       # 🛡️ [ENFORCE] Policy enforcement
│   │   ├── deploy-gatekeeper.sh       # 🛡️ [ENFORCE] Install Gatekeeper to cluster
│   │   ├── enable-gatekeeper-enforcement.sh # 🛡️ [ENFORCE] Switch to deny mode
│   │   └── gatekeeper-constraints/    # 📋 [POLICY] Enforcement configs
│   │       ├── opa-gatekeeper.yaml    # 📋 [POLICY] Gatekeeper deployment
│   │       └── mutations.yaml         # 🛡️ [ENFORCE] Auto-mutations
│   │
│   └── secrets-management/             # 🔧 [FIX] Secrets handling
│       └── migrate-to-vault.sh        # 🔧 [FIX] Vault migration
│
├── 4-Cloud-Migration/                  # Phase 4: AWS Migration
│   │
│   ├── terraform-modules/              # 📋 [POLICY] Infrastructure templates
│   │   ├── secure-vpc/                # 📋 [POLICY] VPC security template
│   │   ├── secure-rds/                # 📋 [POLICY] RDS security template
│   │   └── secure-s3/                 # 📋 [POLICY] S3 security template
│   │
│   ├── migration-scripts/              # 🔧 [FIX] Migration automation
│   │   ├── migrate-database.sh        # 🔧 [FIX] DB migration
│   │   └── migrate-to-s3.sh           # 🔧 [FIX] File migration
│   │
│   ├── aws-fixers/                     # 🔧 [FIX] Cloud-specific fixes
│   │   └── fix-aws-misconfigurations.sh # 🔧 [FIX] AWS security fixes
│   │
│   └── templates/                      # 📋 [POLICY] AWS patterns
│       └── cloudformation/            # 📋 [POLICY] CloudFormation templates
│
├── 5-Compliance-Audit/                 # Phase 5: Compliance Validation
│   │
│   ├── validators/                     # 🔍 [SCAN] Compliance validation
│   │   ├── compare-results.py         # 📊 [REPORT] Before/after comparison
│   │   └── validate-all.sh            # 🔍 [SCAN] Full compliance scan
│   │
│   ├── reports/                        # 📊 [REPORT] Report generation
│   │   ├── generators/                # 📊 [REPORT] Report generators
│   │   │   └── generate_compliance_report.py
│   │   └── templates/                 # 📊 [REPORT] Report templates
│   │
│   ├── frameworks/                     # 📋 [POLICY] Compliance mappings
│   │   ├── pci-dss/                   # 📋 [POLICY] PCI-DSS controls
│   │   ├── hipaa/                     # 📋 [POLICY] HIPAA controls
│   │   └── nist-800-53/               # 📋 [POLICY] NIST controls
│   │
│   ├── standards/                      # 📋 [POLICY] GuidePoint standards
│   │   ├── opa-policies/              # 📋 [POLICY] GuidePoint OPA policies
│   │   └── terraform-modules/         # 📋 [POLICY] GuidePoint Terraform modules
│   │
│   └── evidence/                       # 📊 [REPORT] Audit evidence
│       └── collect-evidence.sh        # 📊 [REPORT] Evidence collection
│
├── 6-Auto-Agents/                      # Phase 6: Continuous Automation
│   │
│   ├── agents/                         # 🤖 [AGENT] AI automation
│   │   ├── cka_agent.py               # 🤖 [AGENT] CKA specialist
│   │   ├── cks_agent.py               # 🤖 [AGENT] CKS specialist
│   │   ├── iac_agent.py               # 🤖 [AGENT] IaC specialist
│   │   └── policy-agents/             # 🤖 [AGENT] Policy automation
│   │       ├── gatekeeper_audit_agent.py # 🤖 [AGENT] Continuous K8s audit
│   │       ├── conftest_gate_agent.py    # 🤖 [AGENT] Conftest automation
│   │       └── opa_enforcement_agent.py  # 🤖 [AGENT] OPA continuous enforcement
│   │
│   ├── workflows/                      # 🔄 [WORKFLOW] Orchestration
│   │   ├── agentic_orchestrator.py    # 🔄 [WORKFLOW] Multi-agent coordination
│   │   ├── scan_workflow.py           # 🔄 [WORKFLOW] Automated scanning
│   │   └── fix_workflow.py            # 🔄 [WORKFLOW] Automated remediation
│   │
│   ├── cicd-templates/                 # 🛡️ [ENFORCE] Pipeline integration
│   │   ├── github-actions/            # 🛡️ [ENFORCE] GitHub Actions workflows
│   │   │   └── security-pipeline.yml
│   │   └── gitlab-ci/                 # 🛡️ [ENFORCE] GitLab CI configs
│   │
│   ├── monitoring/                     # 🔍 [SCAN] Continuous monitoring
│   │   └── scheduled-scans.sh         # 🔍 [SCAN] Weekly security scans
│   │
│   └── incident-response/              # 🔧 [FIX] Automated IR
│       └── auto-isolate.sh            # 🔧 [FIX] Isolate compromised resources
│
└── shared-library/                     # Shared Code
    │
    ├── base-classes/                   # 📚 [LIBRARY] Inheritance
    │   ├── base_scanner.py            # 📚 [LIBRARY] Scanner base class
    │   └── base_fixer.py              # 📚 [LIBRARY] Fixer base class
    │
    ├── utils/                          # 📚 [LIBRARY] Helpers
    │   └── file_utils.py              # 📚 [LIBRARY] File operations
    │
    └── configs/                        # 📚 [LIBRARY] Shared configs
        └── scanners-config.yaml       # 📚 [LIBRARY] Scanner settings
```

---

## 🏷️ Tag Reference Guide

### When to Use Each Tag:

| Tag | Purpose | Creates Files? | Modifies Files? | Example |
|-----|---------|----------------|-----------------|---------|
| 🔍 **[SCAN]** | Discovers issues | No | No (read-only) | `bandit_scanner.py`, `opa_scanner.py` |
| 🔧 **[FIX]** | Remediates issues | Sometimes | Yes (writes/patches) | `fix-hardcoded-secrets.sh`, `opa_fixer.py` |
| 📋 **[POLICY]** | Policy definitions | Yes (policy files) | No (just defines rules) | `kubernetes.rego`, `pod-security-template.yaml` |
| 🛡️ **[ENFORCE]** | Deploys/enables policies | No | Yes (applies configs) | `deploy-gatekeeper.sh`, `enable-enforcement.sh` |
| 📊 **[REPORT]** | Generates docs | Yes (reports) | No (read-only input) | `generate_compliance_report.py` |
| 🤖 **[AGENT]** | AI-driven | Depends | Depends | `gatekeeper_audit_agent.py` |
| 🔄 **[WORKFLOW]** | Orchestrates tools | No | No (calls other tools) | `run-all-scanners.sh` |
| 📚 **[LIBRARY]** | Reusable code | No | No (imported by others) | `base_scanner.py`, `file_utils.py` |

---

## 📍 Where Does OPA Go? (Decision Tree)

### **Question 1: What are you doing with OPA?**

#### ✅ **"I'm scanning for policy violations"**
→ **Location:** `1-Security-Assessment/opa-scanners/`
→ **Tag:** 🔍 **[SCAN]**
→ **Files:** `opa_scanner.py`, `conftest_gate_agent.py`

#### ✅ **"I'm writing/storing policy files (.rego)"**
→ **Location:** `3-Hardening/policies/opa/`
→ **Tag:** 📋 **[POLICY]**
→ **Files:** `kubernetes.rego`, `terraform-security.rego`

#### ✅ **"I'm fixing resources to comply with policies"**
→ **Location:** `3-Hardening/opa-fixers/`
→ **Tag:** 🔧 **[FIX]**
→ **Files:** `opa_fixer.py`, `opa_policy_generator.py`

#### ✅ **"I'm deploying Gatekeeper to enforce policies"**
→ **Location:** `3-Hardening/mutators/`
→ **Tag:** 🛡️ **[ENFORCE]**
→ **Files:** `deploy-gatekeeper.sh`, `enable-gatekeeper-enforcement.sh`

#### ✅ **"I'm running continuous OPA audits (automation)"**
→ **Location:** `6-Auto-Agents/agents/policy-agents/`
→ **Tag:** 🤖 **[AGENT]**
→ **Files:** `gatekeeper_audit_agent.py`, `opa_enforcement_agent.py`

#### ✅ **"I'm using OPA results in compliance reports"**
→ **Location:** `5-Compliance-Audit/validators/` (reads from Phase 1/3)
→ **Tag:** 📊 **[REPORT]**
→ **Files:** `compare-results.py`, `generate_compliance_report.py`

---

## 🔄 OPA/Gatekeeper Workflow Across Phases
```
Phase 1: Assessment
├─ 🔍 [SCAN] opa_scanner.py
│   └─ Reads: 3-Hardening/policies/opa/*.rego
│   └─ Outputs: GP-DATA/active/findings/FINANCE/opa_violations.json
│
Phase 3: Hardening
├─ 📋 [POLICY] kubernetes.rego (stored here)
├─ 🔧 [FIX] opa_fixer.py
│   └─ Reads: GP-DATA/active/findings/FINANCE/opa_violations.json
│   └─ Applies fixes to: FINANCE-project/kubernetes/*.yaml
├─ 🛡️ [ENFORCE] deploy-gatekeeper.sh
│   └─ Deploys: 3-Hardening/policies/gatekeeper/ → Kubernetes cluster
│
Phase 5: Compliance
├─ 📊 [REPORT] generate_compliance_report.py
│   └─ Reads: GP-DATA/active/findings/FINANCE/opa_violations.json (before)
│   └─ Reads: GP-DATA/active/findings/FINANCE/opa_post_fix.json (after)
│   └─ Outputs: Compliance report showing 0 violations
│
Phase 6: Automation
├─ 🤖 [AGENT] gatekeeper_audit_agent.py
│   └─ Runs: Weekly Gatekeeper audit
│   └─ Outputs: Email report to security team
```

---

## 🎯 Quick Decision Guide

**"Where do I put this new OPA thing?"**

1. **Is it a `.rego` file?**
   → `3-Hardening/policies/opa/`

2. **Does it scan/detect violations?**
   → `1-Security-Assessment/opa-scanners/`

3. **Does it fix violations?**
   → `3-Hardening/opa-fixers/`

4. **Does it deploy Gatekeeper?**
   → `3-Hardening/mutators/`

5. **Does it run continuously/automatically?**
   → `6-Auto-Agents/agents/policy-agents/`

6. **Does it generate reports?**
   → `5-Compliance-Audit/` (reads OPA data from other phases)

---

## 📚 Phase Documentation

- [Phase 1: Security Assessment](1-Security-Assessment/README.md) - 🔍 Scanners only
- [Phase 2: App Security Fixes](2-App-Sec-Fixes/README.md) - 🔧 CI fixers only
- [Phase 3: Hardening](3-Hardening/README.md) - 📋 Policies + 🔧 CD fixers + 🛡️ Enforcement
- [Phase 4: Cloud Migration](4-Cloud-Migration/README.md) - 📋 Terraform modules
- [Phase 5: Compliance Audit](5-Compliance-Audit/README.md) - 📊 Reports + validation
- [Phase 6: Auto-Agents](6-Auto-Agents/README.md) - 🤖 AI automation

---

**Framework Version:** 2.0 (Phase-Based with Explicit Tags)
**Last Updated:** 2025-10-14
**Tag System Version:** 1.0