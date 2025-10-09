# Scan Results Guide

**Updated:** October 3, 2025
**Purpose:** Understand where scan results are saved and how Jade uses them

---

## 📁 Where Scan Results Are Saved

### **Primary Location: GP-DATA/active/scans/**

```
GP-DATA/active/scans/
├── opa_20251003_093751_571.json          # Latest OPA scan
├── opa_latest.json                        # Symlink to latest
├── bandit_latest.json                     # Latest Bandit scan
├── trivy_latest.json                      # Latest Trivy scan
├── semgrep_latest.json                    # Latest Semgrep scan
├── gitleaks_latest.json                   # Latest Gitleaks scan
└── conftest/                              # Conftest gate results
    ├── Terraform_CICD_Setup_20251003_093751.json
    └── Terraform_CICD_Setup_20251003_093751_report.txt
```

### **Example: Terraform_CICD_Setup Scan**

**Scan command:**
```bash
PYTHONPATH=GP-PLATFORM/james-config:$PYTHONPATH \
  python GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners/opa_scanner.py \
  GP-PROJECTS/Terraform_CICD_Setup \
  terraform-security
```

**Results:**
```json
{
  "findings": [],
  "summary": {
    "total": 0,
    "files_scanned": 7,
    "severity_breakdown": {
      "critical": 0,
      "high": 0,
      "medium": 0,
      "low": 0
    },
    "policy_package": "terraform-security"
  },
  "target": "GP-PROJECTS/Terraform_CICD_Setup",
  "tool": "opa",
  "timestamp": "2025-10-03T09:37:51.571461",
  "scan_id": "opa_20251003_093751_571"
}
```

✅ **Result: PASSED** - No violations found!

---

## 🔄 Data Flow: From Scan to Jade Decision

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SCAN EXECUTION                                            │
├─────────────────────────────────────────────────────────────┤
│ python opa_scanner.py GP-PROJECTS/Terraform_CICD_Setup      │
│ ↓                                                            │
│ Scans 7 Terraform files                                     │
│ Finds 0 violations                                          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. RESULTS SAVED TO GP-DATA                                  │
├─────────────────────────────────────────────────────────────┤
│ JSON: GP-DATA/active/scans/opa_20251003_093751_571.json    │
│ Link: GP-DATA/active/scans/opa_latest.json → latest scan    │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. GP-RAG AUTO-SYNC                                          │
├─────────────────────────────────────────────────────────────┤
│ File: GP-RAG/auto_sync.py                                   │
│ ↓                                                            │
│ Watches GP-DATA/active/scans/ for new files                 │
│ Auto-ingests scan results into:                             │
│   - ChromaDB vector database (semantic search)              │
│   - SQLite activity database (time-series queries)          │
│                                                              │
│ Indexed data:                                                │
│   - What: "Scanned Terraform_CICD_Setup"                    │
│   - When: "2025-10-03 09:37:51"                             │
│   - Result: "0 violations found"                            │
│   - Files: "7 Terraform files"                              │
│   - Tool: "OPA terraform-security policy"                   │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. JADE AI ANALYSIS (if violations found)                   │
├─────────────────────────────────────────────────────────────┤
│ File: GP-AI/engines/ai_security_engine.py                   │
│                                                              │
│ IF violations > 0:                                           │
│   ↓                                                          │
│   Jade reads scan results                                   │
│   Analyzes each violation:                                  │
│     - Severity (CRITICAL/HIGH/MEDIUM/LOW)                   │
│     - Environment (production/non-prod)                     │
│     - Compliance impact (SOC2, PCI, CIS)                    │
│   ↓                                                          │
│   Makes decision:                                            │
│     CRITICAL     → Create approval proposal (24h expiry)    │
│     HIGH + prod  → Create approval proposal (7d expiry)     │
│     HIGH + dev   → Auto-fix + create PR                     │
│     MEDIUM/LOW   → Auto-fix via mutation                    │
└────────────────────────┬────────────────────────────────────┘
                         ↓
         ┌───────────────┴───────────────┐
         ↓                               ↓
┌──────────────────┐            ┌──────────────────┐
│ 5a. ESCALATION   │            │ 5b. AUTO-FIX     │
├──────────────────┤            ├──────────────────┤
│ File:            │            │ File:            │
│ GP-AI/approval/  │            │ GP-CONSULTING-   │
│ state_machine.py │            │ AGENTS/fixers/   │
│                  │            │ opa_fixer.py     │
│ Create proposal  │            │                  │
│ in approval      │            │ Apply fixes via  │
│ queue            │            │ Gatekeeper       │
│                  │            │ mutation         │
│ Manager reviews  │            │                  │
│ in Electron GUI  │            │ Create PR        │
│                  │            │                  │
│ Approve/Reject   │            │ Log in activity  │
└──────────────────┘            └──────────────────┘
```

---

## 📊 Data Locations by Category

### **1. Raw Scans (JSON)**
**Location:** `GP-DATA/active/scans/`

**Files:**
- `opa_*.json` - OPA policy scans
- `bandit_*.json` - Python security scans
- `trivy_*.json` - Container/dependency scans
- `semgrep_*.json` - SAST scans
- `gitleaks_*.json` - Secret detection scans
- `checkov_*.json` - IaC security scans

**View latest:**
```bash
cat GP-DATA/active/scans/opa_latest.json | jq '.'
cat GP-DATA/active/scans/bandit_latest.json | jq '.'
```

### **2. Conftest Reports (Terraform Validation)**
**Location:** `GP-DATA/active/scans/conftest/`

**Files:**
- `{project}_*.json` - JSON results
- `{project}_*_report.txt` - Human-readable report

**Example:**
```bash
cat GP-DATA/active/scans/conftest/Terraform_CICD_Setup_*_report.txt
```

### **3. Audit Reports (Gatekeeper)**
**Location:** `GP-DATA/active/audit/`

**Files:**
- `gatekeeper_audit_*.txt` - Daily Kubernetes audits
- `gatekeeper_audit_*.json` - JSON format

**View:**
```bash
cat GP-DATA/active/audit/gatekeeper_audit_*_report.txt
```

### **4. Generated Fixes**
**Location:** `GP-DATA/active/fixes/`

**Files:**
- `fix_*.yaml` - Fixed Kubernetes manifests
- `fix_*.tf` - Fixed Terraform files
- `fix_*.json` - Fix metadata

### **5. Generated Policies**
**Location:** `GP-DATA/active/policies/generated/`

**Files:**
- `k8s_*.yaml` - Generated Gatekeeper ConstraintTemplates
- `opa_*.rego` - Generated OPA policies

---

## 🤖 How to Query Results

### **Option 1: Direct File Access**

```bash
# View latest OPA scan
cat GP-DATA/active/scans/opa_latest.json | jq '.summary'

# View all scans today
ls -lh GP-DATA/active/scans/*_$(date +%Y%m%d)*.json

# Count violations
cat GP-DATA/active/scans/opa_latest.json | jq '.summary.total'
```

### **Option 2: Query Jade AI (RAG)**

```bash
# Ask Jade what was scanned
jade query "What did we scan today?"

# Ask about specific project
jade query "Show me scan results for Terraform_CICD_Setup"

# Ask about violations
jade query "What CRITICAL violations did we find this week?"
```

### **Option 3: API (Programmatic)**

```bash
# Get scan history
curl http://localhost:8000/api/v1/scans/history

# Get latest scan by tool
curl http://localhost:8000/api/v1/scans/latest/opa

# Get scans by project
curl http://localhost:8000/api/v1/scans?project=Terraform_CICD_Setup
```

### **Option 4: Electron GUI**

```bash
# Start GUI
cd GP-GUI && npm start

# Navigate to:
# - Dashboard → See scan summary
# - Scans tab → Browse all scans
# - Approval Queue → See violations requiring approval
```

---

## 📈 Understanding Scan Results

### **Result Format (JSON)**

```json
{
  "findings": [
    {
      "severity": "CRITICAL",
      "msg": "S3 bucket allows public access",
      "file": "s3.tf:15",
      "policy": "terraform/s3_bucket_public",
      "compliance": ["SOC2-CC6.1", "PCI-DSS-3.4"]
    }
  ],
  "summary": {
    "total": 1,
    "files_scanned": 7,
    "severity_breakdown": {
      "critical": 1,
      "high": 0,
      "medium": 0,
      "low": 0
    }
  },
  "target": "GP-PROJECTS/Terraform_CICD_Setup",
  "tool": "opa",
  "timestamp": "2025-10-03T09:37:51",
  "scan_id": "opa_20251003_093751_571"
}
```

### **Severity Levels**

| Severity | Description | Jade Action |
|----------|-------------|-------------|
| **CRITICAL** | Data exposure, privilege escalation | Create approval proposal (24h expiry) |
| **HIGH** | Security misconfiguration | Approval (prod) or auto-fix (dev) |
| **MEDIUM** | Best practice violation | Auto-fix via mutation |
| **LOW** | Code quality issue | Auto-fix via mutation |

### **Compliance Mappings**

Violations automatically mapped to compliance frameworks:

- **SOC2**: Access control, encryption, logging
- **PCI-DSS**: Data protection, network security
- **CIS**: Kubernetes security benchmarks
- **NIST**: Access control, audit & accountability
- **HIPAA**: Healthcare data protection
- **GDPR**: Data privacy

---

## 🔍 Example: Finding Your Scan Results

```bash
# Scenario: You just scanned Terraform_CICD_Setup

# 1. Find the latest scan file
ls -lh GP-DATA/active/scans/opa_latest.json

# Output:
# lrwxrwxrwx ... opa_latest.json -> opa_20251003_093751_571.json

# 2. View the results
cat GP-DATA/active/scans/opa_latest.json | jq '.'

# 3. Check if violations found
cat GP-DATA/active/scans/opa_latest.json | jq '.summary.total'
# Output: 0

# 4. If violations found, check approval queue
curl http://localhost:8000/api/v1/approvals/pending | jq '.'

# 5. Query Jade about what happened
jade query "What did we scan today?"
# Output: "Scanned Terraform_CICD_Setup: 0 violations, 7 files, PASSED"
```

---

## 📚 Related Documentation

- **[JADE_INTEGRATION_GUIDE.md](../../GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/JADE_INTEGRATION_GUIDE.md)** - How Jade uses scan results
- **[QUICK_START.md](../../GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/agents/QUICK_START.md)** - Running scans
- **[GP-DATA Architecture](../README.md)** - Data storage design
- **[VISION.md](../../VISION.md)** - Overall system architecture

---

## 🆘 Troubleshooting

**Q: I scanned but don't see results in GP-DATA**

A: Check if the scan completed successfully:
```bash
echo $?  # Should be 0 for success
```

**Q: Results are not showing in Jade's approval queue**

A: Check if violations were found:
```bash
cat GP-DATA/active/scans/opa_latest.json | jq '.summary.total'
```

If 0, no approval needed! If > 0, check Jade is running:
```bash
curl http://localhost:8000/health
```

**Q: Where are old scan results?**

A: Archived after 30 days:
```bash
ls GP-DATA/archive/scans/
```

---

**All scan results flow through GP-DATA and are auto-synced to RAG for Jade to analyze!** 🚀