# GP-DATA - Centralized Data Repository & Evidence Storage

## Overview

GP-DATA is the **single source of truth for all GP-JADE platform data**. It serves as the centralized repository for security scan results, AI analysis outputs, automated fixes, compliance reports, and audit evidence.

**Purpose**: Evidence-based security operations with complete audit trails for compliance (SOC2, ISO27001, HIPAA, PCI-DSS).

**Status**: ✅ Production Ready - Complete Data Centralization
**Size**: ~6.8GB (134+ JSON scan results, reports, analysis)
**Last Updated**: 2025-10-07

---

## Directory Structure

```
GP-DATA/ (~6.8GB total)
├── active/                         # 🔴 Active Operations Data
│   ├── scans/                      # Security scan results (100+ files)
│   │   ├── bandit_*.json          # Python security scans
│   │   ├── trivy_*.json           # Vulnerability scans
│   │   ├── semgrep_*.json         # SAST results
│   │   ├── gitleaks_*.json        # Secrets detection
│   │   ├── checkov_*.json         # IaC security scans
│   │   ├── tfsec_*.json           # Terraform scans
│   │   ├── opa_*.json             # Policy violations
│   │   ├── kubescape_*.json       # Kubernetes security (deprecated)
│   │   ├── *_latest.json          # Symlinks to latest scans
│   │   ├── CLOUD-project/         # Project-specific scans
│   │   ├── manifests/             # Scanned K8s manifests
│   │   ├── raw/                   # Raw scanner outputs
│   │   ├── processed/             # Processed/normalized results
│   │   └── SCAN_RESULTS_GUIDE.md  # Scan results documentation
│   │
│   ├── reports/                    # Generated security reports
│   │   ├── CLOUD-project/         # Project-specific reports
│   │   ├── portfolio/             # Portfolio-level reports
│   │   ├── executive_summary_*.md # Executive summaries
│   │   ├── technical_report_*.md  # Technical details
│   │   ├── rag_summary_*.md       # AI-generated summaries
│   │   └── security_advice_*.json # Security advice from AI
│   │
│   ├── fixes/                      # Automated remediation results
│   │   ├── CLOUD-project/         # Project-specific fixes
│   │   ├── fixes_*.json           # Fix application results
│   │   ├── bandit_fix_report_*.json
│   │   ├── checkov_fix_report_*.json
│   │   └── opa_fixes_*.json       # OPA policy fixes
│   │
│   ├── policies/                   # Generated OPA policies
│   │   └── generated/             # Auto-generated policy files
│   │
│   ├── analysis/                   # AI analysis outputs
│   │   └── k8s_diagnosis_*.json   # Kubernetes diagnostics
│   │
│   ├── escalations/                # Manager escalation reports
│   │   └── escalation_*.json      # Critical issue escalations
│   │
│   ├── audit/                      # Audit trails and evidence
│   │   ├── jade-evidence.jsonl    # JADE AI decision log
│   │   ├── gatekeeper_audit_*.txt # Gatekeeper policy audits
│   │   └── [encrypted secrets]    # Secrets management
│   │
│   ├── workflows/                  # Workflow execution logs
│   │   └── workflow_*_complete.json
│   │
│   ├── chroma_db/                  # 🗄️ ChromaDB Vector Database
│   │   └── [vector embeddings]    # RAG knowledge base
│   │
│   └── deliverables/               # Client deliverables (empty)
│
├── archive/                        # 📦 Historical Data Archive
│   └── [old scans, reports]        # Archived after 90 days
│
├── knowledge-base/                 # 📚 Security Knowledge (deprecated)
│   ├── chroma/                     # Old ChromaDB location
│   ├── enhanced_security_knowledge.md
│   └── network_configuration.md
│   ⚠️  Note: Consolidated to GP-KNOWLEDGE-HUB
│
├── metadata/                       # 📋 Data Metadata
│   └── audits/                     # Audit metadata
│       └── codebase_audit_report.md
│
├── notes/                          # 📝 User Notes & Documentation
│   └── [user-created notes]        # Manual notes from sessions
│
├── research/                       # 🔬 RAG Research Outputs
│   └── [RAG evidence]              # AI research and learning data
│
├── simple_rag_query.py             # Quick RAG query tool
├── simple_sync.py                  # Vector DB sync utility
├── auto_sync_daemon.py             # Automated sync daemon
├── start_auto_sync.sh              # Auto-sync starter script
│
└── Documentation:
    ├── README.md                   # Original documentation
    ├── GP_DATA_ARCHITECTURE.md     # Architecture overview
    ├── CENTRALIZED_ARCHITECTURE.md # Centralization plan
    ├── OUTPUT_MAPPING.md           # Data flow mapping
    ├── AUTO_SYNC_COMPLETE.md       # Auto-sync implementation
    ├── JADE_INTEGRATION_STATUS.md  # JADE integration docs
    └── FINAL_ORGANIZATION_REPORT.md
```

---

## Data Flow

### Complete Platform Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                   External Sources                       │
│  (Projects, Scans, Analysis, User Actions)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┬───────────────────┐
        │                         │                   │
        ▼                         ▼                   ▼
┌───────────────┐      ┌──────────────────┐   ┌──────────────┐
│   Scanners    │      │   GP-AI Engine   │   │ User Actions │
│               │      │                  │   │              │
│ • Bandit      │      │ • Analysis       │   │ • Notes      │
│ • Trivy       │      │ • Remediation    │   │ • Decisions  │
│ • Semgrep     │      │ • Reports        │   │ • Approvals  │
│ • Gitleaks    │      │ • Advice         │   │              │
│ • OPA         │      │                  │   │              │
└───────┬───────┘      └─────────┬────────┘   └──────┬───────┘
        │                        │                    │
        │                        │                    │
        └────────────────────────┼────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │      GP-DATA/active/    │
                    │   (Centralized Storage) │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────┐
        │                        │                    │
        ▼                        ▼                    ▼
┌───────────────┐      ┌──────────────────┐   ┌──────────────┐
│ scans/        │      │ reports/         │   │ fixes/       │
│ (scanners)    │      │ (AI analysis)    │   │ (remediation)│
└───────┬───────┘      └─────────┬────────┘   └──────┬───────┘
        │                        │                    │
        └────────────────────────┼────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   chroma_db/           │
                    │   (Vector Embeddings)  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   audit/               │
                    │   (Evidence Trail)     │
                    └────────────────────────┘
```

### Scanner Data Flow

```
1. Scanner Execution (GP-CONSULTING/scanners/)
         ↓
2. Results Generation (JSON output)
         ↓
3. Save to GP-DATA/active/scans/{scanner}_TIMESTAMP.json
         ↓
4. Symlink to {scanner}_latest.json
         ↓
5. AI Analysis (GP-AI)
         ↓
6. Reports to GP-DATA/active/reports/
         ↓
7. Vector Embedding (chroma_db/)
         ↓
8. Audit Trail (audit/jade-evidence.jsonl)
```

---

## Data Categories

### 1. Security Scans (`active/scans/`)

**~134 JSON files (~5GB)**

**Scanners Integrated**:
- **Bandit** (Python security) - 15+ scans
- **Trivy** (Vulnerabilities) - 20+ scans
- **Semgrep** (SAST) - 10+ scans
- **Gitleaks** (Secrets) - 15+ scans
- **Checkov** (IaC) - 5+ scans
- **tfsec** (Terraform) - 8+ scans
- **OPA** (Policy) - 40+ scans
- **Kubescape** (K8s) - Deprecated, moved to kubescape
- **npm-audit** (Dependencies) - 3+ scans
- **kube-hunter** (K8s attack surface) - 2+ scans

**Naming Convention**:
```
{scanner}_{YYYYMMDD}_{HHMMSS}_{milliseconds}.json
{scanner}_latest.json (symlink)
```

**Example Scan Result**:
```json
{
  "scanner": "bandit",
  "timestamp": "2025-10-07T01:42:15.184",
  "project": "GP-PROJECTS/LinkOps-MLOps",
  "findings": [
    {
      "severity": "HIGH",
      "confidence": "HIGH",
      "issue": "Hardcoded password string",
      "file": "config.py",
      "line": 42,
      "code": "password = 'admin123'",
      "cwe": "CWE-259"
    }
  ],
  "summary": {
    "total": 110,
    "high": 15,
    "medium": 45,
    "low": 50
  }
}
```

### 2. Security Reports (`active/reports/`)

**Three Report Types**:

**Executive Summary** (`executive_summary_*.md`)
- High-level overview for management
- Risk quantification
- Compliance status
- Recommended actions

**Technical Report** (`technical_report_*.md`)
- Detailed findings
- Remediation steps
- Code examples
- CVSS scoring

**RAG Summary** (`rag_summary_*.md`)
- AI-generated insights
- Historical context
- Similar findings
- Best practices

**Example Executive Summary**:
```markdown
# Executive Security Summary - LinkOps-MLOps

**Date**: 2025-09-23
**Risk Level**: MEDIUM
**Compliance**: 67% SOC2 Compliant

## Key Findings
- 110 total security issues identified
- 15 HIGH severity (require immediate attention)
- 45 MEDIUM severity (address within 30 days)

## Top Risks
1. Hardcoded credentials (HIGH) - CWE-259
2. SQL injection vectors (HIGH) - CWE-89
3. Missing input validation (MEDIUM) - CWE-20

## Recommendations
1. Implement secrets management (HashiCorp Vault)
2. Add parameterized queries for all DB calls
3. Deploy input validation middleware

## Compliance Gaps
- SOC2 CC6.1: Encryption at rest (MISSING)
- PCI-DSS 3.4: Masking of PANs (PARTIAL)
```

### 3. Automated Fixes (`active/fixes/`)

**Fix Application Results**

```json
{
  "timestamp": "2025-09-24T12:19:01",
  "scanner": "bandit",
  "fixes_applied": 12,
  "fixes_failed": 3,
  "details": [
    {
      "file": "config.py",
      "line": 42,
      "issue": "Hardcoded password",
      "fix": "Moved to environment variable",
      "status": "SUCCESS",
      "verification": "PASSED"
    }
  ],
  "commit": {
    "sha": "abc123",
    "message": "security: Remove hardcoded credentials"
  }
}
```

### 4. Vector Database (`active/chroma_db/`)

**ChromaDB - THE single vector database**

```
chroma_db/
├── chroma.sqlite3           # Metadata store
└── [UUID]/                  # Vector embeddings
    ├── data_level0.bin      # Embedding vectors (768-dim)
    ├── header.bin           # Index headers
    ├── length.bin           # Document lengths
    └── link_lists.bin       # Similarity links
```

**Contents**:
- **Security documentation** (~35 docs)
- **Scan results** (indexed for RAG)
- **Policy documents** (~9 docs)
- **Tool documentation** (~27 docs)
- **Project workflows** (~129 docs)

**Total**: 200+ embedded documents

**Usage**:
```python
from chromadb import PersistentClient
from GP_PLATFORM.james_config.gp_data_config import CHROMADB_PATH

client = PersistentClient(path=CHROMADB_PATH)
collection = client.get_collection("jade-knowledge")

# Query
results = collection.query(
    query_texts=["Kubernetes pod security best practices"],
    n_results=5
)
```

### 5. Audit Trail (`active/audit/`)

**jade-evidence.jsonl** - JADE AI decision log

```jsonl
{"timestamp":"2025-10-07T01:42:15Z","action":"scan","target":"LinkOps-MLOps","status":"success","findings":110,"llm_confidence":0.87}
{"timestamp":"2025-10-07T01:45:30Z","action":"analyze","scan_id":"scan_123","status":"success","risk_score":7.5}
{"timestamp":"2025-10-07T01:48:12Z","action":"fix","finding_id":"finding_456","status":"success","verification":"passed"}
```

**gatekeeper_audit_*.txt** - OPA Gatekeeper policy audits

```
[2025-10-06 21:00:00] Policy: pod-security-constraint
[2025-10-06 21:00:00] Status: PASS
[2025-10-06 21:00:00] Violations: 0
[2025-10-06 21:00:00] Resources Checked: 15
```

---

## Data Lifecycle

### Scan Result Lifecycle

```
1. Scanner Execution
   └─→ GP-CONSULTING/scanners/{scanner}_scanner.py
         ↓
2. Result Generation
   └─→ JSON output with findings
         ↓
3. Storage
   └─→ GP-DATA/active/scans/{scanner}_{timestamp}.json
         ↓
4. Indexing
   └─→ Create symlink: {scanner}_latest.json
         ↓
5. AI Analysis
   └─→ GP-AI analyzes findings
         ↓
6. Report Generation
   └─→ GP-DATA/active/reports/executive_summary_*.md
         ↓
7. Vector Embedding
   └─→ Embed in chroma_db/ for RAG
         ↓
8. Audit Logging
   └─→ Log to audit/jade-evidence.jsonl
         ↓
9. Archive (90 days)
   └─→ Move to archive/
```

### Fix Application Lifecycle

```
1. User Request
   └─→ "Fix issue #123"
         ↓
2. Fix Generation
   └─→ GP-CONSULTING/fixers/{scanner}_fixer.py
         ↓
3. Fix Application
   └─→ Apply code changes
         ↓
4. Verification
   └─→ Re-scan to verify fix
         ↓
5. Storage
   └─→ GP-DATA/active/fixes/fixes_{timestamp}.json
         ↓
6. Audit Log
   └─→ audit/jade-evidence.jsonl
         ↓
7. Git Commit
   └─→ Create commit with fix
```

---

## Data Access Patterns

### 1. Query Latest Scan

```bash
# View latest scan for specific scanner
cat GP-DATA/active/scans/bandit_latest.json | jq .

# Or by timestamp
cat $(ls -t GP-DATA/active/scans/bandit_*.json | head -1) | jq .
```

### 2. Query Vector Database

```python
from GP_DATA.simple_rag_query import query_knowledge

results = query_knowledge("How to fix SQL injection?")
for doc in results:
    print(f"Source: {doc['metadata']['source']}")
    print(f"Content: {doc['content']}")
```

### 3. Query Audit Trail

```bash
# View recent JADE actions
tail -20 GP-DATA/active/audit/jade-evidence.jsonl | jq .

# Filter by action
jq 'select(.action=="scan")' GP-DATA/active/audit/jade-evidence.jsonl

# Get error rate
jq -s '[.[] | select(.status=="error")] | length' GP-DATA/active/audit/jade-evidence.jsonl
```

### 4. Query via API

```bash
# Get latest scan
curl http://localhost:8000/api/scans/latest

# Get specific scanner results
curl http://localhost:8000/api/scans/bandit

# Get report
curl http://localhost:8000/api/reports/executive/LinkOps-MLOps
```

---

## Utilities

### simple_rag_query.py

**Quick RAG query tool**

```bash
# Query knowledge base
python GP-DATA/simple_rag_query.py "Kubernetes security best practices"

# With specific collection
python GP-DATA/simple_rag_query.py --collection jade-knowledge --query "OPA policies"
```

### simple_sync.py

**Vector DB sync utility**

```bash
# Sync all new documents to vector DB
python GP-DATA/simple_sync.py

# Verify vector DB integrity
python GP-DATA/simple_sync.py --verify

# Rebuild from scratch
python GP-DATA/simple_sync.py --rebuild
```

### auto_sync_daemon.py

**Automated sync daemon**

```bash
# Start auto-sync daemon (watches for new files)
./start_auto_sync.sh

# Or run directly
python GP-DATA/auto_sync_daemon.py --watch active/scans/

# Logs to: active/logs/auto_sync.log
```

---

## Compliance & Audit

### SOC2 Type II Requirements

**✅ Met Requirements**:
- **CC6.1**: Logical and physical access controls
  - Evidence: `audit/jade-evidence.jsonl`
- **CC7.2**: System monitoring
  - Evidence: Scan results, continuous monitoring
- **CC8.1**: Change management
  - Evidence: Fix reports, git commits

### ISO27001 Controls

**✅ Met Controls**:
- **A.12.6.1**: Management of technical vulnerabilities
  - Evidence: Scan results, remediation tracking
- **A.14.2.8**: System security testing
  - Evidence: Automated scanning, 100+ scans
- **A.18.2.1**: Review of information security
  - Evidence: Executive summaries, regular reports

### HIPAA Security Rule

**✅ Met Requirements**:
- **§164.308(a)(8)**: Evaluation
  - Evidence: Security assessments, scan logs
- **§164.308(a)(1)(ii)(B)**: Risk management
  - Evidence: Risk scoring, prioritization
- **§164.312(b)**: Audit controls
  - Evidence: Complete audit trail

### PCI-DSS v4.0

**✅ Met Requirements**:
- **11.3**: Vulnerability scans
  - Evidence: Quarterly scans, continuous monitoring
- **11.3.1**: Internal vulnerability scans
  - Evidence: All scan results
- **11.3.2**: Authenticated scanning
  - Evidence: Credentialed scans (Trivy, Checkov)

---

## Data Retention Policy

### Active Data (0-90 days)

- **Location**: `active/`
- **Access**: High-frequency queries
- **Backup**: Daily incremental

### Archived Data (90+ days)

- **Location**: `archive/`
- **Access**: Historical analysis only
- **Backup**: Monthly full backup
- **Compression**: gzip compressed

### Audit Data (7 years)

- **Location**: `active/audit/`
- **Retention**: 7 years (compliance requirement)
- **Backup**: Immutable backups
- **Encryption**: AES-256 at rest

---

## Storage Statistics

| Category | Files | Size | Growth Rate |
|----------|-------|------|-------------|
| **Scans** | 134 | ~5GB | ~100MB/week |
| **Reports** | 25 | ~50MB | ~5MB/week |
| **Fixes** | 10 | ~10MB | ~1MB/week |
| **Vector DB** | 200+ docs | ~1GB | ~50MB/month |
| **Audit** | 1 | ~500KB | ~10KB/day |
| **Total** | 370+ | **~6.8GB** | ~120MB/week |

---

## Maintenance Tasks

### Daily

```bash
# Check disk space
df -h GP-DATA/

# Verify latest scans
ls -lth GP-DATA/active/scans/*_latest.json

# Check auto-sync status
systemctl status gp-auto-sync  # if running as service
```

### Weekly

```bash
# Sync vector DB
python GP-DATA/simple_sync.py

# Verify audit integrity
python -c "
from GP_PLATFORM.core.jade_logger import get_logger
logger = get_logger()
print(logger.verify_integrity())
"

# Backup critical data
tar -czf gp-data-backup-$(date +%Y%m%d).tar.gz \
  GP-DATA/active/audit/ \
  GP-DATA/active/chroma_db/
```

### Monthly

```bash
# Archive old scans (>90 days)
find GP-DATA/active/scans/ -name "*.json" -mtime +90 -exec mv {} GP-DATA/archive/ \;

# Compress archives
find GP-DATA/archive/ -name "*.json" -exec gzip {} \;

# Generate compliance report
python GP-CONSULTING/reports/generate_compliance_report.py \
  --period monthly \
  --output GP-DATA/active/reports/compliance/
```

---

## Troubleshooting

### Missing Scan Results

```bash
# Check if scanner ran
ls -la GP-DATA/active/scans/{scanner}_*.json

# Check scanner logs
journalctl -u gp-scanner | tail -50

# Re-run scanner
python GP-CONSULTING/scanners/{scanner}_scanner.py GP-PROJECTS/MyApp
```

### Vector DB Issues

```bash
# Check ChromaDB health
python -c "
from chromadb import PersistentClient
from GP_PLATFORM.james_config.gp_data_config import CHROMADB_PATH
client = PersistentClient(path=CHROMADB_PATH)
collection = client.get_collection('jade-knowledge')
print(f'Documents: {collection.count()}')
"

# Rebuild if corrupted
python GP-DATA/simple_sync.py --rebuild
```

### Audit Log Integrity

```bash
# Verify integrity
python -c "
from GP_PLATFORM.core.jade_logger import get_logger
logger = get_logger()
integrity = logger.verify_integrity()
print(f'Valid: {integrity['valid_events']}/{integrity['total_events']}')
if integrity['tampered']:
    print('⚠️  Tampered events detected!')
"
```

---

## Integration Points

### Scanners → GP-DATA

```python
# GP-CONSULTING/scanners/bandit_scanner.py
from GP_PLATFORM.james_config.gp_data_config import ACTIVE_SCANS_DIR

output_path = f"{ACTIVE_SCANS_DIR}/bandit_{timestamp}.json"
with open(output_path, 'w') as f:
    json.dump(scan_results, f)
```

### GP-AI → GP-DATA

```python
# GP-AI/core/ai_security_engine.py
from GP_PLATFORM.james_config.gp_data_config import ACTIVE_REPORTS_DIR

report_path = f"{ACTIVE_REPORTS_DIR}/executive_summary_{timestamp}.md"
with open(report_path, 'w') as f:
    f.write(generate_executive_summary(findings))
```

### JADE Chat → GP-DATA

```python
# GP-AI/cli/jade_chat.py
from GP_PLATFORM.core.jade_logger import get_logger

logger = get_logger()
logger.log_event("chat_query", {
    "question": user_input,
    "confidence": 0.87
})
```

---

## Related Components

- **[GP-PLATFORM/](../GP-PLATFORM/)** - james-config defines GP-DATA paths
- **[GP-CONSULTING/](../GP-CONSULTING/)** - All scanners write to GP-DATA
- **[GP-AI/](../GP-AI/)** - Reads GP-DATA for analysis, writes reports
- **[GP-KNOWLEDGE-HUB/](../GP-KNOWLEDGE-HUB/)** - Consolidated knowledge base
- **[gp-security](../gp-security)** - Wrapper that uses GP-DATA paths

---

## Quick Reference

```bash
# View latest scan
cat GP-DATA/active/scans/bandit_latest.json | jq .

# Query RAG
python GP-DATA/simple_rag_query.py "Your question"

# Sync vector DB
python GP-DATA/simple_sync.py

# Start auto-sync
./GP-DATA/start_auto_sync.sh

# Check audit trail
tail -f GP-DATA/active/audit/jade-evidence.jsonl | jq .

# Archive old data
find GP-DATA/active/scans/ -mtime +90 -exec mv {} GP-DATA/archive/ \;

# Backup critical data
tar -czf gp-data-backup.tar.gz GP-DATA/active/audit/ GP-DATA/active/chroma_db/
```

---

**Status**: ✅ Production Ready - Complete Data Centralization
**Last Updated**: 2025-10-07
**Total Size**: ~6.8GB (134+ scan results, 200+ vector docs)
**Retention**: 90 days active, 7 years audit
**Compliance**: SOC2, ISO27001, HIPAA, PCI-DSS compliant
**Maintained by**: LinkOps Industries - JADE AI Security Platform Team