# RAG Learning Integration Guide

**How to Drop New Data into GP-Copilot**

You now have **3 learning systems** working together:
1. **Dynamic Learner** (unstructured docs → Vector DB)
2. **Auto Sync** (workspace monitoring → Vector DB)
3. **Scan Graph Integrator** (NEW! scan results → Knowledge Graph)

---

## System 1: Dynamic Learner (For Documents) 📚

**Purpose**: Learn from unstructured documents (PDFs, markdown, text)

**Drop files here:**
```bash
/home/jimmie/linkops-industries/GP-copilot/GP-RAG/unprocessed/
```

**Supported formats:**
- Markdown (`.md`)
- PDF (`.pdf`)
- Text (`.txt`)
- JSON (general `.json`)

**How to use:**

### Option A: Manual Sync (Recommended)
```bash
cd /home/jimmie/linkops-industries/GP-copilot
source ai-env/bin/activate
python GP-RAG/dynamic_learner.py sync
```

This will:
1. Scan `GP-RAG/unprocessed/` for new files
2. Process and chunk content
3. Add to ChromaDB vector store
4. Move processed files to `GP-RAG/processed/`

### Option B: Watch Mode (Auto-sync)
```bash
python GP-RAG/dynamic_learner.py watch
```

This runs in background and automatically processes files as you drop them.

**Example:**
```bash
# Drop a security policy document
cp ~/Downloads/security-policy.pdf GP-RAG/unprocessed/

# Process it
python GP-RAG/dynamic_learner.py sync

# Query it
python GP-RAG/simple_rag_query.py "What is our security policy?"
```

---

## System 2: Auto Sync (For Workspace Changes) 🔄

**Purpose**: Auto-monitor your workspace for code/config changes

**Watches:**
```bash
~/jade-workspace/projects/**
```

**Monitored file types:**
- Terraform (`.tf`, `.tfvars`)
- Kubernetes (`.yaml`, `.yml`)
- OPA policies (`.rego`)
- Python (`.py`)
- Configs (`.json`)
- Docs (`.md`)
- Scripts (`.sh`)

**How to use:**
```bash
# Start auto-sync daemon
python GP-DATA/auto_sync_daemon.py
```

This runs in background and automatically ingests changes as you work.

**Example:**
```bash
# Edit a Terraform file
vim ~/jade-workspace/projects/aws/main.tf

# Auto-sync sees the change and ingests it
# No manual action needed!

# Query recent changes
python GP-RAG/simple_rag_query.py "What Terraform changes did I make today?"
```

---

## System 3: Scan Graph Integrator (For Security Scans) 🔒 **NEW!**

**Purpose**: Populate knowledge graph with security scan findings

**Drop scan files here:**
```bash
/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans/
```

**Supported scanners:**
- Bandit (Python SAST)
- Trivy (Container/dependency scanning)
- Semgrep (SAST)
- Checkov (IaC scanning)
- Gitleaks (Secret detection)

**How to use:**

### Option A: Single Scan File
```bash
python GP-AI/core/scan_graph_integrator.py GP-DATA/active/scans/bandit_latest.json
```

### Option B: Entire Directory
```bash
python GP-AI/core/scan_graph_integrator.py GP-DATA/active/scans/
```

### Option C: Default (No args)
```bash
python GP-AI/core/scan_graph_integrator.py
# Defaults to GP-DATA/active/scans/
```

**Example:**
```bash
# Run Bandit scan
bandit -r GP-PROJECTS/my-app -f json -o GP-DATA/active/scans/bandit_my-app.json

# Integrate into graph
python GP-AI/core/scan_graph_integrator.py GP-DATA/active/scans/bandit_my-app.json

# Query graph
python -c "
from GP_AI.core.rag_graph_engine import security_graph
findings = security_graph.find_nodes_by_query('my-app')
print(f'Found {len(findings)} nodes related to my-app')
"
```

---

## How They Work Together 🔗

```
┌─────────────────────────────────────────────────────────────┐
│                    Drop New Data                              │
└────────────┬─────────────────┬──────────────────┬────────────┘
             │                 │                  │
             ↓                 ↓                  ↓
    ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐
    │  GP-RAG/       │  │ ~/jade-      │  │ GP-DATA/active/ │
    │  unprocessed/  │  │ workspace/   │  │ scans/          │
    └────────┬───────┘  └──────┬───────┘  └────────┬────────┘
             │                 │                    │
             ↓                 ↓                    ↓
    ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐
    │ Dynamic        │  │ Auto Sync    │  │ Scan Graph      │
    │ Learner        │  │              │  │ Integrator      │
    └────────┬───────┘  └──────┬───────┘  └────────┬────────┘
             │                 │                    │
             ↓                 ↓                    ↓
    ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐
    │ ChromaDB       │  │ ChromaDB     │  │ NetworkX        │
    │ (Vectors)      │  │ (Vectors)    │  │ Graph           │
    └────────┬───────┘  └──────┬───────┘  └────────┬────────┘
             │                 │                    │
             └─────────────────┼────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  RAG + RAG Graph     │
                    │  Query System        │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Intelligent Answers │
                    │  with Context        │
                    └──────────────────────┘
```

---

## Decision Tree: Which System to Use? 🌳

### If you have a **security scan result**:
→ Use **Scan Graph Integrator**
→ Drops into knowledge graph
→ Enables relationship queries

### If you have a **document/policy/guide**:
→ Use **Dynamic Learner**
→ Drops into vector database
→ Enables semantic search

### If you're **actively coding**:
→ Use **Auto Sync** (runs in background)
→ Auto-captures changes
→ Enables "What did I change?" queries

---

## Example Workflows 📋

### Workflow 1: New Security Policy
```bash
# 1. Drop policy document
cp security-policy-2025.pdf GP-RAG/unprocessed/

# 2. Process it
python GP-RAG/dynamic_learner.py sync

# 3. Query it
python GP-RAG/simple_rag_query.py "What is our password policy?"
```

### Workflow 2: New Security Scan
```bash
# 1. Run scan
trivy fs GP-PROJECTS/webapp -f json -o GP-DATA/active/scans/trivy_webapp.json

# 2. Integrate into graph
python GP-AI/core/scan_graph_integrator.py GP-DATA/active/scans/trivy_webapp.json

# 3. Query graph with LangGraph
python -c "
from GP_RAG.jade_rag_langgraph import JadeRAGAgent
agent = JadeRAGAgent()
result = agent.query('What vulnerabilities exist in webapp?')
print(result['response'])
"
```

### Workflow 3: Daily Development
```bash
# 1. Start auto-sync (once, runs in background)
python GP-DATA/auto_sync_daemon.py &

# 2. Work normally - edit Terraform, write code, etc.
vim ~/jade-workspace/projects/aws/main.tf

# 3. Auto-sync captures changes automatically

# 4. Query what you did
python GP-RAG/simple_rag_query.py "What Terraform changes did I make today?"
```

---

## Quick Start: Add New Data Now ⚡

### Step 1: Drop a test document
```bash
echo "# Test Security Policy
This is a test policy document.
- Passwords must be 12+ characters
- MFA required for all users
- Session timeout: 30 minutes" > GP-RAG/unprocessed/test-policy.md
```

### Step 2: Process it
```bash
python GP-RAG/dynamic_learner.py sync
```

### Step 3: Query it
```bash
python GP-RAG/simple_rag_query.py "What is the password requirement?"
```

**Expected output:**
```
Passwords must be 12+ characters
Source: test-policy.md
```

---

## Current State 📊

### Vector Database (ChromaDB)
**Location**: `GP-DATA/knowledge-base/chroma/`
**Collections**:
- `security_patterns` (security best practices)
- `client_knowledge` (client-specific docs)
- `compliance_frameworks` (SOC2, CIS, PCI-DSS)
- `cks_knowledge` (Kubernetes security)
- `scan_findings` (latest scan results)
- `documentation` (project docs)
- `project_context` (project metadata)
- `dynamic_learning` (from unprocessed files)

### Knowledge Graph (NetworkX)
**Location**: `GP-DATA/knowledge-base/security_graph.pkl`
**Stats**:
- Nodes: 1,696
- Edges: 3,741
- Findings: 1,658 (from real scans!)
- Projects: 3 (LinkOps-MLOps, DVWA, Portfolio)
- CWEs: 15
- OWASP: 10

---

## Integration with Jade CLI 🤖

You can query both systems through Jade:

### Query Vector DB (Documents)
```bash
jade query "What is our security policy?"
```

### Query Knowledge Graph (Scan Findings) **NEW!**
```bash
# Coming soon:
jade graph-query "Show me all SQL injection findings"
jade graph-query "What's the security posture of LinkOps-MLOps?"
```

---

## Best Practices 🎯

### For Documents:
- ✅ Drop PDFs, markdown, text into `GP-RAG/unprocessed/`
- ✅ Run `python GP-RAG/dynamic_learner.py sync` periodically
- ✅ Or run `watch` mode for auto-processing

### For Scans:
- ✅ Save scan results as JSON in `GP-DATA/active/scans/`
- ✅ Run `python GP-AI/core/scan_graph_integrator.py` after new scans
- ✅ Use consistent naming: `<scanner>_<project>_<timestamp>.json`

### For Code Changes:
- ✅ Keep projects in `~/jade-workspace/`
- ✅ Run auto-sync daemon in background
- ✅ Changes are auto-captured

---

## Troubleshooting 🔧

### "No module named 'watchdog'"
```bash
pip install watchdog
```

### "ChromaDB collection not found"
```bash
# Re-initialize RAG engine
python GP-AI/core/rag_engine.py
```

### "Graph file not found"
```bash
# Rebuild graph
python GP-AI/core/rag_graph_engine.py
```

### "Scan integration failed"
Check scanner format:
```bash
# Verify JSON structure
jq '.' GP-DATA/active/scans/your-scan.json
```

---

## Summary ✨

**YES! You can still drop files in `GP-RAG/unprocessed/` and run the learn script.**

**But now you ALSO have:**
- Scan graph integration for security findings
- Auto-sync for workspace monitoring
- Knowledge graph for relationship queries

**All three systems work together** to give Jade comprehensive intelligence:
- **Documents** (policies, guides) → Vector DB → Semantic search
- **Code changes** (Terraform, K8s) → Vector DB → Time-series queries
- **Security scans** (Trivy, Bandit) → Knowledge Graph → Relationship queries

**Drop data anywhere, Jade learns it all!** 🚀