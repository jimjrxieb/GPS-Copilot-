# GP-RAG Architecture - Deep Dive Analysis

**Date:** 2025-10-16
**Analyst:** Full codebase audit
**Status:** Jimmie's Vision Documented

---

## 🎯 What Jimmie Wants: RAG Vision

Based on the code analysis, here's **YOUR vision for RAG**:

### The Dream

**"Drop → Learn → Query"** - A **3-step security knowledge system**:

1. **DROP** a document in `unprocessed/`
2. **LEARN** by running `python simple_learn.py`
3. **QUERY** through Jade AI: "What did I just learn?"

**Hybrid Intelligence:**
- **Vector Search** (ChromaDB) for semantic "vibes" (unstructured docs, guides, policies)
- **Knowledge Graph** (NetworkX) for precise relationships (CVE → CWE → Finding → Fix)
- **LangGraph** (workflow) for multi-step reasoning ("Find similar CVEs, then show me fixes")

---

## 📁 GP-RAG Structure Explained

```
GP-Backend/GP-RAG/
├── simple_learn.py              ⭐ YOUR MAIN TOOL - Drop & Learn
├── jade_rag_langgraph.py        🧠 Hybrid RAG + Graph + LangGraph Engine
├── ingest_scan_results.py       📊 Ingest security scans into RAG
├── ingest_jade_knowledge.py     📚 Ingest training data
├── graph_ingest_knowledge.py    🕸️ Build knowledge graph
├── jade.py                      🏛️ Legacy orchestrator (superseded)
├── auto_sync.py                 🤖 Watch ~/jade-workspace for changes
├── dynamic_learner.py           👂 File watcher for unprocessed/
│
├── unprocessed/                 📥 DROP ZONE - Put docs here!
│   ├── jade-knowledge/          (Training data for Jade)
│   ├── session-docs/            (Docs from sessions)
│   ├── projects-docs/           (Project-specific)
│   └── intake/                  (Client intake structure)
│
├── processed/                   📦 AUTO-ARCHIVE - Files move here
│   ├── client-docs/
│   ├── james-os-knowledge/
│   └── security-docs/
│
├── mlops/                       🚀 YOUR FUTURE - Kube PAC Copilot
│   ├── mlops.md                 (Architectural blueprint)
│   └── mlops2.json              (Implementation spec)
│
├── core/
│   └── jade_engine.py           (Core RAG implementation)
│
└── tests/                       (Test scripts)
```

---

## 🧠 How RAG Works (3-Layer System)

### Layer 1: Vector Search (Semantic "Vibes")

**Technology:** ChromaDB with HuggingFace embeddings
**Location:** `GP-DATA/jade-knowledge/chroma/` (18MB)
**Purpose:** Find documents by **meaning**, not keywords

**Example:**
```python
Query: "How do I stop privileged containers?"
Vector Search finds:
  - "Kubernetes security contexts prevent privilege escalation"
  - "CIS Benchmark 5.2.5: Drop ALL capabilities"
  - "OPA policy: deny privileged containers"
```

**What it DOESN'T do:**
- ❌ Can't tell you "CVE-2024-1234 affects these 3 files"
- ❌ Can't traverse relationships
- ❌ Just fuzzy matching

---

### Layer 2: Knowledge Graph (Precise Relationships)

**Technology:** NetworkX MultiDiGraph
**Location:** `GP-DATA/jade-knowledge/security_graph.pkl` (972KB)
**Purpose:** **Structured knowledge traversal**

**Graph Structure:**
```
CVE-2024-33663 (cve node)
    ├─[instance_of]──> CWE-327 (Broken Crypto)
    ├─[maps_to]──> OWASP A02:2021 (Cryptographic Failures)
    ├─[detected_by]──> Trivy Scanner
    ├─[found_in]──> python-jose==3.3.0
    ├─[affects]──> LinkOps-MLOps/requirements.txt:42
    ├─[remediates]──> Upgrade to python-jose==3.4.0
    └─[relates_to]──> 12 similar findings

[Multi-hop query:]
"Show me all SQL injection findings"
  → Start: CWE-89 (SQL Injection)
  → Traverse: [instance_of] edges
  → Find: 47 findings across 3 projects
  → Traverse: [found_in] edges
  → Result: Exact file:line locations
```

**What it DOES:**
- ✅ Precise: "This CVE affects THESE files"
- ✅ Relational: "Show me all findings → CWEs → OWASP categories"
- ✅ Structured: Know exactly what connects to what

---

### Layer 3: LangGraph (Multi-Step Reasoning)

**Technology:** LangGraph + Qwen2.5-7B LLM
**File:** `jade_rag_langgraph.py`
**Purpose:** **Intelligent workflow orchestration**

**Workflow Steps:**
```
User Query: "Explain CVE-2024-33663 and show similar issues in my code"
    │
    ▼
[1] classify_domain()
    → Domain: cve_analysis
    │
    ▼
[2] retrieve_knowledge()
    → Graph: Find CVE-2024-33663 node
    → Graph: Traverse to related nodes (CWE, OWASP, findings)
    → Vector: Search for "CVE-2024-33663" in docs
    → Combine: 8 sources (3 from graph, 5 from vectors)
    │
    ▼
[3] reason_about_security()
    → Extract: severity=CRITICAL, remediation_available=true
    → Analyze: 12 similar findings across 3 projects
    │
    ▼
[4] draft_response() [uses Qwen2.5-7B LLM]
    → Generate: Technical analysis + business impact + fixes
    │
    ▼
[5] enhance_response()
    → Add sources
    → Calculate confidence (0.92)
    │
    ▼
[6] finalize()
    → Add reasoning chain for transparency
    │
    ▼
Result: Comprehensive answer with citations
```

---

## 🔄 Data Flow: How Knowledge Flows

### 1. Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  SOURCE: Security Scans                                      │
│  GP-DATA/active/1-sec-assessment/ci-findings/*.json         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  INGESTER: ingest_scan_results.py                           │
│  - Parses JSON (Bandit, Trivy, Semgrep formats)             │
│  - Extracts findings (CVE, CWE, severity, file:line)        │
│  - Creates nodes & edges                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
        ▼                  ▼
┌──────────────┐    ┌──────────────────┐
│  ChromaDB    │    │  Knowledge Graph │
│  (Vectors)   │    │  (NetworkX)      │
│  18MB        │    │  972KB           │
└──────────────┘    └──────────────────┘
        │                  │
        └────────┬─────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  STORAGE: GP-DATA/jade-knowledge/                            │
│  ├── chroma/           (vector database)                     │
│  └── security_graph.pkl (knowledge graph)                    │
└─────────────────────────────────────────────────────────────┘
```

### 2. Learning from Documents (Simple Drop & Learn)

```
You:
  cp ~/my-security-policy.md GP-Backend/GP-RAG/unprocessed/

You:
  python GP-Backend/GP-RAG/simple_learn.py

simple_learn.py:
  1. Reads file from unprocessed/
  2. Calls rag_engine.add_security_knowledge()
  3. Moves file to processed/
  4. Updates ChromaDB

Jade can now answer:
  "What is our password policy?"
  → Retrieves: Your document from ChromaDB
  → Generates: AI summary with policy details
```

### 3. Querying (Through Jade AI)

```
You:
  cd GP-Frontend/GP-AI/cli
  ./jade-cli.py chat

You (in chat):
  "Show me all SQL injection findings"

jade-cli.py:
  └─> jade_rag_langgraph.py
      └─> JadeRAGAgent.query()
          ├─> [1] classify_domain() → code_security
          ├─> [2] retrieve_knowledge()
          │   ├─> Graph: Find CWE-89 node
          │   ├─> Graph: Traverse [instance_of] edges
          │   ├─> Vector: Search "SQL injection"
          │   └─> Combine: 15 sources
          ├─> [3] reason_about_security()
          ├─> [4] draft_response() [Qwen LLM]
          └─> [5-6] enhance + finalize

Result:
  "I found 47 SQL injection vulnerabilities:
   - 23 in LinkOps-MLOps (Bandit)
   - 18 in FINANCE-project (Semgrep)
   - 6 in DVWA (intentional)

   Critical files:
   - LinkOps-MLOps/app/routes.py:127 (raw SQL)
   - FINANCE-project/backend/cards.controller.js:50 (template literals)

   Remediation: Use parameterized queries..."
```

---

## 📊 Current Stats (What's Already Loaded)

### Vector Database (ChromaDB)
```
Location: GP-DATA/jade-knowledge/chroma/
Size: 18MB
Documents: 328+
Collections:
  - security_patterns (best practices)
  - compliance_frameworks (PCI-DSS, SOC2)
  - cks_knowledge (Kubernetes security)
  - documentation (project docs)
  - client_knowledge
  - scan_findings (from scans)
  - project_context
  - troubleshooting
  - dynamic_learning (from unprocessed/)
```

### Knowledge Graph (NetworkX)
```
Location: GP-DATA/jade-knowledge/security_graph.pkl
Size: 972KB
Nodes: 1,696
  - 1,658 findings (real scan results!)
  - 15 CWEs
  - 10 OWASP categories
  - 6 tools (Trivy, Bandit, Semgrep, etc.)
  - 3 projects
Edges: 3,741
Relationships:
  - instance_of (Finding → CWE)
  - categorized_as (CWE → OWASP)
  - detected_by (Finding → Tool)
  - found_in (Finding → File)
  - fixed_by (Finding → Remediation)
  - relates_to (CVE → CVE)
```

---

## 🚀 MLOps Directory: Your Future Vision

**File:** `GP-Backend/GP-RAG/mlops/mlops.md`

This is **NOT MLOps for machine learning models**. It's a **Kubernetes Policy-as-Code (PAC) Copilot** specification!

### What's in mlops.md?

A complete architectural blueprint for:

**"Kube PAC Copilot" - Policy Generation for Kubernetes**

**Pipeline:**
```
K8s Manifest
    ↓
Feature Extraction (src/features/extract.py)
    ↓
Policy Retrieval (src/retrieve/index.py)
    ↓
Ranking (src/rank/model.py)
    ↓
Draft OPA/Rego Policy (src/policy_gen/drafter.py)
    ↓
Test Policy (src/policy_gen/test_runner.py)
    ↓
Deploy or Fix (src/troubleshoot/)
```

**Components:**
1. **Feature Extraction** - Parse K8s YAML for security features (privileged, hostPath, etc.)
2. **Policy Retrieval** - RAG-based retrieval of relevant OPA policies
3. **Policy Generation** - Draft OPA/Rego policies from templates
4. **Testing** - Run OPA unit tests in sandbox
5. **Troubleshooting** - Linter + counterexample generation
6. **CI Integration** - SARIF output for GitHub
7. **API** - FastAPI server for policy analysis

**Why it's in GP-RAG/mlops/:**
- Uses RAG for **policy retrieval** (hybrid search)
- Uses knowledge graph for **policy relationships**
- MLOps-style **training/eval/deployment** workflow
- **NOT** about training ML models - about **policy lifecycle management**

---

## 🎯 How RAG Connects to Everything

### Integration Map

```
GP-Backend/GP-RAG (THIS)
    │
    ├─> GP-DATA/jade-knowledge/
    │   ├─> chroma/              (vector storage)
    │   └─> security_graph.pkl   (graph storage)
    │
    ├─> GP-Frontend/GP-AI/
    │   ├─> cli/jade-cli.py      (user interface)
    │   └─> core/
    │       ├─> rag_engine.py    (RAG engine)
    │       └─> rag_graph_engine.py (graph engine)
    │
    ├─> GP-CONSULTING/
    │   └─> Reads: Policies, scan results, fixers
    │       (RAG learns from these)
    │
    └─> GP-PROJECTS/
        └─> Scans ingest from project findings
```

### Who Uses RAG?

| Component | How They Use RAG |
|-----------|------------------|
| **Jade CLI** (`GP-Frontend/GP-AI/cli/jade-cli.py`) | Main user interface - queries RAG for answers |
| **Scan Integrator** (`ingest_scan_results.py`) | Feeds security findings into RAG |
| **simple_learn.py** | User drops docs → RAG learns |
| **auto_sync.py** | Watches ~/jade-workspace → auto-ingests changes |
| **GP-CONSULTING tools** | Reference RAG for remediation advice |

---

## 🔍 Your Design Principles (Inferred)

### 1. **Simplicity First**
```python
# simple_learn.py - YOUR philosophy
# "Drop a file, run one command, done"
cp ~/doc.md unprocessed/
python simple_learn.py
# That's it!
```

### 2. **Hybrid Intelligence**
- **Not just vectors** (too fuzzy)
- **Not just graphs** (too rigid)
- **Both together** (best of both worlds)

### 3. **Real Data**
- Already loaded **1,658 real findings** from scans
- Not toy examples
- Production-ready from day 1

### 4. **Transparent Reasoning**
```python
# LangGraph workflow shows its work
result["reasoning_chain"] = [
    "Classified query as: cve_analysis",
    "Graph: Found 3 starting nodes",
    "Graph: Traversed 12 nodes via 4 paths",
    "Vector: Retrieved 5 documents",
    "Combined: 17 total sources",
    "Generated LLM response",
    "Response confidence: 0.92"
]
```

### 5. **Multiple Entry Points**
- **Simple**: Drop file → `simple_learn.py`
- **Automated**: Watch workspace → `auto_sync.py`
- **Bulk**: Scan results → `ingest_scan_results.py`
- **Interactive**: Chat → `jade-cli.py`

---

## 🤔 Why MLOps in GP-RAG?

**Answer:** Because **Policy-as-Code IS an MLOps workflow**:

| ML Concept | Policy Equivalent |
|------------|-------------------|
| **Training Data** | Policy corpus (OPA templates) |
| **Feature Engineering** | Extract K8s manifest features |
| **Model** | Policy retrieval + generation |
| **Inference** | Draft policy for new manifest |
| **Evaluation** | OPA unit tests |
| **Deployment** | Apply to cluster (Gatekeeper) |
| **Monitoring** | Violation metrics (Grafana) |
| **Feedback Loop** | Failures → improve policies |

**It's MLOps without the neural networks** - just deterministic policy engineering with RAG-enhanced retrieval.

---

## 📋 Key Files Breakdown

### Core RAG Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `simple_learn.py` | ⭐ **YOUR MAIN TOOL** | Drop docs in unprocessed/, run this |
| `jade_rag_langgraph.py` | Advanced query engine | Called by Jade CLI |
| `ingest_scan_results.py` | Bulk ingest scans | After running security scans |
| `ingest_jade_knowledge.py` | Ingest training data | Bootstrap knowledge |
| `graph_ingest_knowledge.py` | Build knowledge graph | Build graph structure |
| `auto_sync.py` | Auto-watch workspace | Background daemon |

### Storage Locations

| Location | What's Stored | Size |
|----------|---------------|------|
| `GP-DATA/jade-knowledge/chroma/` | Vector embeddings | 18MB |
| `GP-DATA/jade-knowledge/security_graph.pkl` | Knowledge graph | 972KB |
| `GP-Backend/GP-RAG/unprocessed/` | Files to learn | Variable |
| `GP-Backend/GP-RAG/processed/` | Learned files archive | 29MB |

---

## 🚀 Your Intended Workflow

### Daily Use:
```bash
# 1. Work on a project, create docs
vim ~/my-security-analysis.md

# 2. Drop it in RAG
cp ~/my-security-analysis.md \
   GP-Backend/GP-RAG/unprocessed/

# 3. Learn from it
python GP-Backend/GP-RAG/simple_learn.py

# 4. Query it
cd GP-Frontend/GP-AI/cli
./jade-cli.py chat

> "What did I just document about security?"
Jade: "Based on your security analysis document..."
```

### Automated (Set and Forget):
```bash
# Start auto-sync (once)
python GP-Backend/GP-RAG/auto_sync.py &

# Now work normally, Jade auto-learns
cd ~/jade-workspace/
vim terraform/main.tf
vim kubernetes/deployment.yaml

# Jade automatically ingests changes
# Query anytime:
./jade-cli.py chat
> "What Terraform changes did I make?"
```

### After Security Scans:
```bash
# Run scans
./gp-security assess GP-PROJECTS/FINANCE-project

# Ingest results into RAG
python GP-Backend/GP-RAG/ingest_scan_results.py

# Query findings
./jade-cli.py chat
> "Show me all CRITICAL findings"
> "What SQL injections did you find?"
> "Explain CVE-2024-33663"
```

---

## ✅ Summary: What You Have

**GP-RAG is your 3-layer security intelligence system:**

1. **Vector Search** (ChromaDB) - Fuzzy semantic search
2. **Knowledge Graph** (NetworkX) - Precise relationship traversal
3. **LangGraph** (Workflows) - Multi-step reasoning with LLM

**Current Status:**
- ✅ 328+ documents in vector DB
- ✅ 1,658 findings in knowledge graph
- ✅ Working ingestion pipeline
- ✅ Simple drop & learn workflow
- ✅ Qwen2.5-7B LLM integration
- ✅ Multi-hop graph traversal
- 🚀 MLOps (Kube PAC Copilot) - Future vision documented

**Your Philosophy:**
- **Simple** - Drop file → run script → done
- **Hybrid** - Vectors + Graph = Best of both
- **Real** - 1,658 real findings, not toys
- **Transparent** - Shows reasoning chain
- **Flexible** - Multiple entry points

---

**Location in Pillars:** ✅ **GP-Backend is CORRECT**
- RAG = Backend processing (ingestion, graph building, vector embeddings)
- Frontend (GP-AI) = User interface (Jade CLI, API)
- Data (GP-DATA) = Storage (chroma/, security_graph.pkl)

**GP-KNOWLEDGE-HUB:** ❌ **DELETE IT** - It's deprecated, RAG lives in GP-DATA now.

---

**Last Updated:** 2025-10-16
**Audit:** Complete
**Status:** Your vision is clear! 🎯
