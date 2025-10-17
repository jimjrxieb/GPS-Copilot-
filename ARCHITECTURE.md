# GP-Copilot Architecture v2.0

**Date:** 2025-10-16
**Status:** Reorganized - 5 Pillar Architecture
**Previous:** Cluttered single-level structure
**Current:** Clean pillar-based organization

---

## 🏛️ Five Pillar Architecture

```
GP-copilot/
├── GP-Backend/        # Backend services (RAG, Knowledge, Testing)
├── GP-CONSULTING/     # Security framework (Phases 1-6)
├── GP-DATA/           # All data storage (findings, reports, knowledge)
├── GP-Frontend/       # AI orchestration & user interfaces
└── GP-PROJECTS/       # Client project sandboxes
```

---

## 📁 Pillar 1: GP-Backend

**Purpose:** Backend processing, knowledge management, testing infrastructure

```
GP-Backend/
├── GP-KNOWLEDGE-HUB/     # Central knowledge repository
│   ├── api/              # Knowledge API endpoints
│   ├── ingest/           # Knowledge ingestion scripts
│   ├── knowledge-base/   # Markdown knowledge files
│   └── sync/             # Sync utilities
│
├── GP-RAG/               # RAG (Retrieval Augmented Generation) engine
│   ├── core/             # RAG core logic
│   ├── mlops/            # Model operations
│   ├── processed/        # Processed knowledge
│   └── unprocessed/      # Raw knowledge to process
│
├── GP-TESTING-VAL/       # Testing & validation
│   ├── demos/            # Demo scripts
│   ├── tests/            # Test suites
│   └── test_terraform/   # Terraform testing
│
└── GP-TOOLS/             # Tool binaries
    └── binaries/         # External tool executables
```

**Key Files:**
- `GP-RAG/jade_rag_langgraph.py` - Main RAG graph orchestrator
- `GP-RAG/ingest_scan_results.py` - Ingests security scans into RAG
- `GP-KNOWLEDGE-HUB/ingest/consolidate-knowledge.py` - Knowledge consolidation

---

## 📁 Pillar 2: GP-CONSULTING

**Purpose:** 6-phase security engagement framework

```
GP-CONSULTING/
├── 1-Security-Assessment/     # 🔍 Phase 1: Scan & discover
│   ├── ci-scanners/           # Bandit, Semgrep, Gitleaks
│   ├── cd-scanners/           # Checkov, Trivy, Tfsec
│   ├── runtime-scanners/      # AWS Config, CloudTrail, GuardDuty
│   └── tools/                 # Orchestration scripts
│
├── 2-App-Sec-Fixes/           # 🔧 Phase 2: Code-level fixes
│   ├── ci-fixers/             # SQL injection, secrets, XSS fixes
│   ├── ci-templates/          # Fix templates
│   └── remediation/           # Fix recommendation database
│
├── 3-Hardening/               # 🛡️ Phase 3: Infrastructure hardening
│   ├── cd-fixers/             # K8s security, S3 encryption, IAM
│   ├── policies/              # OPA/Rego + Gatekeeper policies
│   ├── mutators/              # Admission control
│   └── secrets-management/    # Vault integration
│
├── 4-Cloud-Migration/         # ☁️ Phase 4: AWS migration
│   ├── terraform-modules/     # Secure infrastructure templates
│   ├── aws-fixers/            # AWS-specific fixes
│   └── migration-scripts/     # Migration automation
│
├── 5-Compliance-Audit/        # ✅ Phase 5: Validation & reporting
│   ├── validators/            # Before/after comparison
│   ├── frameworks/            # PCI-DSS, HIPAA, NIST mappings
│   ├── reports/               # Report generators
│   └── standards/             # GuidePoint standards
│
├── 6-Auto-Agents/             # 🤖 Phase 6: Continuous automation
│   ├── agents/                # 14 AI security agents
│   ├── workflows/             # Multi-agent orchestration
│   ├── cicd-templates/        # GitHub Actions, GitLab CI
│   └── monitoring/            # Alerting & incident response
│
└── shared-library/            # 📚 Shared code
    ├── base-classes/          # Scanner/Fixer base classes
    ├── utils/                 # Helper functions
    └── configs/               # Shared configurations
```

**Key Files:**
- `run-complete-engagement.sh` - Orchestrates all 6 phases
- `README.md` - Framework documentation
- `tagsandlabels.md` - Tool classification guide

**Tool Tags:**
- 🔍 `[SCAN]` - Discovers issues (read-only)
- 🔧 `[FIX]` - Remediates issues (writes/modifies)
- 📋 `[POLICY]` - Policy definitions
- 🛡️ `[ENFORCE]` - Policy enforcement
- 📊 `[REPORT]` - Generates reports
- 🤖 `[AGENT]` - AI-driven automation

---

## 📁 Pillar 3: GP-DATA

**Purpose:** Centralized data storage for all GP-Copilot operations

```
GP-DATA/
├── active/                    # Active engagement data
│   ├── 1-sec-assessment/     # Phase 1 scan results
│   │   ├── ci-findings/      # CI scanner outputs (JSON)
│   │   ├── cd-findings/      # CD scanner outputs (JSON)
│   │   └── runtime-findings/ # Runtime scanner outputs
│   │
│   ├── 2-fixes/              # Phase 2 fix reports
│   ├── 3-hardening/          # Phase 3 hardening logs
│   ├── 5-com-audit/          # Phase 5 compliance reports
│   ├── reports/              # Executive summaries
│   └── workflows/            # Workflow state
│
├── GP-DOCS/                  # Project documentation
│   ├── architecture/         # Architecture docs
│   ├── deployment/           # Deployment guides
│   ├── guides/               # User guides
│   └── reports/              # Historical reports
│
├── jade-knowledge/           # Jade AI knowledge base
│   ├── chroma/               # ChromaDB vector storage
│   └── chroma_backup/        # Vector DB backups
│
├── ai-models/                # Downloaded AI models
├── audit/                    # Audit logs
├── configs/                  # Configuration files
├── logs/                     # System logs
└── metadata/                 # Metadata & indices
```

**Data Flow:**
```
Scan → GP-DATA/active/1-sec-assessment/
Fix  → GP-DATA/active/2-fixes/
Harden → GP-DATA/active/3-hardening/
Audit → GP-DATA/active/5-com-audit/
```

---

## 📁 Pillar 4: GP-Frontend

**Purpose:** AI orchestration, platform services, user interfaces

```
GP-Frontend/
├── GP-AI/                    # AI orchestration layer
│   ├── agents/               # Jade orchestrator, troubleshooting
│   ├── api/                  # API endpoints (approval, secrets)
│   ├── cli/                  # CLI tools (jade-cli.py, jade_chat.py)
│   ├── config/               # AI config (prompts, routing)
│   ├── core/                 # RAG engine, security reasoning
│   ├── engines/              # LLM adapters
│   ├── integrations/         # Scan integration, tool registry
│   ├── models/               # Model management
│   └── workflows/            # Approval workflows
│
├── GP-PLATFORM/              # Platform services
│   ├── api/                  # Platform APIs (MCP, automation)
│   ├── coordination/         # Multi-agent coordination
│   ├── core/                 # James orchestrator, secrets manager
│   ├── james-config/         # Configuration (agent metadata, GP-DATA paths)
│   ├── mcp/                  # MCP (Model Context Protocol) server
│   ├── model_client/         # Model client integrations
│   ├── scripts/              # Utility scripts
│   └── workflow/             # Workflow management
│
└── GP-GUI/                   # Web GUI (future)
```

**Key Files:**
- `GP-AI/cli/jade-cli.py` - Main Jade CLI interface
- `GP-PLATFORM/core/james_orchestrator.py` - James AI orchestrator
- `GP-PLATFORM/james-config/gp_data_config.py` - GP-DATA path config

---

## 📁 Pillar 5: GP-PROJECTS

**Purpose:** Client project sandboxes for security testing

```
GP-PROJECTS/
├── FINANCE-project/          # SecureBank neobank (9,098 LOC)
│   ├── backend/              # Node.js backend (22 APIs)
│   ├── frontend/             # React frontend (5 components)
│   ├── infrastructure/       # K8s + Terraform + AWS
│   └── docs/                 # Project docs
│
├── DVWA/                     # Damn Vulnerable Web App
├── CLOUD-project/            # Cloud security demo
├── DEFENSE-project/          # Defense demos
└── kubernetes-goat/          # K8s security training
```

**Active Projects:**
- `FINANCE-project` - Branch: `phase4-aws-migration` (Phase 4 complete)
- `DVWA` - Classic vulnerable app for testing
- Others - Various security training projects

---

## 🔄 Data Flow Architecture

### Security Workflow Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  User executes: ./gp-security assess GP-PROJECTS/FINANCE   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  GP-CONSULTING/1-Security-Assessment/                       │
│  ├── CI scanners run (Bandit, Semgrep, Gitleaks)           │
│  ├── CD scanners run (Checkov, Trivy)                      │
│  └── Runtime scanners run (AWS Config)                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Results saved to GP-DATA/active/1-sec-assessment/          │
│  ├── ci-findings/*.json                                     │
│  ├── cd-findings/*.json                                     │
│  └── runtime-findings/*.json                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  GP-Backend/GP-RAG/ingest_scan_results.py                   │
│  ├── Reads findings from GP-DATA                            │
│  ├── Enriches with security context                         │
│  └── Stores in vector database                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  GP-Frontend/GP-AI/cli/jade-cli.py                          │
│  ├── User queries: "What vulnerabilities did you find?"     │
│  ├── RAG retrieves relevant findings                        │
│  └── AI generates remediation recommendations              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  User executes: ./gp-security fix GP-PROJECTS/FINANCE       │
│  GP-CONSULTING/2-App-Sec-Fixes/ applies fixes               │
│  Results → GP-DATA/active/2-fixes/                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Path Configuration

### Python Import Paths

**Scanners** (in GP-CONSULTING):
```python
# Add shared library to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared-library' / 'base-classes'))
```

**Jade AI** (in GP-Frontend/GP-AI):
```python
# Access GP-PLATFORM/james-config
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-PLATFORM" / "james-config"))
```

**RAG Ingestion** (in GP-Backend/GP-RAG):
```python
# Access GP-DATA
gp_root = Path(__file__).parent.parent.parent
data_dir = gp_root / "GP-DATA" / "active" / "1-sec-assessment"
```

### Key Path Patterns

| Component | Relative Path to Root |
|-----------|----------------------|
| Scanner | `../../../` (3 levels up) |
| Jade CLI | `../../` (2 levels up) |
| RAG Scripts | `../../` (2 levels up) |
| Platform Core | `../../../` (3 levels up from james-config) |

---

## 🚀 Master CLI: gp-security

**Location:** `/home/jimmie/linkops-industries/GP-copilot/gp-security`

### Commands

```bash
# Phase 1: Security Assessment
./gp-security assess GP-PROJECTS/FINANCE-project
./gp-security assess GP-PROJECTS/FINANCE-project --ci     # CI only
./gp-security assess GP-PROJECTS/FINANCE-project --cd     # CD only

# Phase 2: Application Fixes
./gp-security fix GP-PROJECTS/FINANCE-project

# Phase 3: Infrastructure Hardening
./gp-security harden GP-PROJECTS/FINANCE-project

# Phase 5: Compliance Validation
./gp-security validate GP-PROJECTS/FINANCE-project

# Complete Workflow (all 6 phases)
./gp-security workflow GP-PROJECTS/FINANCE-project

# Skip specific phases
./gp-security workflow GP-PROJECTS/FINANCE-project --skip-phases=1,2
```

---

## 🔗 Integration Points

### 1. Scanners → GP-DATA
- Scanners write JSON output to `GP-DATA/active/1-sec-assessment/`
- Standard format with metadata, findings, severity breakdown

### 2. GP-DATA → RAG
- `GP-Backend/GP-RAG/ingest_scan_results.py` reads from GP-DATA
- Stores enriched findings in ChromaDB vector store
- Located in `GP-DATA/jade-knowledge/chroma/`

### 3. RAG → Jade AI
- `GP-Frontend/GP-AI/cli/jade-cli.py` queries RAG
- AI retrieves relevant security context
- Generates intelligent recommendations

### 4. James Orchestrator → All Pillars
- `GP-Frontend/GP-PLATFORM/core/james_orchestrator.py`
- Coordinates multi-phase workflows
- Uses `james-config/gp_data_config.py` for paths

---

## 📊 Status Summary

### ✅ Working
- 5-pillar organization complete
- All broken symlinks removed
- Master `gp-security` CLI created
- Python imports updated (scanners use relative paths)
- GP-DATA centralization complete
- FINANCE-project Phase 4 complete (9,098 LOC, 644 findings)

### ⚠️ Needs Testing
- End-to-end workflow execution
- RAG ingestion pipeline
- Jade CLI with new paths
- Cross-pillar integration

### 📝 Documentation
- This architecture doc (ARCHITECTURE.md) ✅
- GP-CONSULTING/README.md (Phase overview) ✅
- GP-CONSULTING/tagsandlabels.md (Tool classification) ✅
- Individual README files per pillar ⏳

---

## 🎯 Design Principles

1. **Separation of Concerns**
   - Backend (processing) separate from Frontend (orchestration)
   - Data isolated in GP-DATA
   - Security tools in GP-CONSULTING
   - Projects isolated in GP-PROJECTS

2. **Centralized Data**
   - All scan results → GP-DATA/active/
   - All documentation → GP-DATA/GP-DOCS/
   - All knowledge → GP-DATA/jade-knowledge/

3. **Relative Paths**
   - No hardcoded absolute paths
   - Use Path navigation from `__file__`
   - Standard depths: 2-3 levels to root

4. **Phase-Based Workflow**
   - Linear progression: Assess → Fix → Harden → Migrate → Validate → Automate
   - Can skip phases as needed
   - Each phase stores output in GP-DATA/active/

5. **Tool Classification**
   - Scanners (read-only) in Phase 1
   - Fixers (write) in Phase 2-3
   - Policies (definitions) in Phase 3
   - Enforcers (deployment) in Phase 3
   - Agents (automation) in Phase 6

---

## 📚 Key Documentation Files

| File | Purpose |
|------|---------|
| `/ARCHITECTURE.md` | This file - overall architecture |
| `/README.md` | Project overview |
| `/START_HERE.md` | Quick start guide |
| `/VISION.md` | Project vision & roadmap |
| `/GP-CONSULTING/README.md` | Security framework overview |
| `/GP-CONSULTING/tagsandlabels.md` | Tool classification guide |
| `/GP-DATA/GP-DOCS/` | Project-specific documentation |
| `/bin/README.md` | Tool binaries documentation |

---

## 🔍 Quick Reference

### Find Something

```bash
# Find all scanners
find GP-CONSULTING/1-Security-Assessment -name "*_scanner.py"

# Find all fixers
find GP-CONSULTING -name "fix-*.sh"

# Find scan results
ls GP-DATA/active/1-sec-assessment/*/

# Find policies
find GP-CONSULTING/3-Hardening/policies -name "*.rego"

# Find project docs
ls GP-DATA/GP-DOCS/projects/
```

### Common Tasks

```bash
# Run security assessment
./gp-security assess GP-PROJECTS/FINANCE-project

# Check scan results
ls -lh GP-DATA/active/1-sec-assessment/ci-findings/

# View latest findings
jq '.findings[] | {file, severity, title}' GP-DATA/active/1-sec-assessment/ci-findings/*.json | less

# Query Jade AI
GP-Frontend/GP-AI/cli/jade-cli.py chat

# Check FINANCE project status
cd GP-PROJECTS/FINANCE-project && git status
```

---

**Architecture Version:** 2.0 (5-Pillar Organization)
**Last Updated:** 2025-10-16
**Status:** Reorganization Complete ✅
