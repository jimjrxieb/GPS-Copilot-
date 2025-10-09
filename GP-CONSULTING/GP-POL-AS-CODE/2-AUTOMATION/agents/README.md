# GP Policy Automation Agents

**Status:** ✅ Production Ready
**Updated:** October 3, 2025
**Purpose:** Simple, autonomous agents implementing the three-step security groove

---

## 🚀 Quick Start

**Want to see it in action? Run this:**

```bash
# Test on your Terraform or Kubernetes repo
./example_workflow.sh ~/projects/my-terraform-infra
```

**Where to see changes:**
1. **Your git repo:** `git status && git diff` (most important!)
2. **Approval Queue:** Open Jade GUI → Approval Queue tab
3. **Query Jade:** `jade query "What did we do today?"`

**📖 Read this first:** [QUICK_START.md](QUICK_START.md) - Complete usage guide with examples

---

## 🎯 The Three-Step Groove

**Step 1: OPA + Gatekeeper Codification**
Rego policies for Terraform at plan time, ConstraintTemplates for Kubernetes at admission — deny bad builds by default.

**Step 2: Automation Wiring**
Conftest gates in CI (shift-left), daily Gatekeeper audit that surfaces live violations, PR bot that opens fixes against Helm/Kustomize sources.

**Step 3: Close the Loop**
Safe auto-patches in non-prod, Gatekeeper mutation for sane defaults, staged rollout from `dryrun → warn → deny` to remediate fast without breaking prod.

---

## 📦 Agents

### 1. **Conftest Gate Agent** (`conftest_gate_agent.py`)

**Purpose:** CI/CD gate - validate Terraform plans against OPA policies at plan time.

**What it does:**
- Runs `terraform plan` and converts to JSON
- Tests plan against OPA policies using Conftest
- Fails pipeline if violations found
- Shift-left: catch issues before deployment

**Usage:**
```bash
# In CI/CD pipeline
python conftest_gate_agent.py /path/to/terraform

# Returns exit code 0 if passed, 1 if violations
```

**Example `.github/workflows/terraform.yml`:**
```yaml
- name: OPA Security Gate
  run: |
    python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py ./infrastructure
```

---

### 2. **Gatekeeper Audit Agent** (`gatekeeper_audit_agent.py`)

**Purpose:** Daily Kubernetes audit - surface live violations in running clusters.

**What it does:**
- Queries Gatekeeper for audit violations
- Parses violations from all ConstraintTemplates
- Groups by severity (critical/high/medium/low)
- Generates human-readable audit report
- Triggers PR bot for auto-remediation

**Usage:**
```bash
# Run daily audit
python gatekeeper_audit_agent.py

# Output: /GP-DATA/active/audit/gatekeeper_audit_2025-10-03_14-30-00.txt
```

**Schedule with Kubernetes CronJob:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gatekeeper-daily-audit
spec:
  schedule: "0 9 * * *"  # Daily at 9 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: audit
            image: gp-copilot:latest
            command:
            - python
            - /app/GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/gatekeeper_audit_agent.py
```

---

### 3. **PR Bot Agent** (`pr_bot_agent.py`)

**Purpose:** Automated fix proposals - create PRs with fixes for Gatekeeper violations.

**What it does:**
- Reads Gatekeeper audit violations
- Searches repo for violating resources (Helm charts, Kustomize, raw manifests)
- Applies fixes using `opa_fixer.py`
- Creates git branch with fixes
- Opens PR with detailed remediation plan

**Usage:**
```bash
# Generate PR with fixes
python pr_bot_agent.py /path/to/k8s/repo /path/to/audit_report.json

# Requires: gh CLI (GitHub CLI) for PR creation
```

**Workflow Integration:**
```bash
# 1. Run audit
python gatekeeper_audit_agent.py

# 2. If violations found, create PR
if [ $? -ne 0 ]; then
  python pr_bot_agent.py ~/projects/k8s-manifests /tmp/audit.json
fi
```

---

### 4. **Patch Rollout Agent** (`patch_rollout_agent.py`)

**Purpose:** Staged rollout - progressive enforcement from `dryrun → warn → deny`.

**What it does:**
- Deploys Gatekeeper Constraints with staged enforcement
- Week 1: `dryrun` (audit only, gather data)
- Week 2-3: `warn` (log violations, alert teams)
- Week 4+: `deny` (full enforcement)
- Enables Gatekeeper mutation for auto-patching in non-prod
- Tracks rollout status and readiness

**Usage:**
```bash
# Deploy policy in dryrun mode
python patch_rollout_agent.py deploy constraint.yaml staging dryrun

# Run progressive rollout (auto-advances through stages)
python patch_rollout_agent.py progressive constraint.yaml staging

# Enable mutation in non-prod (auto-patch resources)
python patch_rollout_agent.py mutation dev

# Check rollout status
python patch_rollout_agent.py status k8sdenyprivileged
```

**Progressive Rollout Example:**
```bash
# Day 1: Deploy in dryrun (audit only)
python patch_rollout_agent.py deploy pod-security-constraint.yaml production dryrun

# Day 8: Upgrade to warn (log violations)
python patch_rollout_agent.py deploy pod-security-constraint.yaml production warn

# Day 15: Upgrade to deny (full enforcement)
python patch_rollout_agent.py deploy pod-security-constraint.yaml production deny
```

---

## 🔄 Complete Workflow

**Daily Automation Pipeline:**

```bash
#!/bin/bash
# GP-Copilot Daily Security Loop

set -e

REPO_PATH="/home/jimmie/projects/k8s-manifests"
AUDIT_FILE="/tmp/gatekeeper_audit_$(date +%Y%m%d).json"

echo "🔍 Step 1: Gatekeeper Daily Audit"
python gatekeeper_audit_agent.py > "$AUDIT_FILE"

if [ $? -ne 0 ]; then
  echo "⚠️  Violations found!"

  echo "🤖 Step 2: Create PR with Fixes"
  python pr_bot_agent.py "$REPO_PATH" "$AUDIT_FILE"

  echo "📧 Step 3: Notify Team"
  # (Integrate with notification system)
else
  echo "✅ No violations - cluster is compliant!"
fi
```

**CI/CD Integration:**

```yaml
# .github/workflows/security.yml
name: Security Gates

on: [pull_request]

jobs:
  terraform-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Conftest Gate
        run: |
          python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py ./infrastructure

  k8s-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: OPA K8s Validation
        run: |
          python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py . security
```

---

## 🛡️ Security Principles

### Shift-Left (Conftest Gate)
✅ Catch violations **before** deployment
✅ Fail fast in CI/CD
✅ Developer feedback loop < 5 minutes

### Continuous Audit (Gatekeeper Audit)
✅ Daily scans of live clusters
✅ Find drift and misconfigurations
✅ Track compliance over time

### Automated Remediation (PR Bot)
✅ Auto-generate fixes
✅ Human review before merge
✅ Audit trail in git history

### Safe Rollout (Patch Rollout)
✅ Progressive enforcement (dryrun → warn → deny)
✅ Gatekeeper mutation for sane defaults
✅ No production breakage

---

## 📊 Metrics & Reporting

Each agent generates metrics for tracking:

**Conftest Gate:**
- Violations per Terraform plan
- Most common violations
- Time to fix (PR merge time)

**Gatekeeper Audit:**
- Total violations per day
- Violations by severity
- Violations by namespace
- Violations by constraint type

**PR Bot:**
- PRs created per week
- Auto-fix success rate
- Time to merge

**Patch Rollout:**
- Policies in dryrun/warn/deny
- Violations during each stage
- Time to full enforcement

---

## 🚀 Next Steps

1. **Test the workflow:**
   ```bash
   # 1. Deploy test policy in dryrun
   python patch_rollout_agent.py deploy test-constraint.yaml dev dryrun

   # 2. Run audit
   python gatekeeper_audit_agent.py

   # 3. Generate PR
   python pr_bot_agent.py ~/projects/test-k8s /tmp/audit.json
   ```

2. **Schedule daily audit:**
   - Add CronJob to Kubernetes cluster
   - Or use Jenkins/GitHub Actions scheduled workflow

3. **Integrate with Jade AI:**
   - Jade reads audit reports
   - Jade prioritizes violations
   - Jade approves PR bot fixes
   - Jade tracks remediation metrics

4. **Add to VISION.md Phase 4:**
   - Policy automation is now production-ready
   - Feeds into reporting system
   - Closes the security loop

---

## 📚 Documentation

- [Conftest Docs](https://www.conftest.dev/)
- [Gatekeeper Docs](https://open-policy-agent.github.io/gatekeeper/)
- [OPA Docs](https://www.openpolicyagent.org/docs/)
- [GP-POL-AS-CODE README](../README.md)

---

**Version:** 1.0
**Author:** GP-Copilot Team
**Contact:** security@guidepoint.com