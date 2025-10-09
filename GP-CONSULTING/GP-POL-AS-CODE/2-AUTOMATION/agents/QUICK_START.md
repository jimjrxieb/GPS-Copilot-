# Quick Start: Using the Automation Agents

**Updated:** October 3, 2025

---

## 🚀 Run the Example Workflow

The easiest way to see how everything works:

```bash
# Run on a Terraform repo
./example_workflow.sh ~/projects/my-terraform-infra

# Run on a Kubernetes repo
./example_workflow.sh ~/projects/my-k8s-manifests
```

This will:
1. ✅ Scan for violations (Conftest Gate)
2. ✅ Generate fixes (PR Bot)
3. ✅ Show staged rollout options (Patch Rollout)
4. ✅ Tell you where to see results

---

## 📍 Where to See Changes

### **1. Your Git Repo** (Most Important!)

```bash
cd ~/projects/my-terraform-infra

# See what Jade modified
git status

# View the actual changes
git diff

# See Jade's commit message
git log -1
```

**Example output:**
```diff
modified:   s3.tf

diff --git a/s3.tf b/s3.tf
index abc123..def456 100644
--- a/s3.tf
+++ b/s3.tf
@@ -1,5 +1,15 @@
 resource "aws_s3_bucket" "app" {
   bucket = "my-app-bucket"
-  acl    = "public-read"  # REMOVED by Jade
+  acl    = "private"      # FIXED by Jade
+}
+
+# ADDED by Jade to block public access
+resource "aws_s3_bucket_public_access_block" "app" {
+  bucket = aws_s3_bucket.app.id
+
+  block_public_acls       = true
+  block_public_policy     = true
+  ignore_public_acls      = true
+  restrict_public_buckets = true
 }
```

---

### **2. Approval Queue (Electron GUI)**

```bash
# Start Jade GUI
cd /home/jimmie/linkops-industries/GP-copilot/GP-GUI
npm start
```

**What you'll see:**
- **Left panel:** List of all proposals (CRITICAL, HIGH, MEDIUM)
- **Right panel:** Detailed diff view (current vs proposed)
- **Buttons:** [Approve] [Reject] [Modify]

**Screenshot (conceptual):**
```
┌─────────────────────────────────────────────────────────────┐
│ GP-COPILOT - Approval Queue                  [3 Pending]    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ ┌─────────────────┐  ┌────────────────────────────────────┐ │
│ │ Proposals       │  │ Details: Proposal #1001            │ │
│ ├─────────────────┤  ├────────────────────────────────────┤ │
│ │                 │  │                                    │ │
│ │ 🔴 #1001        │  │ Current Code:                      │ │
│ │ Fix S3 Public   │  │   acl = "public-read"              │ │
│ │ Bucket          │  │                                    │ │
│ │ [CRITICAL]      │  │ Proposed Fix:                      │ │
│ │                 │  │   acl = "private"                  │ │
│ │ 🟡 #1002        │  │   + public_access_block resource   │ │
│ │ Encrypt RDS     │  │                                    │ │
│ │ [HIGH]          │  │ Compliance: SOC2-CC6.1             │ │
│ │                 │  │                                    │ │
│ │ 🟢 #1003        │  │ [Approve] [Reject] [Modify]        │ │
│ │ Add Tags        │  │                                    │ │
│ │ [AUTO-FIXED]    │  │                                    │ │
│ │                 │  │                                    │ │
│ └─────────────────┘  └────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

### **3. Activity Tracker (Ask Jade)**

```bash
# Query Jade about what happened
jade query "What did we do today?"
jade query "Show me all CRITICAL proposals"
jade query "What violations did you find in my-terraform-infra?"
```

**Example response:**
```
Jade Response:

Today (October 3, 2025) we accomplished:

📊 Security Scans:
- Scanned my-terraform-infra (23 Terraform files)
- Found 12 violations (3 CRITICAL, 2 HIGH, 7 MEDIUM)

🔧 Fixes Applied:
- ✅ Fixed 3 CRITICAL S3 public bucket violations
- ✅ Auto-fixed 7 MEDIUM tagging violations
- ⏳ Pending approval: 2 HIGH RDS encryption violations

📁 Files Modified:
- s3.tf (added encryption, blocked public access)
- main.tf (added compliance tags)

📋 Compliance Impact:
- SOC2-CC6.1: 3 controls enforced
- PCI-DSS-3.4: 2 controls enforced
```

---

### **4. Audit Reports (File System)**

```bash
# View audit reports
ls -lh /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/audit/

# Read latest report
cat /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/audit/gatekeeper_audit_2025-10-03_09-00-00.txt
```

**Example report:**
```
================================================================================
GATEKEEPER DAILY AUDIT REPORT
Generated: 2025-10-03T09:00:00
================================================================================

Total Violations: 5

Violations by Severity:
  CRITICAL: 2
  HIGH: 0
  MEDIUM: 3

Detailed Violations:
--------------------------------------------------------------------------------

[CRITICAL] K8sDenyPrivileged
  Resource: Deployment/nginx
  Namespace: default
  Message: Container 'nginx' is running in privileged mode
  Enforcement: deny

[CRITICAL] K8sRequireNonRoot
  Resource: Deployment/redis
  Namespace: cache
  Message: Container 'redis' running as root user
  Enforcement: warn

[MEDIUM] K8sRequireResourceLimits
  Resource: Deployment/api
  Namespace: default
  Message: Container 'api' missing resource limits
  Enforcement: dryrun

================================================================================
```

---

### **5. Pull Requests (GitHub/GitLab)**

If PR bot is enabled and you have `gh` CLI:

```bash
# View created PRs
gh pr list

# View PR details
gh pr view 123
```

**Example PR:**
```
Title: 🤖 Fix S3 Security Violations (Proposal #1001)

## Summary
Jade AI detected 3 CRITICAL S3 public bucket vulnerabilities.

## Changes
- ✅ Blocked public access on 2 S3 buckets
- ✅ Enabled encryption at rest

## Compliance
- SOC2-CC6.1, PCI-DSS-3.4

## Files Modified
- s3.tf

## Approval Trail
- Approved by: Manager (Oct 3, 2025 10:14 AM)
```

---

## 🤖 How Jade Makes Decisions

### **Decision Matrix**

```
Input: Violation found
   ↓
Check Severity
   ├─ CRITICAL → Create Approval Proposal (Expires: 24h)
   ├─ HIGH     → Check Environment
   │              ├─ Production → Create Approval Proposal (Expires: 7d)
   │              └─ Non-Prod   → Auto-Fix + Create PR
   └─ MEDIUM/LOW → Auto-Fix via Gatekeeper Mutation
```

### **Where Decisions Happen**

**File:** `GP-AI/engines/ai_security_engine.py` (Jade AI Engine)

**Logic:**
```python
def decide_action(violation):
    # Step 1: Analyze severity
    if violation['severity'] == 'CRITICAL':
        return create_approval_proposal(violation, expiry_hours=24)

    # Step 2: Check environment
    if violation['severity'] == 'HIGH':
        if violation['environment'] == 'production':
            return create_approval_proposal(violation, expiry_hours=168)
        else:
            return auto_fix_and_create_pr(violation)

    # Step 3: Auto-fix low-severity issues
    if violation['severity'] in ['MEDIUM', 'LOW']:
        return auto_fix_via_mutation(violation)
```

**File:** `GP-AI/approval/state_machine.py` (Approval System)

Manages the proposal lifecycle:
- `proposed` → `pending` → `approved` → `executing` → `completed`
- Or: `pending` → `rejected` (if manager declines)
- Or: `pending` → `expired` (if not reviewed in time)

---

## 📊 Visual Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Manager: "jade scan ~/projects/my-infra"                     │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Jade AI Engine                                               │
│ - Analyzes repo type (Terraform/K8s)                         │
│ - Calls appropriate agent                                    │
└────────────────────────┬────────────────────────────────────┘
                         ↓
         ┌───────────────┴───────────────┐
         ↓                               ↓
┌──────────────────┐            ┌──────────────────┐
│ Conftest Gate    │            │ Gatekeeper Audit │
│ (Terraform)      │            │ (Kubernetes)     │
└────────┬─────────┘            └────────┬─────────┘
         ↓                               ↓
         └───────────────┬───────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Violations Found: 12                                         │
│ - 3 CRITICAL (S3 public buckets)                             │
│ - 2 HIGH (RDS unencrypted)                                   │
│ - 7 MEDIUM (missing tags)                                    │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Jade Decision Engine                                         │
│                                                               │
│ CRITICAL (3) → Create 3 approval proposals                   │
│ HIGH (2)     → Check environment...                          │
│                ├─ Production: Create 2 approval proposals    │
│                └─ Non-prod: Auto-fix                         │
│ MEDIUM (7)   → Auto-fix via Gatekeeper mutation              │
└────────────────────────┬────────────────────────────────────┘
                         ↓
         ┌───────────────┴───────────────┐
         ↓                               ↓
┌──────────────────┐            ┌──────────────────┐
│ Approval Queue   │            │ Auto-Execute     │
│ (5 proposals)    │            │ (7 fixes)        │
│                  │            │                  │
│ Manager reviews  │            │ Jade applies:    │
│ and approves     │            │ - Gatekeeper     │
│ in Electron GUI  │            │   mutation       │
│                  │            │ - PR bot         │
└────────┬─────────┘            └────────┬─────────┘
         ↓                               ↓
         └───────────────┬───────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Execution Phase                                              │
│ - Apply fixes to files                                       │
│ - Create git commits                                         │
│ - Create PRs (if enabled)                                    │
│ - Update approval state: executing → completed               │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Track in RAG (GP-RAG/auto_sync.py)                          │
│ - What: "Fixed 12 violations in my-infra"                    │
│ - When: "Oct 3, 2025 10:15 AM"                              │
│ - How: "Applied guidepoint-secure-s3.tf patterns"           │
│ - Compliance: "SOC2-CC6.1, PCI-DSS-3.4"                      │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Manager: "jade query 'What did we do today?'"               │
│                                                               │
│ Jade: "Fixed 12 violations (5 approved, 7 auto-fixed).      │
│        Modified 3 files. Applied 9 compliance controls."     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Try It Now

### **Test on DVWA (Already in GP-PROJECTS)**

```bash
# Scan the DVWA project
cd /home/jimmie/linkops-industries/GP-copilot
./GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/example_workflow.sh GP-PROJECTS/DVWA

# See what Jade found
ls -lh GP-DATA/active/audit/

# View results
cat GP-DATA/active/audit/latest.txt
```

### **Test on Your Own Repo**

```bash
# Replace with your actual repo path
./GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/example_workflow.sh ~/projects/my-terraform-infra

# Check git changes
cd ~/projects/my-terraform-infra
git status
git diff
```

---

## 📚 More Documentation

- **[JADE_INTEGRATION_GUIDE.md](JADE_INTEGRATION_GUIDE.md)** - Complete integration guide
- **[README.md](README.md)** - Agent documentation
- **[../../README.md](../../README.md)** - GP-POL-AS-CODE overview
- **[../../../../VISION.md](../../../../VISION.md)** - Overall architecture

---

## 🆘 Troubleshooting

**Q: I don't see any changes in my git repo**

A: Check if Jade created approval proposals instead (CRITICAL/HIGH violations require approval first)
```bash
# View approval queue via API
curl http://localhost:8000/api/v1/approvals/pending

# Or open Jade GUI
cd GP-GUI && npm start
```

**Q: Conftest gate fails with "conftest not found"**

A: Install conftest:
```bash
curl -L -o conftest.tar.gz https://github.com/open-policy-agent/conftest/releases/download/v0.49.1/conftest_0.49.1_Linux_x86_64.tar.gz
tar xzf conftest.tar.gz
sudo mv conftest /usr/local/bin/
```

**Q: Gatekeeper audit fails with "kubectl not found"**

A: Install kubectl:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

**Q: Where is Jade's FastAPI server?**

A: Start it:
```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-AI
uvicorn api.main:app --reload
```

Access at: http://localhost:8000/docs

---

**Ready to automate your security workflow!** 🚀