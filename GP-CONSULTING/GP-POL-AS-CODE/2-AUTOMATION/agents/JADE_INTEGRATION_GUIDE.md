# Jade AI Integration Guide
## How Jade Orchestrates the Three-Step Security Groove

**Updated:** October 3, 2025
**Purpose:** Show how Jade AI uses automation agents to make intelligent security decisions

---

## 🤖 Where Jade Comes In

Jade is the **intelligent orchestrator** that:
1. **Analyzes** violations found by agents
2. **Prioritizes** which fixes to apply first
3. **Proposes** changes to the approval queue
4. **Decides** when to escalate vs auto-fix
5. **Tracks** everything in RAG for "What did we do today?"

---

## 📊 Complete Workflow: From Scan to Fix

### **Example: Manager Scans a Terraform Repo**

```bash
# Manager's command
cd /home/jimmie/projects/my-terraform-infra
jade scan --type terraform
```

#### **What Happens Behind the Scenes:**

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Jade Calls Conftest Gate Agent                     │
├─────────────────────────────────────────────────────────────┤
│  → python conftest_gate_agent.py .                          │
│  → Finds 12 violations in Terraform plan                    │
│  → Returns JSON:                                             │
│    {                                                          │
│      "violations": [                                          │
│        {                                                      │
│          "policy": "terraform/s3_bucket_public",             │
│          "severity": "CRITICAL",                             │
│          "msg": "S3 bucket allows public access",            │
│          "file": "s3.tf:15"                                  │
│        },                                                     │
│        {                                                      │
│          "policy": "terraform/rds_unencrypted",              │
│          "severity": "HIGH",                                 │
│          "msg": "RDS database not encrypted",                │
│          "file": "rds.tf:42"                                 │
│        },                                                     │
│        ... (10 more violations)                              │
│      ]                                                        │
│    }                                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Jade AI Analyzes Violations                        │
├─────────────────────────────────────────────────────────────┤
│  Jade uses DeepSeek-Coder-V2 (code-specialized LLM) to:     │
│                                                               │
│  1. Group violations by type                                 │
│     → 3 S3 bucket issues                                     │
│     → 2 RDS encryption issues                                │
│     → 7 resource tagging issues                              │
│                                                               │
│  2. Assess severity & impact                                 │
│     → CRITICAL: 3 violations (public S3 buckets)             │
│     → HIGH: 2 violations (unencrypted databases)             │
│     → MEDIUM: 7 violations (missing tags)                    │
│                                                               │
│  3. Check RAG for similar past fixes                         │
│     → Query: "How did we fix S3 public buckets before?"      │
│     → RAG returns: "Applied guidepoint-secure-s3.tf module"  │
│                                                               │
│  4. Generate fix recommendations                             │
│     → CRITICAL fixes: Require human approval                 │
│     → HIGH fixes: Auto-fix in non-prod, approve in prod      │
│     → MEDIUM fixes: Auto-fix everywhere                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Jade Decides Escalation Strategy                   │
├─────────────────────────────────────────────────────────────┤
│  Decision Matrix (see GP-AI/approval/state_machine.py):     │
│                                                               │
│  IF severity == "CRITICAL":                                  │
│    → Create approval proposal                                │
│    → Show in Electron GUI approval queue                     │
│    → Wait for manager approval                               │
│    → Expiry: 24 hours                                        │
│                                                               │
│  IF severity == "HIGH" AND environment == "production":      │
│    → Create approval proposal                                │
│    → Expiry: 7 days                                          │
│                                                               │
│  IF severity == "HIGH" AND environment == "non-prod":        │
│    → Auto-fix (safe mutation)                                │
│    → Create PR for review                                    │
│    → Notify in approval queue (FYI)                          │
│                                                               │
│  IF severity == "MEDIUM" OR "LOW":                           │
│    → Auto-fix via Gatekeeper mutation                        │
│    → Log in activity tracker                                 │
│    → Include in daily summary                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Jade Creates Approval Proposals                    │
├─────────────────────────────────────────────────────────────┤
│  For the 3 CRITICAL S3 violations:                           │
│                                                               │
│  POST /api/v1/approvals/propose                              │
│  {                                                            │
│    "title": "Fix S3 Public Bucket Violations",               │
│    "severity": "critical",                                   │
│    "category": "security",                                   │
│    "proposed_changes": {                                     │
│      "files": ["s3.tf"],                                     │
│      "diff": "... (unified diff showing changes) ...",       │
│      "current_code": "... (vulnerable code) ...",            │
│      "proposed_code": "... (secure code with encryption) ..." │
│    },                                                         │
│    "risk_assessment": {                                      │
│      "severity": "critical",                                 │
│      "impact": "Data exposure risk",                         │
│      "affected_resources": ["my-app-bucket", "logs-bucket"], │
│      "compliance_impact": ["SOC2-CC6.1", "PCI-DSS-3.4"]      │
│    },                                                         │
│    "auto_execute": false,  // Requires human approval        │
│    "expiry_hours": 24                                        │
│  }                                                            │
│                                                               │
│  → Proposal ID: #1001                                        │
│  → Appears in Electron GUI approval queue                    │
│  → Manager gets desktop notification                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Manager Reviews in Approval Queue                  │
├─────────────────────────────────────────────────────────────┤
│  Manager opens Electron app → Approval Queue tab            │
│                                                               │
│  Sees:                                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Proposal #1001 [CRITICAL]                              │ │
│  │ Fix S3 Public Bucket Violations                        │ │
│  │                                                          │ │
│  │ Current Code (s3.tf:15):                               │ │
│  │   resource "aws_s3_bucket" "app" {                     │ │
│  │     bucket = "my-app-bucket"                           │ │
│  │     acl    = "public-read"  ← DANGEROUS!               │ │
│  │   }                                                      │ │
│  │                                                          │ │
│  │ Proposed Fix:                                           │ │
│  │   resource "aws_s3_bucket" "app" {                     │ │
│  │     bucket = "my-app-bucket"                           │ │
│  │     acl    = "private"                                 │ │
│  │   }                                                      │ │
│  │                                                          │ │
│  │   resource "aws_s3_bucket_public_access_block" "app" { │ │
│  │     bucket = aws_s3_bucket.app.id                      │ │
│  │     block_public_acls       = true                     │ │
│  │     block_public_policy     = true                     │ │
│  │     ignore_public_acls      = true                     │ │
│  │     restrict_public_buckets = true                     │ │
│  │   }                                                      │ │
│  │                                                          │ │
│  │ Compliance: SOC2-CC6.1, PCI-DSS-3.4                    │ │
│  │                                                          │ │
│  │ [Approve] [Reject] [Modify]                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Manager clicks [Approve]                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Jade Executes Approved Fix                         │
├─────────────────────────────────────────────────────────────┤
│  1. Update proposal state: pending → executing               │
│                                                               │
│  2. Apply fix to Terraform files                             │
│     → Edit s3.tf (add encryption, block public access)       │
│                                                               │
│  3. Run terraform validate                                   │
│     → Ensure syntax is correct                               │
│                                                               │
│  4. Create git commit                                         │
│     git add s3.tf                                            │
│     git commit -m "🔒 Fix S3 public bucket (Proposal #1001)" │
│                                                               │
│  5. Create PR (if configured)                                │
│     gh pr create --title "Fix S3 security violations"        │
│                                                               │
│  6. Update proposal state: executing → completed             │
│                                                               │
│  7. Log to activity tracker (RAG)                            │
│     → "Fixed 3 CRITICAL S3 violations in my-terraform-infra" │
│     → "Applied guidepoint-secure-s3.tf patterns"             │
│     → "Compliance: SOC2-CC6.1, PCI-DSS-3.4"                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Where You See Changes

### **1. In Your Git Repo (Local Files)**

```bash
# After Jade executes approved fix
cd /home/jimmie/projects/my-terraform-infra

# See modified files
git status
# modified:   s3.tf
# modified:   rds.tf

# View the diff
git diff s3.tf
# Shows: public ACL → private + encryption blocks added

# Check commit history
git log -1
# commit abc123...
# Author: Jade AI <jade@gp-copilot.local>
# Date:   Oct 3 2025
#
# 🔒 Fix S3 public bucket (Proposal #1001)
#
# Applied fixes:
# - s3.tf: Block public access, enable encryption
# - Compliance: SOC2-CC6.1, PCI-DSS-3.4
#
# 🤖 Generated with GP-Copilot
# Co-Authored-By: Manager <manager@company.com>
```

### **2. In Approval Queue (Electron GUI)**

Location: Electron App → Approval Queue Tab

```
┌──────────────────────────────────────────────────────────┐
│ APPROVAL QUEUE                            [3 Pending]     │
├──────────────────────────────────────────────────────────┤
│                                                            │
│ ✅ #1001 [CRITICAL] Fix S3 Public Bucket                  │
│    Status: Completed                                      │
│    Approved by: Manager                                   │
│    Executed: Oct 3, 2025 10:15 AM                        │
│    Files modified: s3.tf                                  │
│                                                            │
│ ⏳ #1002 [HIGH] Encrypt RDS Database                      │
│    Status: Pending Approval                               │
│    Expires in: 6 days                                     │
│    [View Details] [Approve] [Reject]                     │
│                                                            │
│ ⚙️  #1003 [MEDIUM] Add Required Tags                      │
│    Status: Auto-Executed                                  │
│    Completed: Oct 3, 2025 10:16 AM                       │
│    Files modified: main.tf, variables.tf                  │
│                                                            │
└──────────────────────────────────────────────────────────┘
```

### **3. In Activity Tracker (RAG Database)**

Query Jade: **"What did we do today?"**

```
Jade Response:

Today (October 3, 2025) we accomplished:

📊 Security Scans:
- Scanned my-terraform-infra (23 Terraform files)
- Found 12 violations (3 CRITICAL, 2 HIGH, 7 MEDIUM)

🔧 Fixes Applied:
- ✅ Fixed 3 CRITICAL S3 public bucket violations (Proposal #1001)
- ✅ Auto-fixed 7 MEDIUM tagging violations (Proposal #1003)
- ⏳ Pending approval: 2 HIGH RDS encryption violations (Proposal #1002)

📁 Files Modified:
- s3.tf (added encryption, blocked public access)
- main.tf (added compliance tags)
- variables.tf (added tag defaults)

📋 Compliance Impact:
- SOC2-CC6.1: 3 controls enforced
- PCI-DSS-3.4: 2 controls enforced
- CIS-AWS-1.2.0: 5 controls enforced

🎯 Next Steps:
- Review Proposal #1002 (RDS encryption) - expires in 6 days
- Deploy fixes to staging environment
- Run Gatekeeper audit on production K8s cluster
```

### **4. In Pull Request (GitHub/GitLab)**

If you have PR bot enabled:

```
Title: 🤖 Fix S3 Security Violations (Proposal #1001)

## Summary
Jade AI detected 3 CRITICAL S3 public bucket vulnerabilities and applied secure configurations.

## Changes
- ✅ Blocked public access on 2 S3 buckets
- ✅ Enabled encryption at rest (AES-256)
- ✅ Added bucket policies to enforce HTTPS

## Compliance
- SOC2-CC6.1 (Access Control)
- PCI-DSS-3.4 (Encryption at Rest)
- CIS-AWS-1.2.0-2.1.5 (S3 Bucket Public Access)

## Files Modified
- `s3.tf`: Added public access block + encryption
- `s3_policy.tf`: Added HTTPS-only policy

## Testing
- ✅ `terraform validate` passed
- ✅ `terraform plan` passed (no changes to existing resources)
- ✅ `conftest test` passed (0 violations)

## Approval Trail
- Proposed by: Jade AI
- Reviewed by: Manager (manager@company.com)
- Approved: Oct 3, 2025 10:14 AM
- Executed: Oct 3, 2025 10:15 AM

---
🤖 Generated by [GP-Copilot](https://github.com/linkops-industries/GP-copilot)
```

---

## 🎯 Decision Matrix: When Jade Escalates vs Auto-Fixes

### **Escalation Rules (Requires Manager Approval)**

| Condition | Action | Expiry | Example |
|-----------|--------|--------|---------|
| **CRITICAL** severity | Create approval proposal | 24 hours | Public S3 bucket, root user access |
| **HIGH** + production env | Create approval proposal | 7 days | Unencrypted RDS in prod |
| **Compliance violation** (SOC2, PCI) | Create approval proposal | 3 days | Missing audit logging |
| **Data at rest** encryption changes | Create approval proposal | 7 days | RDS/S3 encryption changes |
| **Network boundary** changes | Create approval proposal | 7 days | Security group rules, VPC changes |

### **Auto-Fix Rules (Jade Executes Immediately)**

| Condition | Action | Notification | Example |
|-----------|--------|--------------|---------|
| **MEDIUM/LOW** severity | Auto-fix via mutation | Activity log only | Missing resource tags |
| **HIGH** + non-prod env | Auto-fix + create PR | Approval queue (FYI) | Unencrypted RDS in dev |
| **Kubernetes** defaults | Gatekeeper mutation | Activity log only | runAsNonRoot, resource limits |
| **Terraform** formatting | Auto-fix | Activity log only | terraform fmt |
| **Policy drift** in staging | Auto-fix | Activity log only | Revert to baseline |

### **Progressive Rollout (Staged Enforcement)**

| Stage | Duration | Enforcement | Action |
|-------|----------|-------------|--------|
| **dryrun** | 7 days | Audit only | Collect violation data, no blocking |
| **warn** | 7 days | Log + warn | Alert teams, prepare fixes |
| **deny** | Permanent | Block violations | Full enforcement in production |

---

## 🚀 Real-World Usage Examples

### **Example 1: Scan a Terraform Repo**

```bash
# Manager's workstation
cd ~/projects/my-infra

# Run Jade scan
jade scan --type terraform

# Or use agent directly
python /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/conftest_gate_agent.py .

# Output shows:
# ❌ CONFTEST GATE FAILED
# Found 12 violations:
#   - [terraform/s3_bucket_public] S3 bucket allows public access (s3.tf:15)
#   - [terraform/rds_unencrypted] RDS not encrypted (rds.tf:42)
#   ...
#
# 🤖 Jade created 3 approval proposals
# 🔧 Jade auto-fixed 7 MEDIUM violations
# 📊 View details: http://localhost:8000/docs#/approvals/pending
```

### **Example 2: Daily Kubernetes Audit**

```bash
# Automated daily cron job
0 9 * * * cd /home/jimmie/linkops-industries/GP-copilot && \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/gatekeeper_audit_agent.py

# Jade receives audit results
# Finds 5 violations in production K8s cluster
#
# Jade decides:
# - 2 CRITICAL (privileged containers) → Create approval proposals
# - 3 MEDIUM (missing resource limits) → Auto-fix via Gatekeeper mutation
#
# Manager gets notification:
# "Jade found 5 violations. 2 require your approval, 3 auto-fixed."
```

### **Example 3: Progressive Rollout to Production**

```bash
# Jade orchestrates staged rollout
jade policy deploy pod-security-constraint.yaml --environment production

# Week 1: dryrun mode
# - Jade monitors violations
# - Collects data: "25 pods violate runAsNonRoot"
# - No blocking

# Week 2: warn mode
# - Jade creates PRs for fixes
# - Sends warnings to developers
# - Still not blocking

# Week 3: deny mode
# - Jade enforces policy
# - Blocks new privileged pods
# - Auto-fixes existing violations (after approval)
```

---

## 📝 How to View Jade's Decisions

### **Option 1: Electron GUI (Recommended)**

```bash
# Start Jade UI
cd /home/jimmie/linkops-industries/GP-copilot/GP-GUI
npm start

# Navigate to:
# - Approval Queue tab → See all proposals
# - Activity Dashboard → See daily summary
# - Secrets Manager → Configure integrations
```

### **Option 2: API (Programmatic)**

```bash
# Get pending approvals
curl http://localhost:8000/api/v1/approvals/pending

# Get approval details
curl http://localhost:8000/api/v1/approvals/1001

# Approve a proposal
curl -X POST http://localhost:8000/api/v1/approvals/1001/approve \
  -H "Content-Type: application/json" \
  -d '{"approver": "manager@company.com", "notes": "Looks good"}'
```

### **Option 3: Query RAG Database**

```bash
# Ask Jade
jade query "What violations did you find today?"
jade query "Show me all CRITICAL proposals"
jade query "What did we fix in my-terraform-infra?"
```

---

## 🔗 Integration Points

### **Jade AI Components That Work Together:**

```
┌─────────────────────────────────────────────────────────────┐
│                    JADE AI ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [Manager Command] → [Jade CLI]                              │
│           ↓                                                   │
│  [Jade AI Engine] ← [DeepSeek-Coder-V2 LLM]                 │
│           ↓                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Orchestrator: Decides which agent to call              │ │
│  └────────────────────────────────────────────────────────┘ │
│           ↓                                                   │
│  ┌───────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Conftest  │ Gatekeeper   │ PR Bot       │ Patch Rollout│ │
│  │ Gate      │ Audit        │ Agent        │ Agent        │ │
│  └───────────┴──────────────┴──────────────┴──────────────┘ │
│           ↓                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Decision Engine: Escalate or Auto-Fix?                 │ │
│  │ - Check severity (CRITICAL → approve, MEDIUM → auto)   │ │
│  │ - Check environment (prod → approve, dev → auto)       │ │
│  │ - Check compliance (SOC2 → approve)                    │ │
│  └────────────────────────────────────────────────────────┘ │
│           ↓                                                   │
│  ┌───────────────────┬────────────────────────────────────┐ │
│  │ Create Approval   │ Auto-Fix via                       │ │
│  │ Proposal          │ Gatekeeper Mutation                │ │
│  │ (state_machine.py)│ (patch_rollout_agent.py)           │ │
│  └───────────────────┴────────────────────────────────────┘ │
│           ↓                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Track in RAG (auto_sync.py)                            │ │
│  │ - What: "Fixed S3 public bucket"                       │ │
│  │ - When: "Oct 3, 2025 10:15 AM"                         │ │
│  │ - How: "Applied guidepoint-secure-s3.tf"               │ │
│  │ - Compliance: "SOC2-CC6.1, PCI-DSS-3.4"                │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 Key Takeaways

1. **Jade is the brain** - Agents are the hands
2. **Manager stays in control** - CRITICAL changes require approval
3. **Everything is tracked** - RAG remembers all decisions
4. **Progressive enforcement** - dryrun → warn → deny prevents breakage
5. **Compliance-aware** - Auto-maps fixes to SOC2, PCI, CIS controls

---

## 📚 Related Documentation

- [Approval State Machine](../../../GP-AI/approval/state_machine.py) - How proposals work
- [RAG Auto-Sync](../../../GP-RAG/auto_sync.py) - How activity is tracked
- [Jade AI Engine](../../../GP-AI/engines/ai_security_engine.py) - How decisions are made
- [VISION.md](../../../VISION.md) - Overall architecture

---

**Next Steps:**
1. Try scanning a Terraform repo: `jade scan --type terraform ~/projects/my-infra`
2. Review proposals in Electron GUI: `cd GP-GUI && npm start`
3. Query Jade: `jade query "What did we do today?"`