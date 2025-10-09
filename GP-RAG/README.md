# GP-RAG - RAG + Knowledge Graph for Security Intelligence

**Jade's learning and reasoning system.**

---

## What's Here 📁

```
GP-RAG/
├── simple_learn.py              # ⭐ Drop files in unprocessed/ and run this
├── jade_rag_langgraph.py        # RAG + RAG Graph + LangGraph integration
├── auto_sync.py                 # Auto-sync workspace changes (daemon)
├── dynamic_learner.py           # Advanced learning (needs watchdog)
├── jade.py                      # Legacy orchestrator
├── jade_api.py                  # API interface
├── test_*.py                    # Test scripts
├── core/
│   ├── jade_engine.py           # Core RAG engine
│   └── dynamic_learner.py       # Learner implementation
├── unprocessed/                 # ⭐ DROP NEW DOCS HERE
│   ├── client-docs/
│   ├── james-os-knowledge/
│   └── security-docs/
├── processed/                   # Processed docs (auto-moved)
└── intake/                      # Client intake structure
    ├── clients/
    ├── meetings/
    └── people/
```

---

## Quick Start 🚀

### 1. Add New Documents (Easiest Way)

```bash
# Drop your file in unprocessed/
cp ~/my-document.md GP-RAG/unprocessed/

# Learn from it
python GP-RAG/simple_learn.py
```

**Supported formats**: `.md`, `.txt`

**That's it!** Your document is now in the RAG system.

---

### 2. Query Your Documents

```python
from GP_RAG.jade_rag_langgraph import JadeRAGAgent

agent = JadeRAGAgent()
result = agent.query("What is our security policy?")
print(result['response'])
```

---

### 3. Enable Auto-Sync (Optional)

```bash
# Auto-monitor workspace for changes
python GP-RAG/auto_sync.py &
```

This watches `~/jade-workspace/` and auto-ingests Terraform, K8s, Python, OPA files.

---

## How It Works 🧠

**3-Layer Intelligence System:**

### 1. Vector Search (ChromaDB)
- **What**: Semantic similarity search for documents
- **Where**: `GP-DATA/knowledge-base/chroma/`
- **Use**: Unstructured docs (policies, guides, markdown)

### 2. Knowledge Graph (NetworkX)
- **What**: Structured relationships (CVE → CWE → OWASP → Findings)
- **Where**: `GP-DATA/knowledge-base/security_graph.pkl`
- **Use**: Security scan findings (1,658 findings loaded!)
- **See**: [RAG_GRAPH_IMPLEMENTATION_COMPLETE.md](../RAG_GRAPH_IMPLEMENTATION_COMPLETE.md)

### 3. LangGraph (Workflow Orchestration)
- **What**: Combines graph + vector search with multi-step reasoning
- **File**: `jade_rag_langgraph.py`
- **LLM**: Qwen2.5-7B-Instruct

**Together**, they enable:
- "Show me our password policy" (vector search)
- "What SQL injection findings exist?" (graph traversal)
- "Explain this CVE and show similar findings in my projects" (hybrid: graph + vector)

---

## Files & Directories Explained 📋

### Core Files (Use These):

| File | Purpose | When to Use |
|------|---------|-------------|
| `simple_learn.py` | Process docs from `unprocessed/` | Drop & learn workflow |
| `jade_rag_langgraph.py` | RAG + Graph query engine | Advanced queries with reasoning |
| `auto_sync.py` | Watch workspace, auto-ingest | Background daemon mode |
| `dynamic_learner.py` | File watcher for `unprocessed/` | Requires `watchdog` package |

### Test Files:

| File | Tests |
|------|-------|
| `test_jade_comprehensive.py` | Full RAG + LangGraph workflow |
| `test_auto_sync.py` | Auto-sync functionality |
| `test_jade_ai.py` | Basic Jade AI tests |

### Directories:

| Directory | Purpose | Action |
|-----------|---------|--------|
| `unprocessed/` | **Drop zone for new docs** | Drop files here, run `simple_learn.py` |
| `processed/` | Processed docs archive | Files auto-move here after learning |
| `intake/` | Client intake structure | Organize client docs by client/meeting/person |
| `core/` | Core RAG implementation | Don't modify unless needed |

---

## Integration with GP-Copilot 🔗

RAG works seamlessly with the knowledge graph:

```
┌─────────────────────────────────────────────────────────┐
│  GP-RAG (This Directory)                                 │
│  • Vector search for documents                           │
│  • Learning from unprocessed/                            │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GP-AI/core/rag_graph_engine.py                          │
│  • Knowledge graph structure                             │
│  • 1,696 nodes, 3,741 edges                              │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GP-AI/core/scan_graph_integrator.py                     │
│  • Populates graph from security scans                   │
│  • 1,658 findings from Trivy, Bandit, Semgrep, etc.     │
└─────────────────┬───────────────────────────────────────┘
                  ↓
          Combined Intelligence
```

**See also:**
- [RAG_GRAPH_IMPLEMENTATION_COMPLETE.md](../RAG_GRAPH_IMPLEMENTATION_COMPLETE.md)
- [SCAN_GRAPH_INTEGRATION_COMPLETE.md](../SCAN_GRAPH_INTEGRATION_COMPLETE.md)
- [RAG_LEARNING_INTEGRATION_GUIDE.md](../RAG_LEARNING_INTEGRATION_GUIDE.md)

---

## Testing 🧪

```bash
# Test simple learning
echo "# Test Security Policy" > unprocessed/test.md
python simple_learn.py

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
- **Nodes**: 1,696
  - 1,658 findings (from real scans!)
  - 15 CWEs
  - 10 OWASP categories
  - 6 tools (Trivy, Bandit, etc.)
  - 3 projects (LinkOps-MLOps, DVWA, Portfolio)
- **Edges**: 3,741
- **Relationships**: instance_of, categorized_as, detected_by, found_in, fixed_by

---

## Example Workflows 💡

### Workflow 1: Learn from New Policy
```bash
# 1. Drop the file
cp ~/security-policy-2025.pdf unprocessed/
# (Note: PDF support coming soon, use .md for now)

# 2. Process it
python simple_learn.py

# 3. Query it
python -c "
from GP_RAG.jade_rag_langgraph import JadeRAGAgent
agent = JadeRAGAgent()
result = agent.query('What is our password policy?')
print(result['response'])
"
```

### Workflow 2: Auto-Sync Development Work
```bash
# 1. Start auto-sync (once, runs in background)
python auto_sync.py &

# 2. Work on your projects
vim ~/jade-workspace/terraform/main.tf

# 3. Changes are auto-captured
# Query recent work:
python -c "
from GP_RAG.jade_rag_langgraph import JadeRAGAgent
agent = JadeRAGAgent()
result = agent.query('What Terraform changes did I make today?')
print(result['response'])
"
```

### Workflow 3: Query Security Scans
```bash
# Scans are already loaded (1,658 findings!)
# Query the knowledge graph:
python -c "
from GP_RAG.jade_rag_langgraph import JadeRAGAgent
agent = JadeRAGAgent()

# This uses BOTH graph traversal AND vector search
result = agent.query('Show me all SQL injection findings')
print(result['response'])
print(f\"Graph nodes traversed: {len(result['graph_nodes'])}\")
print(f\"Paths: {result['graph_paths']}\")
"
```

---

## Troubleshooting 🔧

### "No module named 'watchdog'"
```bash
# Option 1: Install watchdog
pip install watchdog

# Option 2: Use simple_learn.py (no watchdog needed)
python simple_learn.py
```

### "ChromaDB error"
```bash
# Re-initialize RAG engine
python GP-AI/core/rag_engine.py
```

### "Knowledge graph not found"
```bash
# Rebuild graph from scratch
python GP-AI/core/rag_graph_engine.py

# Or populate from scans
python GP-AI/core/scan_graph_integrator.py GP-DATA/active/scans/
```

### "Import errors"
```bash
# Make sure you're in the right directory
cd /home/jimmie/linkops-industries/GP-copilot
source ai-env/bin/activate
python GP-RAG/simple_learn.py
```

---

## Summary ✨

**GP-RAG contains Jade's learning and reasoning system:**

### What You Do:
1. Drop docs in `unprocessed/`
2. Run `python simple_learn.py`
3. Query with `jade` or Python

### What Jade Does:
- **Learns** from your documents (vector embeddings)
- **Reasons** with knowledge graph (CVE → CWE → OWASP → Findings)
- **Combines** both for intelligent answers

### Key Points:
- ✅ **Simple**: Drop & learn in 2 steps
- ✅ **Smart**: Relationship-aware intelligence
- ✅ **Real data**: 1,658 findings already loaded
- ✅ **Clean**: No cruft, just what you need

---

**For security scan ingestion**, use `GP-AI/core/scan_graph_integrator.py` instead.

---

Last updated: 2025-10-07
