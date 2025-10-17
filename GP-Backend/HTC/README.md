# HTC (Human-Teachable Computer) - Jade's Learning System

**Jade's RAG + Knowledge Graph intelligence system.**

---

## What's Here 📁

```
HTC/
├── ingest.py                   ⭐ UNIFIED INGESTION (use this!)
├── auto_sync.py                ⭐ AUTO-WATCH WORKSPACE
├── jade_rag_langgraph.py       ⭐ CORE ENGINE (RAG + Graph + LangGraph)
├── jade_api.py                 ⭐ API INTERFACE
│
├── test_*.py                   Tests
│
├── unprocessed/                DROP ZONE (put files here)
│   ├── *.md, *.txt             Markdown/text docs
│   └── jade-knowledge/         JSONL knowledge
│       └── *.jsonl             Training conversations
│
├── processed/                  Archive (files auto-move here)
│
├── deprecated/                 Legacy scripts (backward compatible)
│   ├── README.md               Migration guide
│   ├── simple_learn.py         OLD: Markdown ingestion
│   ├── ingest_jade_knowledge.py  OLD: JSONL ingestion
│   ├── graph_ingest_knowledge.py  OLD: Graph builder
│   ├── jade.py                 OLD: Legacy orchestrator
│   └── dynamic_learner.py      OLD: File watcher
│
└── utils/                      Rarely used utilities
    ├── README.md               Utility guide
    ├── migrate_vector_db_knowledge.py  One-time migration
    └── reembed_processed_files.py      Re-embedding utility
```

---

## Quick Start 🚀

### 1. Ingest Knowledge (One Command)

```bash
# Drop your files in unprocessed/
cp ~/my-docs/*.md HTC/unprocessed/
cp ~/training/*.jsonl HTC/unprocessed/jade-knowledge/

# Ingest everything (auto-detects format)
python HTC/ingest.py
```

**Supported formats**: `.md`, `.txt`, `.jsonl` (conversations or document chunks)

**That's it!** Your documents are now in the RAG system.

---

### 2. Auto-Watch Workspace (Optional)

```bash
# Start background daemon
python HTC/auto_sync.py &
```

Watches `~/jade-workspace/` and auto-ingests Terraform, K8s, Python, OPA files.

---

### 3. Query Knowledge

```python
from HTC.jade_rag_langgraph import JadeRAGAgent

agent = JadeRAGAgent()
result = agent.query("What is our security policy?")
print(result['response'])
```

---

## How It Works 🧠

### Three-Layer Intelligence System:

#### 1. Vector Search (ChromaDB)
- **What**: Semantic similarity search for documents
- **Where**: `GP-DATA/knowledge-base/chroma/`
- **Use**: "Find documents about X"

#### 2. Knowledge Graph (NetworkX)
- **What**: Structured relationships (CVE → CWE → OWASP → Findings)
- **Where**: `GP-DATA/knowledge-base/security_graph.pkl`
- **Use**: "Show me what's connected to X"

#### 3. LangGraph (Workflow Orchestration)
- **What**: Combines RAG + Graph with multi-step reasoning
- **File**: `jade_rag_langgraph.py`
- **LLM**: Qwen2.5-7B-Instruct

**Together**, they enable:
- "Show me our password policy" → **Vector search**
- "What SQL injection findings exist?" → **Graph traversal**
- "Explain this CVE and show similar findings" → **Hybrid: Graph + Vector**

---

## Core Files (Use These) 📋

| File | Purpose | When to Use |
|------|---------|-------------|
| **ingest.py** | **Unified ingestion** for all formats | Drop files in `unprocessed/` and run this |
| **auto_sync.py** | **Auto-watch** workspace for changes | Background daemon for automatic learning |
| **jade_rag_langgraph.py** | **Core engine** (RAG + Graph + LangGraph) | Query knowledge, reasoning workflows |
| **jade_api.py** | **API interface** | REST API for Jade |

**That's it. 4 files to know.**

---

## Integration with GP-Copilot 🔗

HTC works seamlessly with the rest of GP-Copilot:

```
┌─────────────────────────────────────────────────────────┐
│  HTC (This Directory)                                    │
│  • Vector search for documents                           │
│  • Learning from unprocessed/                            │
│  • Knowledge graph relationships                         │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GP-Frontend/GP-AI/core/rag_engine.py                    │
│  • RAG engine implementation                             │
│  • ChromaDB collections                                  │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GP-DATA/knowledge-base/                                 │
│  • chroma/ (vector database)                             │
│  • security_graph.pkl (knowledge graph)                  │
└─────────────────────────────────────────────────────────┘
```

---

## Usage Examples 💡

### Example 1: Ingest Markdown Documentation

```bash
# 1. Drop your docs
cp ~/security-policy-2025.md HTC/unprocessed/

# 2. Ingest
python HTC/ingest.py

# Output:
# 📚 Found 1 files to process:
#    - Markdown: 1
#    - Text: 0
#    - JSONL: 0
# ✅ Ingested: security-policy-2025.md (8432 chars)
# ✅ Knowledge successfully ingested into Jade RAG system
```

### Example 2: Ingest JSONL Training Data

```bash
# 1. Drop JSONL conversations
cp ~/cks-training.jsonl HTC/unprocessed/jade-knowledge/

# 2. Ingest
python HTC/ingest.py

# Detects JSONL format automatically:
# 📂 Processing JSONL: cks-training.jsonl
#   💾 Ingesting 152 documents to 'cks' collection...
# ✅ Processed 152 lines from cks-training.jsonl
```

### Example 3: Ingest Everything + Build Graph

```bash
# One command to rule them all
python HTC/ingest.py --all

# Ingests all files AND builds knowledge graph
```

### Example 4: Preview Without Ingesting (Dry Run)

```bash
# See what would be ingested
python HTC/ingest.py --dry-run

# Output shows files but doesn't actually ingest
```

---

## Testing 🧪

```bash
# Test ingestion (dry run)
echo "# Test Security Policy" > unprocessed/test.md
python ingest.py --dry-run

# Test actual ingestion
python ingest.py

# Test RAG + LangGraph
python test_jade_comprehensive.py

# Test auto-sync
python test_auto_sync.py
```

---

## Current Stats 📊

### Vector Database (ChromaDB)
- **Documents**: 328+
- **Collections**: 9
  - `security_patterns` (security best practices)
  - `compliance_frameworks` (SOC2, CIS, PCI-DSS)
  - `cks_knowledge` (Kubernetes security)
  - `documentation` (project docs)
  - `client_knowledge` (client-specific)
  - `scan_findings` (latest scans)
  - `project_context` (metadata)
  - `troubleshooting` (guides)
  - `dynamic_learning` (from unprocessed/)

### Knowledge Graph (NetworkX)
- **Nodes**: 1,696+
  - 1,658+ findings (from real scans!)
  - 15+ CWEs
  - 10+ OWASP categories
  - 6+ tools (Trivy, Bandit, etc.)
  - 3+ projects
- **Edges**: 3,741+
- **Relationships**: instance_of, categorized_as, detected_by, found_in, fixed_by

---

## Troubleshooting 🔧

### "No module named 'watchdog'"

You don't need `watchdog` anymore! Use `auto_sync.py` instead of `dynamic_learner.py`.

### "ChromaDB error"

```bash
# Re-initialize RAG engine
python GP-Frontend/GP-AI/core/rag_engine.py
```

### "Knowledge graph not found"

```bash
# Rebuild graph from RAG
python ingest.py --build-graph
```

### "Import errors"

```bash
# Make sure you're in the right directory
cd /home/jimmie/linkops-industries/GP-copilot
source ai-env/bin/activate
python GP-Backend/HTC/ingest.py
```

---

## Migration from Old Scripts

### Old → New Command Reference

| Old Command | New Command | Notes |
|-------------|-------------|-------|
| `python simple_learn.py` | `python ingest.py` | Auto-detects format |
| `python ingest_jade_knowledge.py` | `python ingest.py` | Handles JSONL |
| `python graph_ingest_knowledge.py` | `python ingest.py --build-graph` | Builds graph |
| `python simple_learn.py && python graph_ingest_knowledge.py` | `python ingest.py --all` | One command! |

**Old scripts still work** (moved to `deprecated/`), but use `ingest.py` going forward.

---

## Summary ✨

**HTC contains Jade's learning and reasoning system.**

### What You Do:
1. Drop docs in `unprocessed/`
2. Run `python ingest.py`
3. Query with `jade` or Python

### What Jade Does:
- **Learns** from your documents (vector embeddings)
- **Reasons** with knowledge graph (relationships)
- **Combines** both for intelligent answers

### Key Points:
- ✅ **Simple**: One command for all formats
- ✅ **Smart**: Relationship-aware intelligence
- ✅ **Real data**: 1,658+ findings already loaded
- ✅ **Clean**: 4 scripts instead of 11

---

## What Changed? (Consolidation Summary)

### Before (11 scripts 😰):
Multiple confusing scripts - "Which one do I use?"

### After (4 scripts 😊):
- **ingest.py** - Unified ingestion (replaces 3 scripts)
- **auto_sync.py** - Workspace watcher
- **jade_rag_langgraph.py** - Core engine
- **jade_api.py** - API

**Benefits**:
- **63% fewer scripts** (11 → 4)
- **One ingestion path** (was 5)
- **Auto-detects format** (no need to pick script)
- **Backward compatible** (old scripts still work)

**For more details:**
- Consolidation analysis: [HTC_CLEANUP_ANALYSIS.md](HTC_CLEANUP_ANALYSIS.md)
- Deprecated scripts: [deprecated/README.md](deprecated/README.md)
- Utility scripts: [utils/README.md](utils/README.md)

---

Last updated: 2025-10-16
