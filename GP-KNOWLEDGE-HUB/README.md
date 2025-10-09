# 🧠 GP-KNOWLEDGE-HUB - Centralized Knowledge Management System

## Overview

GP-KNOWLEDGE-HUB is the **single source of truth** for all security knowledge in the GP-JADE platform. It consolidates security documentation, policies, tools, and workflows from across the platform into one centralized, searchable knowledge base.

**Status**: ✅ Active (Consolidated from scattered locations)
**Size**: ~4.1MB (202 files)
**Last Consolidation**: 2025-09-29

---

## Directory Structure

```
GP-KNOWLEDGE-HUB/ (~4.1MB, 202 files)
├── knowledge-base/              # 📚 Organized Knowledge Repository
│   ├── security/                # Security guides and documentation (35 files)
│   │   ├── *_security_guide.md
│   │   ├── *_vulnerability_*.md
│   │   └── security_index.md
│   │
│   ├── policies/                # Security policies and OPA rules (9 files)
│   │   ├── COMPLIANCE_MAPPINGS.md
│   │   ├── THREAT_MODEL.md
│   │   ├── gatekeeper_comprehensive_explanation.md
│   │   └── policies_index.md
│   │
│   ├── tools/                   # Scanner/Fixer documentation (27 files)
│   │   ├── *_scanner.py (copied for reference)
│   │   ├── *_fixer.py (copied for reference)
│   │   ├── *_security_guide.md
│   │   └── tools_index.md
│   │
│   ├── workflows/               # Project documentation and workflows (129 files)
│   │   ├── GP-PROJECTS_* (project-specific docs)
│   │   ├── gatekeeper_*.md
│   │   └── workflows_index.md
│   │
│   └── compliance/              # Compliance frameworks (empty - TBD)
│
├── api/                         # 🌐 Knowledge Access API
│   ├── knowledge_api.py         # FastAPI knowledge query endpoint
│   ├── jade_central_config.py  # Configuration for knowledge access
│   └── __pycache__/
│
├── ingest/                      # 📥 Knowledge Ingestion Pipeline
│   ├── add-new-knowledge.py     # Add new documents to knowledge base
│   └── consolidate-knowledge.py # Consolidate from scattered sources
│
├── sync/                        # 🔄 Cleanup & Maintenance
│   └── cleanup-scattered-vectors.py  # Remove duplicate vector DBs
│
├── backups/                     # 💾 Historical Backups
│   └── vector-cleanup-20250929_091332/
│
├── knowledge_mapping.json       # 📋 Knowledge source mapping
├── consolidation_report_*.md    # 📊 Consolidation reports
├── vector_cleanup_report_*.md   # 🧹 Cleanup reports
└── DEPRECATED.md               # ⚠️ Migration guide from old locations
```

---

## Purpose & Philosophy

### The Problem Before GP-KNOWLEDGE-HUB

Knowledge was **scattered** across:
- `GP-DATA/knowledge-base/`
- `GP-RAG/processed/`
- `GP-CONSULTING/policies/`
- `GP-PROJECTS/*/docs/`
- Multiple vector databases in different locations

**Result**: Duplication, inconsistency, hard to maintain

### The Solution: Single Source of Truth

```
┌─────────────────────────────────────────────────────┐
│              GP-KNOWLEDGE-HUB                       │
│         (Single Source of Truth)                    │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┬──────────────────┐
        │                         │                  │
        ▼                         ▼                  ▼
┌───────────────┐      ┌──────────────────┐   ┌──────────┐
│   GP-AI/RAG   │      │   GP-CONSULTING  │   │  JADE    │
│   (Queries)   │      │   (References)   │   │  (Chat)  │
└───────────────┘      └──────────────────┘   └──────────┘
```

**Benefits**:
1. ✅ **Single Location**: All knowledge in one place
2. ✅ **No Duplication**: Each document exists once
3. ✅ **Easy Updates**: Modify in one location
4. ✅ **Consistent Access**: All tools read from same source
5. ✅ **Version Control**: Track all knowledge changes
6. ✅ **Searchable**: Indexed and categorized

---

## Knowledge Base Categories

### 1. Security (`knowledge-base/security/`)

**35 security documents** covering:
- **Vulnerability Guides**: CVE analysis, remediation strategies
- **Security Best Practices**: Kubernetes, Terraform, OPA
- **Comprehensive Guides**: IaC security, cloud security
- **Tool-Specific Guides**: Bandit, Trivy, Checkov, Semgrep
- **Architecture Docs**: CCSP, cloud migration, testing standards

**Key Files**:
```
advanced_kubernetes_opa_security.md
comprehensive_iac_terraform_opa_guide.md
kubernetes_security_comprehensive.md
terraform_security_guide.md
expanded_security_iac_corpus.md
```

### 2. Policies (`knowledge-base/policies/`)

**9 policy documents** including:
- **Compliance Mappings**: Map findings to frameworks (CIS, NIST, PCI-DSS)
- **Threat Models**: Attack path analysis
- **OPA Integration**: Kubernetes admission control
- **Gatekeeper**: Comprehensive policy enforcement guide
- **GuidePoint Standards**: Engagement methodology

**Key Files**:
```
COMPLIANCE_MAPPINGS.md
THREAT_MODEL.md
gatekeeper_comprehensive_explanation.md
GUIDEPOINT_ENGAGEMENT_GUIDE.md
```

### 3. Tools (`knowledge-base/tools/`)

**27 tool references** (scanners + fixers):
- **Scanners**: bandit, semgrep, trivy, gitleaks, checkov, tfsec, OPA
- **Fixers**: Automated remediation scripts for each scanner
- **Guides**: Tool usage, configuration, best practices

**Key Files**:
```
*_scanner.py (reference copies)
*_fixer.py (reference copies)
semgrep_gitleaks_security_guide.md
trivy_comprehensive_guide.md
```

### 4. Workflows (`knowledge-base/workflows/`)

**129 workflow documents** from projects:
- **GP-PROJECTS Documentation**: LinkOps-MLOps, DVWA, Terraform setups
- **Deployment Guides**: CI/CD, GitHub Actions, Kubernetes
- **Security Reports**: Vulnerability assessments, remediation reports
- **Architecture Docs**: Microservices, data flows, system designs

**Key Files**:
```
gatekeeper_complete_flow.md
GP-PROJECTS_LinkOps-MLOps_*.md (80+ files)
GP-PROJECTS_DVWA_*.md (15+ files)
GP-PROJECTS_Terraform_CICD_Setup_*.md (10+ files)
```

### 5. Compliance (`knowledge-base/compliance/`)

**Planned** for future:
- CIS Benchmarks
- NIST frameworks
- PCI-DSS requirements
- HIPAA guidelines
- SOC 2 controls

---

## API Access (`api/`)

### Knowledge API (`knowledge_api.py`)

FastAPI-based REST API for querying the knowledge base:

```python
# Start API server
cd GP-KNOWLEDGE-HUB/api
uvicorn knowledge_api:app --reload --port 8100

# Query knowledge
curl -X POST http://localhost:8100/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How to fix SQL injection in Python?"}'
```

**Endpoints**:
- `POST /query` - Search knowledge base
- `GET /categories` - List all categories
- `GET /documents/{category}` - List documents in category
- `GET /document/{path}` - Retrieve specific document

### Central Configuration (`jade_central_config.py`)

Unified configuration for knowledge access across all platform components.

---

## Ingestion Pipeline (`ingest/`)

### Add New Knowledge (`add-new-knowledge.py`)

```bash
# Add a new document to the knowledge base
python ingest/add-new-knowledge.py \
  --source /path/to/document.md \
  --category security \
  --index

# Add multiple documents
python ingest/add-new-knowledge.py \
  --source-dir /path/to/docs/ \
  --category policies \
  --index
```

### Consolidate Knowledge (`consolidate-knowledge.py`)

```bash
# Consolidate from scattered sources (one-time migration)
python ingest/consolidate-knowledge.py

# Outputs:
# - Copies files to knowledge-base/
# - Generates consolidation_report_*.md
# - Updates knowledge_mapping.json
```

**Sources Consolidated**:
- `GP-DATA/knowledge-base/` → `GP-KNOWLEDGE-HUB/knowledge-base/security/`
- `GP-CONSULTING/policies/` → `GP-KNOWLEDGE-HUB/knowledge-base/policies/`
- `GP-CONSULTING/fixers/` → `GP-KNOWLEDGE-HUB/knowledge-base/tools/`
- `GP-PROJECTS/*/docs/` → `GP-KNOWLEDGE-HUB/knowledge-base/workflows/`

---

## Sync & Maintenance (`sync/`)

### Cleanup Scattered Vectors (`cleanup-scattered-vectors.py`)

```bash
# Remove duplicate vector databases from old locations
python sync/cleanup-scattered-vectors.py

# Creates backup before deletion
# Generates vector_cleanup_report_*.md
```

**Removed Locations**:
- `GP-DATA/active/vector-db/`
- `GP-RAG/vector-db/`
- `GP-CONSULTING/vector-db/`

**Kept Location**:
- `GP-DATA/active/chroma_db/` (THE single vector database)

---

## Workflow & Integration

### How Knowledge Flows

```
1. New Knowledge Source (scan results, docs, reports)
         ↓
2. Ingestion Pipeline (add-new-knowledge.py)
         ↓
3. Knowledge Base (knowledge-base/{category}/)
         ↓
4. Vector Database (GP-DATA/active/chroma_db/)
         ↓
5. RAG Engine (GP-AI/core/rag_engine.py)
         ↓
6. AI Analysis (GP-AI/core/ai_security_engine.py)
         ↓
7. User Query Response (Jade Chat, API)
```

### Integration Points

**Consumers (Read from this hub)**:
- **GP-AI/RAG**: Semantic search via ChromaDB
- **JADE Chat**: Knowledge-augmented responses
- **GP-CONSULTING**: Reference policies and guides
- **API Clients**: External tools querying knowledge

**Producers (Write to this hub)**:
- **Scan Results**: GP-DATA/active/results/ → security/
- **Security Reports**: GP-DATA/active/reports/ → security/
- **Project Docs**: GP-PROJECTS/ → workflows/
- **Manual Additions**: via add-new-knowledge.py

---

## Key Files

### Configuration & Mapping

**knowledge_mapping.json**
```json
{
  "source_mappings": {
    "GP-DATA/knowledge-base/": "knowledge-base/security/",
    "GP-CONSULTING/policies/": "knowledge-base/policies/",
    "GP-PROJECTS/*/docs/": "knowledge-base/workflows/"
  },
  "categories": ["security", "policies", "tools", "workflows", "compliance"],
  "total_files": 202
}
```

**DEPRECATED.md**
Migration guide explaining old locations and new structure.

### Reports

**consolidation_report_20250929_092724.md**
- Files consolidated: 202
- Categories created: 4
- Duplicates removed: 15
- Total size: 4.1MB

**vector_cleanup_report_20250929_091337.md**
- Vector DBs removed: 3
- Backup created: backups/vector-cleanup-20250929_091332/
- Single vector DB: GP-DATA/active/chroma_db/

---

## Usage Examples

### Query Knowledge via Python

```python
from GP_KNOWLEDGE_HUB.api.knowledge_api import search_knowledge

results = search_knowledge(
    query="How to remediate SQL injection in Python?",
    category="security",
    limit=5
)

for doc in results:
    print(f"Title: {doc['title']}")
    print(f"Content: {doc['content'][:200]}...")
    print(f"Score: {doc['score']}")
```

### Access via JADE Chat

```bash
# Jade automatically uses knowledge hub
jade chat

> "Show me Kubernetes security best practices"
# Jade queries GP-KNOWLEDGE-HUB → Returns relevant docs

> "How do I fix CVE-2024-1234?"
# Jade searches security/ category → Provides remediation
```

### Add New Security Document

```bash
# Add a new security guide
python ingest/add-new-knowledge.py \
  --source my_security_guide.md \
  --category security \
  --title "Advanced Container Security" \
  --tags "docker,containers,security" \
  --index

# Automatically:
# 1. Copies to knowledge-base/security/
# 2. Updates index
# 3. Triggers vector DB update
```

---

## Maintenance Tasks

### Regular Maintenance

```bash
# Weekly: Verify index integrity
python sync/verify-knowledge-index.py

# Monthly: Consolidate new project docs
python ingest/consolidate-knowledge.py --incremental

# As Needed: Rebuild vector DB
cd ../GP-DATA && python simple_sync.py
```

### Troubleshooting

**Knowledge not found in RAG queries**
```bash
# Check if document exists
ls knowledge-base/security/my_doc.md

# Verify vector DB is up to date
cd ../GP-DATA && python simple_sync.py

# Check RAG engine connection
python -c "from GP_AI.core.rag_engine import RAGEngine; rag = RAGEngine(); print(rag.query('test'))"
```

**Duplicate documents**
```bash
# Find duplicates
find knowledge-base/ -type f -exec md5sum {} \; | sort | uniq -d -w32

# Remove duplicates (careful!)
python sync/remove-duplicates.py --dry-run
```

---

## Knowledge Statistics

| Category | Files | Size | Types |
|----------|-------|------|-------|
| **security/** | 35 | ~2.5MB | Guides, CVE analyses, best practices |
| **policies/** | 9 | ~500KB | Compliance, threat models, OPA rules |
| **tools/** | 27 | ~600KB | Scanner/fixer references |
| **workflows/** | 129 | ~1.5MB | Project docs, deployment guides |
| **compliance/** | 0 | 0 | (Planned) |
| **TOTAL** | **202** | **~4.1MB** | Mixed markdown + Python |

---

## Migration History

### Consolidation (2025-09-29)

**Before**:
- Knowledge scattered across 5+ directories
- 3 duplicate vector databases
- Inconsistent naming and organization

**After**:
- Single knowledge-base/ directory
- 1 vector database (GP-DATA/active/chroma_db/)
- Organized by category with indexes

**Removed Locations**:
- ❌ `GP-DATA/knowledge-base/` → Moved to `GP-KNOWLEDGE-HUB/knowledge-base/security/`
- ❌ `GP-RAG/processed/` → Moved to `GP-KNOWLEDGE-HUB/knowledge-base/security/`
- ❌ `GP-CONSULTING/policies/` → Moved to `GP-KNOWLEDGE-HUB/knowledge-base/policies/`

---

## Future Enhancements

### Planned Features

- [ ] **Automated Ingestion**: Watch GP-DATA for new scan results
- [ ] **Knowledge Versioning**: Track document changes over time
- [ ] **Compliance Section**: Add CIS, NIST, PCI-DSS frameworks
- [ ] **Search API Improvements**: Advanced filtering and ranking
- [ ] **Knowledge Validation**: Automated quality checks
- [ ] **Usage Analytics**: Track which knowledge is most queried

### Potential Additions

- [ ] **Interactive Knowledge Browser**: Web UI for browsing
- [ ] **Knowledge Graph**: Relationships between documents
- [ ] **Auto-Summarization**: LLM-generated document summaries
- [ ] **External Sources**: Integrate NIST NVD, MITRE ATT&CK

---

## Related Components

- **[GP-DATA/](../GP-DATA/)** - Data storage and vector DB
- **[GP-AI/](../GP-AI/)** - RAG engine and AI analysis
- **[GP-CONSULTING/](../GP-CONSULTING/)** - References policies/tools
- **[GP-RAG/](../GP-RAG/)** - Document processing pipelines
- **[GP-DOCS/](../GP-DOCS/)** - Platform documentation

---

## Quick Reference

```bash
# Query knowledge base
curl -X POST http://localhost:8100/query -d '{"question": "..."}'

# Add new document
python ingest/add-new-knowledge.py --source doc.md --category security

# Consolidate scattered knowledge (one-time)
python ingest/consolidate-knowledge.py

# Cleanup duplicate vectors
python sync/cleanup-scattered-vectors.py

# Rebuild vector DB
cd ../GP-DATA && python simple_sync.py
```

---

**Status**: ✅ Production Ready (Consolidated & Organized)
**Last Updated**: 2025-10-07
**Total Knowledge**: 202 files (~4.1MB)
**Maintained by**: LinkOps Industries - JADE AI Security Platform Team