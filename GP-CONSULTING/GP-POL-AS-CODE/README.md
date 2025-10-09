# GP Policy-as-Code (GP-POL-AS-CODE)

**Status:** ✅ Reorganized (Oct 2, 2025) | 🤖 Agent-Ready | 🚀 Production Policies
**Part of:** GP-Copilot / Jade AI Security Platform
**Purpose:** Automated security policy management for Kubernetes, Terraform, and cloud infrastructure

---

## 📁 Directory Structure (v2.0 - Clean)

```
GP-POL-AS-CODE/
│
├── 1-POLICIES/                          # 📚 Source of Truth
│   ├── opa/                             # 12 OPA policies (1,676 lines)
│   │   ├── pod-security.rego           # Container security (CIS-5.2.x)
│   │   ├── network-policies.rego       # Network segmentation (PCI-DSS-1.2)
│   │   ├── terraform-security.rego     # IaC security (AWS/Azure/GCP)
│   │   ├── secrets-management.rego     # Secret handling (CIS-5.4.1)
│   │   ├── compliance-controls.rego    # SOC2, HIPAA, GDPR
│   │   └── ... (7 more policies)
│   │
│   └── gatekeeper/                      # Kubernetes admission control
│       ├── templates/                   # ConstraintTemplates (reusable)
│       │   └── pod-security-template.yaml
│       └── constraints/                 # Constraint instances
│           ├── production/              # Production enforcement
│           │   └── pod-security-constraint.yaml
│           └── staging/                 # Staging audit mode
│
├── 2-AUTOMATION/                        # 🤖 Agent Tools
│   ├── agents/                          # ✨ NEW: Three-Step Automation Agents
│   │   ├── conftest_gate_agent.py      # Step 1: CI Terraform validation
│   │   ├── gatekeeper_audit_agent.py   # Step 2: Daily K8s audit
│   │   ├── pr_bot_agent.py             # Step 2: Auto-fix PR creator
│   │   ├── patch_rollout_agent.py      # Step 3: Staged rollout (dryrun→warn→deny)
│   │   └── README.md                    # Agent documentation
│   │
│   ├── scanners/                        # Read-only analysis
│   │   ├── opa_scanner.py              # OPA policy evaluation (565 lines)
│   │   └── opa_server_config.yaml      # OPA server config
│   │
│   ├── fixers/                          # Auto-remediate violations
│   │   └── opa_fixer.py                # 30+ fix patterns (896 lines)
│   │
│   ├── generators/                      # Create new policies
│   │   └── opa_policy_generator.py     # Gatekeeper generator (377 lines)
│   │
│   └── orchestrators/                   # Workflow coordination
│       ├── opa_manager.py              # OPA lifecycle (483 lines)
│       └── opa_cluster_manager.py      # Cluster operations
│
├── 3-STANDARDS/                         # 🏢 GuidePoint Production
│   ├── opa-policies/
│   │   └── guidepoint-security-standards.rego  # 280 lines, 12 rules
│   │
│   ├── terraform-modules/
│   │   ├── guidepoint-secure-rds.tf    # Secure RDS (400 lines)
│   │   └── guidepoint-secure-s3.tf     # Secure S3 (350 lines)
│   │
│   ├── GUIDEPOINT_STANDARDS_SUMMARY.md # Quick reference
│   └── README.md                        # Implementation guide
│
├── 4-DOCS/                              # 📖 Documentation
│   ├── COMPLIANCE_MAPPINGS.md           # Policy → framework mappings
│   ├── GUIDEPOINT_ENGAGEMENT_GUIDE.md   # Client workflow
│   ├── THREAT_MODEL.md                  # Attack vector analysis
│   ├── HUMAN_WORKFLOW.md                # Manual security process
│   ├── JADE_AI_WORKFLOW.md              # AI automation workflow
│   ├── IMPLEMENTATION_SUMMARY.md        # Implementation details
│   ├── OPA_INTEGRATION_VALIDATION.md    # Integration testing
│   └── README.md                        # Docs index
│
└── README.md                            # This file - main documentation
```

**Total:** 13 directories, 28 files, 5,819 lines of code
**Breakdown:** 1,676 OPA policies + 750 Terraform + 900 automation + 2,493 orchestration

---

## 🚀 Quick Start

### **Option 1: Policy Agent (Recommended)**

```bash
cd /home/jimmie/linkops-industries/GP-copilot

# Autonomous remediation (Scan → Fix → Generate → Deploy)
python GP-PLATFORM/coordination/policy_agent.py remediate /path/to/project

# Or scan only
python GP-PLATFORM/coordination/policy_agent.py scan /path/to/project
```

### **Option 2: Individual Tools**

```bash
cd GP-CONSULTING-AGENTS/GP-POL-AS-CODE

# 1. Scan
python 2-AUTOMATION/scanners/opa_scanner.py /path/to/project security

# 2. Generate fixes
python 2-AUTOMATION/fixers/opa_fixer.py scan_results.json /path/to/project

# 3. Generate Gatekeeper policies
python 2-AUTOMATION/generators/opa_policy_generator.py
```

---

## 🎯 Use Cases

### **CI/CD Pipeline**

```yaml
# .github/workflows/security.yml
- name: OPA Security Scan
  run: |
    python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py . security
```

### **Kubernetes Cluster**

```bash
# Install Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.15/deploy/gatekeeper.yaml

# Deploy policies
kubectl apply -f 1-POLICIES/gatekeeper/templates/
kubectl apply -f 1-POLICIES/gatekeeper/constraints/production/
```

### **Pre-Commit Hook**

```bash
# .git/hooks/pre-commit
python 2-AUTOMATION/scanners/opa_scanner.py . terraform-security
```

---

## 📊 What's Inside

### **1-POLICIES/** (Source of Truth)

**OPA Policies (12 files):**
- `pod-security.rego` - Container security (CIS-5.2.x)
- `network-policies.rego` - Network segmentation (PCI-DSS-1.2)
- `secrets-management.rego` - Secret handling (CIS-5.4.1)
- `terraform-security.rego` - IaC security (AWS, Azure, GCP)
- `compliance-controls.rego` - SOC2, HIPAA, GDPR
- And 7 more...

**Gatekeeper Templates:**
- `pod-security-template.yaml` - Blocks privileged, requires non-root

---

### **2-AUTOMATION/** (Agent Tools)

**✨ NEW: Three-Step Automation Agents** (Oct 3, 2025)

The three-step groove: **OPA + Gatekeeper codification** → **Automation wiring** → **Close the loop**

1. **Conftest Gate Agent** - CI shift-left validation
   - Validates Terraform plans against OPA policies at plan time
   - Fails pipeline if violations found (deny bad builds by default)
   - Example: `python conftest_gate_agent.py ./infrastructure`

2. **Gatekeeper Audit Agent** - Daily Kubernetes violation scanning
   - Surfaces live violations in running clusters
   - Generates audit reports grouped by severity
   - Example: `python gatekeeper_audit_agent.py`

3. **PR Bot Agent** - Automated fix proposals
   - Analyzes audit violations
   - Generates fixes using OpaFixer
   - Creates PRs against Helm/Kustomize sources
   - Example: `python pr_bot_agent.py /path/to/repo audit.json`

4. **Patch Rollout Agent** - Staged deployment (dryrun → warn → deny)
   - Progressive enforcement prevents production breakage
   - Enables Gatekeeper mutation for sane defaults
   - Example: `python patch_rollout_agent.py progressive constraint.yaml staging`

**Full Documentation:** [2-AUTOMATION/agents/README.md](2-AUTOMATION/agents/README.md)

---

**Scanners (Read-Only):**
- `opa_scanner.py` (565 lines) - Detect violations

**Generators (Create New):**
- `opa_policy_generator.py` (377 lines) - Generate Gatekeeper from violations

**Fixers (Modify Files):**
- `opa_fixer.py` (896 lines) - 30+ automated fix patterns
  - Remove privileged flags
  - Add resource limits
  - Enforce non-root users
  - Enable encryption
  - Add compliance labels

**Orchestrators (Workflows):**
- `opa_manager.py` (483 lines) - OPA lifecycle
- `policy_agent.py` (NEW) - Autonomous remediation

---

### **3-STANDARDS/** (GuidePoint)

**Production-Ready Policy:**
- `guidepoint-security-standards.rego` (280 lines, 12 rules)
  - Non-root containers (CIS-5.2.6)
  - No privileged (CIS-5.2.5)
  - Resource limits (CIS-5.7.3)
  - No host access (CIS-5.2.4)
  - And 8 more...

**Terraform Modules:**
- `guidepoint-secure-rds.tf` - Encrypted RDS, Secrets Manager
- `guidepoint-secure-s3.tf` - No public buckets, KMS encryption

---

### **4-DOCS/** (Documentation)

- `COMPLIANCE_MAPPINGS.md` - Map policies → frameworks
- `THREAT_MODEL.md` - Attack vectors explained
- `GUIDEPOINT_ENGAGEMENT_GUIDE.md` - Client workflow
- `HUMAN_WORKFLOW.md` - Manual process
- `JADE_AI_WORKFLOW.md` - AI automation

---

## 🤖 Integration with Jade AI

### **Policy Agent**

Coordinates all tools for autonomous operation:

```python
from GP_PLATFORM.coordination.policy_agent import PolicyAgent

agent = PolicyAgent(approval_required=True)
results = agent.auto_remediate("/path/to/project")

# Workflow:
# 1. 📊 Scan: 25 violations
# 2. 🔧 Generate: 18 fixes
# 3. ⏸️  Approval: Human review
# 4. ✨ Apply: 12 files modified
# 5. 🛡️  Generate: 5 Gatekeeper policies
```

### **LLM-Powered Generation**

**Status:** Testing DeepSeek-Coder-V2 (16B, code-specialized)

**Use Case:** Convert OPA policies → Gatekeeper ConstraintTemplates

**How:**
1. Parse OPA .rego rules
2. Generate ConstraintTemplate YAML
3. Embed Rego logic
4. Add compliance annotations

---

## 🏢 GuidePoint Standards

**Implemented Requirements:**
- ✅ Non-root containers mandatory
- ✅ No privileged containers
- ✅ Resource limits required
- ✅ No privilege escalation
- ✅ Drop dangerous capabilities
- ✅ No host namespace access
- ✅ No hostPath volumes
- ✅ Pod Security Standards enforced
- ✅ Database encryption required
- ✅ No public S3 buckets
- ✅ No hardcoded secrets
- ✅ HTTPS/TLS only

**Compliance Frameworks:**
- CIS Kubernetes Benchmark
- SOC2 (CC6.1, CC7.1, CC9.1)
- PCI-DSS (1.2, 2.2.2, 3.4)
- NIST (AC-2, AC-3, AC-6)
- HIPAA, GDPR, SLSA

---

## 📈 Metrics

- **OPA Policies:** 12 files, 1,676 lines
- **Gatekeeper Templates:** 1 (expandable to 12+)
- **Fix Patterns:** 30+ automated fixes
- **Terraform Modules:** 2 (RDS, S3)
- **Compliance Frameworks:** 7 (CIS, SOC2, PCI-DSS, HIPAA, GDPR, NIST, SLSA)
- **Cloud Providers:** AWS, Azure, GCP
- **Languages:** Python, Rego, YAML

---

## 🔄 CI/CD vs Cluster Deployment

### **CI/CD Only (No Server)**
✅ OPA Scanner
✅ OPA Fixer
✅ Policy Generator
✅ Terraform validation
✅ Pre-commit hooks

### **Requires Server (Cluster)**
🔴 Gatekeeper (Kubernetes admission control)
🔴 OPA Server (alternative to Gatekeeper)

### **Best Practice:**
```
Local Dev → CI/CD → Staging (audit) → Production (enforce)
```

---

## 🚦 Status & Next Steps

**Completed:**
1. ✅ Directory reorganization (v2.0)
2. ✅ PolicyAgent orchestrator created
3. ✅ 12 OPA policies (1,676 lines)
4. ✅ GuidePoint standards (280 lines)
5. ✅ 30+ automated fix patterns
6. ✅ **Three-Step Automation Agents** (Oct 3, 2025)
   - ✅ Conftest Gate Agent (CI shift-left)
   - ✅ Gatekeeper Audit Agent (daily scanning)
   - ✅ PR Bot Agent (auto-fix PRs)
   - ✅ Patch Rollout Agent (dryrun → warn → deny)

**In Progress:**
- ⏳ Testing DeepSeek-Coder for Gatekeeper generation

**Planned:**
- ⏸️ Expand Gatekeeper templates (1 → 12)
- ⏸️ Network policy generator
- ⏸️ Approval workflow integration

---

## 🎓 Documentation

- [COMPLIANCE_MAPPINGS.md](4-DOCS/COMPLIANCE_MAPPINGS.md)
- [THREAT_MODEL.md](4-DOCS/THREAT_MODEL.md)
- [GUIDEPOINT_ENGAGEMENT_GUIDE.md](4-DOCS/GUIDEPOINT_ENGAGEMENT_GUIDE.md)
- [HUMAN_WORKFLOW.md](4-DOCS/HUMAN_WORKFLOW.md)
- [JADE_AI_WORKFLOW.md](4-DOCS/JADE_AI_WORKFLOW.md)

**External:**
- [OPA Docs](https://www.openpolicyagent.org/docs/)
- [Gatekeeper Docs](https://open-policy-agent.github.io/gatekeeper/)
- [CIS Benchmark](https://www.cisecurity.org/benchmark/kubernetes)

---

**Version:** 2.0 (Reorganized Structure)
**Last Updated:** October 2, 2025
**Contact:** security@guidepoint.com
**Maintained by:** GP-Copilot / Jade AI