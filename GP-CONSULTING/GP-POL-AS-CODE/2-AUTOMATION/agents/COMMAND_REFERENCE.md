# GP-Copilot Command Reference
## All Commands for Scans, Agents, and Automation

**Updated:** October 3, 2025
**Status:** ✅ All tools installed and working

---

## 📦 Installed Tools

```bash
# Verify installations
which terraform  # /snap/bin/terraform
which opa        # /usr/local/bin/opa
which conftest   # /home/jimmie/linkops-industries/GP-copilot/bin/conftest
which python3    # /usr/bin/python3
```

---

## 🎯 Quick Commands (Most Common)

### **Scan a Terraform Project**
```bash
cd /home/jimmie/linkops-industries/GP-copilot

# Using OPA Scanner (Recommended - always works)
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup \
  terraform-security
```

### **Scan Using Conftest Gate (Now Available!)**
```bash
cd /home/jimmie/linkops-industries/GP-copilot

python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py \
  GP-PROJECTS/Terraform_CICD_Setup
```

### **View Latest Results**
```bash
# JSON format
cat GP-DATA/active/scans/opa_latest.json | jq '.'

# Human-readable summary
cat GP-PROJECTS/Terraform_CICD_Setup/GP-copilot/SCAN_SUMMARY_*.md
```

### **Query Jade**
```bash
jade query "What did we scan today?"
jade query "Show me scan results for Terraform_CICD_Setup"
jade query "What CRITICAL violations did we find?"
```

---

## 📋 All Scanner Commands

### **1. OPA Scanner (Multi-Purpose)**

**Security scan:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  <target_directory> \
  security
```

**Terraform-specific scan:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  <target_directory> \
  terraform-security
```

**Kubernetes scan:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  <target_directory> \
  kubernetes
```

**Examples:**
```bash
# Scan Terraform_CICD_Setup
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup \
  terraform-security

# Scan DVWA project
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/DVWA \
  security

# Scan LinkOps-MLOps
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/LinkOps-MLOps \
  security
```

---

### **2. Bandit Scanner (Python Security)**

```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/bandit_scanner.py \
  <target_directory>
```

**Example:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/bandit_scanner.py \
  GP-PROJECTS/DVWA
```

---

### **3. Trivy Scanner (Container/Dependency Security)**

```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/trivy_scanner.py \
  <target_directory>
```

**Example:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/trivy_scanner.py \
  GP-PROJECTS/LinkOps-MLOps
```

---

### **4. Gitleaks Scanner (Secret Detection)**

```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/gitleaks_scanner.py \
  <target_directory> \
  detect
```

**Example:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/gitleaks_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup \
  detect
```

---

### **5. Semgrep Scanner (SAST)**

```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/semgrep_scanner.py \
  <target_directory>
```

---

## 🤖 Automation Agent Commands

### **1. Conftest Gate Agent (CI Shift-Left)**

**Purpose:** Validate Terraform plans at CI time

```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py \
  <terraform_directory>
```

**Example:**
```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py \
  GP-PROJECTS/Terraform_CICD_Setup
```

**What it does:**
1. Runs `terraform plan`
2. Validates plan against OPA policies using Conftest
3. Saves results to `GP-DATA/active/scans/conftest/`
4. Returns exit code 0 (pass) or 1 (fail)

---

### **2. Gatekeeper Audit Agent (Daily K8s Audit)**

**Purpose:** Surface live violations in Kubernetes clusters

```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/gatekeeper_audit_agent.py
```

**What it does:**
1. Queries Gatekeeper for violations
2. Groups by severity (CRITICAL/HIGH/MEDIUM/LOW)
3. Saves report to `GP-DATA/active/audit/`
4. Returns exit code 0 (no violations) or 1 (violations found)

**Note:** Requires Gatekeeper installed in Kubernetes cluster

---

### **3. PR Bot Agent (Auto-Fix PRs)**

**Purpose:** Create PRs with automated fixes

```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/pr_bot_agent.py \
  <repo_path> \
  <audit_file>
```

**Example:**
```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/pr_bot_agent.py \
  ~/projects/my-k8s-manifests \
  /tmp/gatekeeper_audit.json
```

**What it does:**
1. Reads audit violations
2. Searches repo for violating resources
3. Applies fixes using `opa_fixer.py`
4. Creates git branch and PR

**Note:** Requires `gh` CLI for PR creation

---

### **4. Patch Rollout Agent (Staged Deployment)**

**Purpose:** Progressive enforcement (dryrun → warn → deny)

**Deploy with specific enforcement:**
```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py \
  deploy \
  <constraint_file> \
  <environment> \
  <enforcement_action>
```

**Progressive rollout:**
```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py \
  progressive \
  <constraint_file> \
  <environment>
```

**Enable mutation (non-prod only):**
```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py \
  mutation \
  <environment>
```

**Check rollout status:**
```bash
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py \
  status \
  <constraint_name>
```

**Examples:**
```bash
# Deploy in dryrun mode (audit only)
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py \
  deploy \
  GP-CONSULTING-AGENTS/GP-POL-AS-CODE/1-POLICIES/gatekeeper/constraints/production/pod-security-constraint.yaml \
  staging \
  dryrun

# Progressive rollout (auto-advances through stages)
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py \
  progressive \
  GP-CONSULTING-AGENTS/GP-POL-AS-CODE/1-POLICIES/gatekeeper/constraints/production/pod-security-constraint.yaml \
  staging

# Enable mutation in dev
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/patch_rollout_agent.py \
  mutation \
  dev
```

---

## 🔄 Complete Workflow Commands

### **Example Workflow Script**

Use the provided workflow script:
```bash
cd GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents

./example_workflow.sh ~/projects/my-terraform-infra
```

**What it does:**
1. Detects repo type (Terraform/K8s)
2. Runs appropriate scanners
3. Shows where to see results
4. Explains next steps

---

### **Manual Complete Workflow**

**Step 1: Scan**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup \
  terraform-security
```

**Step 2: Check Results**
```bash
cat GP-DATA/active/scans/opa_latest.json | jq '.summary'
```

**Step 3: If Violations Found, Generate Fixes**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/fixers/opa_fixer.py \
  GP-DATA/active/scans/opa_latest.json \
  GP-PROJECTS/Terraform_CICD_Setup
```

**Step 4: Review in Jade Approval Queue**
```bash
# Start Jade GUI
cd GP-GUI && npm start
# Navigate to Approval Queue tab
```

**Step 5: Query Jade**
```bash
jade query "What did we do today?"
```

---

## 📊 View Results Commands

### **View Scan Results**

**Latest OPA scan:**
```bash
cat GP-DATA/active/scans/opa_latest.json | jq '.'
```

**Summary only:**
```bash
cat GP-DATA/active/scans/opa_latest.json | jq '.summary'
```

**Count violations:**
```bash
cat GP-DATA/active/scans/opa_latest.json | jq '.summary.total'
```

**All scans today:**
```bash
ls -lh GP-DATA/active/scans/*_$(date +%Y%m%d)*.json
```

---

### **View Conftest Results**

```bash
# Latest conftest scan
ls -lh GP-DATA/active/scans/conftest/

# Human-readable report
cat GP-DATA/active/scans/conftest/*_report.txt
```

---

### **View Audit Reports**

```bash
# Gatekeeper audit reports
ls -lh GP-DATA/active/audit/

# Latest audit
cat GP-DATA/active/audit/gatekeeper_audit_*_report.txt
```

---

## 🚀 CI/CD Integration Commands

### **GitHub Actions**

Add to `.github/workflows/security.yml`:
```yaml
- name: OPA Security Scan
  run: |
    PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
      python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
      . \
      terraform-security

- name: Conftest Gate
  run: |
    python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py \
      ./infrastructure
```

---

### **Pre-Commit Hook**

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
cd /home/jimmie/linkops-industries/GP-copilot

PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  . \
  terraform-security

if [ $? -ne 0 ]; then
  echo "❌ OPA security scan failed"
  exit 1
fi
```

---

### **Daily Cron Job**

```bash
# Add to crontab: crontab -e
0 9 * * * cd /home/jimmie/linkops-industries/GP-copilot && PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/gatekeeper_audit_agent.py
```

---

## 🎯 Project-Specific Commands

### **Terraform_CICD_Setup**
```bash
# OPA scan
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup \
  terraform-security

# Conftest gate
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py \
  GP-PROJECTS/Terraform_CICD_Setup

# View results
cat GP-PROJECTS/Terraform_CICD_Setup/GP-copilot/scan_results_*.json | jq '.'
```

---

### **DVWA**
```bash
# Security scan
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/DVWA \
  security

# Bandit (Python security)
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/bandit_scanner.py \
  GP-PROJECTS/DVWA
```

---

### **LinkOps-MLOps**
```bash
# Security scan
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/LinkOps-MLOps \
  security

# Trivy (dependencies)
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/scanners/trivy_scanner.py \
  GP-PROJECTS/LinkOps-MLOps
```

---

## 🔧 Utility Commands

### **Check Tool Versions**
```bash
terraform version
opa version
bin/conftest --version
python3 --version
```

---

### **Clean Old Scans**
```bash
# Remove scans older than 30 days
find GP-DATA/active/scans/ -name "*.json" -mtime +30 -delete
```

---

### **Export Results**
```bash
# Export all scans to archive
tar -czf gp-copilot-scans-$(date +%Y%m%d).tar.gz GP-DATA/active/scans/
```

---

## 📚 Documentation Commands

**View guides:**
```bash
# Integration guide
cat GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/JADE_INTEGRATION_GUIDE.md

# Quick start
cat GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/QUICK_START.md

# Scan results guide
cat GP-DATA/active/scans/SCAN_RESULTS_GUIDE.md

# This command reference
cat GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/COMMAND_REFERENCE.md
```

---

## 🆘 Troubleshooting Commands

**Check if tools are installed:**
```bash
which terraform && echo "✅ terraform" || echo "❌ terraform not found"
which opa && echo "✅ opa" || echo "✅ opa" || echo "❌ opa not found"
which bin/conftest && echo "✅ conftest" || echo "❌ conftest not found"
```

**Check PYTHONPATH:**
```bash
echo $PYTHONPATH
```

**Test OPA scanner:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python -c "from gp_data_config import GPDataConfig; print('✅ Config module working')"
```

**Check Jade API:**
```bash
curl http://localhost:8000/health
```

---

## 📋 Cheat Sheet (Copy-Paste Ready)

```bash
# Navigate to GP-Copilot
cd /home/jimmie/linkops-industries/GP-copilot

# Scan Terraform project
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup \
  terraform-security

# Conftest gate
python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py \
  GP-PROJECTS/Terraform_CICD_Setup

# View results
cat GP-DATA/active/scans/opa_latest.json | jq '.summary'

# Query Jade
jade query "What did we scan today?"

# Open Jade GUI
cd GP-GUI && npm start
```

---

**All commands assume you're in `/home/jimmie/linkops-industries/GP-copilot`**

**For more details, see:**
- [JADE_INTEGRATION_GUIDE.md](JADE_INTEGRATION_GUIDE.md)
- [QUICK_START.md](QUICK_START.md)
- [SCAN_RESULTS_GUIDE.md](../../../GP-DATA/active/scans/SCAN_RESULTS_GUIDE.md)
