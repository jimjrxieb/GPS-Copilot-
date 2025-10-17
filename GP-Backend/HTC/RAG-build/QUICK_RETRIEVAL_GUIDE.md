# 🚀 Quick Guide: Using Jade's Embedded Knowledge

**Last Updated**: 2025-10-16
**Status**: ✅ Fully operational with 121 embedded documents

---

## 📚 What Knowledge is Available?

| Collection | Documents | Content |
|-----------|-----------|---------|
| **patterns** | 87 | Kubernetes, Terraform, OPA, security guides |
| **docs** | 31 | James-OS architecture, agent patterns, testing |
| **client** | 3 | ACME Corp security requirements |
| **compliance** | 0 | (Ready for PCI-DSS, SOC2, HIPAA guides) |
| **cks** | 0 | (Ready for CKS study materials) |
| **scans** | 0 | (Ready for scan findings) |
| **projects** | 0 | (Ready for project context) |

---

## 🔍 Query Examples

### Via Python API

```python
from GP_RAG.core import rag_engine

# Query security patterns
results = rag_engine.query_knowledge(
    "Kubernetes pod security policies",
    "patterns",  # Use SHORT collection name!
    n_results=5
)

for result in results:
    print(result['content'])
    print(result.get('source', 'Unknown'))
    print('-' * 60)
```

### Available Queries

**Kubernetes Security:**
```python
results = rag_engine.query_knowledge("Kubernetes RBAC best practices", "patterns", n_results=3)
results = rag_engine.query_knowledge("Pod Security Standards", "patterns", n_results=3)
results = rag_engine.query_knowledge("Network policies", "patterns", n_results=3)
```

**Terraform & IaC:**
```python
results = rag_engine.query_knowledge("Terraform security hardening", "patterns", n_results=3)
results = rag_engine.query_knowledge("S3 bucket encryption", "patterns", n_results=3)
results = rag_engine.query_knowledge("OPA policy examples", "patterns", n_results=3)
```

**James-OS Architecture:**
```python
results = rag_engine.query_knowledge("agent design patterns", "docs", n_results=3)
results = rag_engine.query_knowledge("architectural principles", "docs", n_results=3)
results = rag_engine.query_knowledge("testing standards", "docs", n_results=3)
```

**Client Requirements:**
```python
results = rag_engine.query_knowledge("ACME Corp security requirements", "client", n_results=3)
```

---

## 🤖 Via Jade Chat

```bash
cd /home/jimmie/linkops-industries/GP-copilot
./bin/jade chat

# Then ask questions:
> "Show me Kubernetes security best practices"
> "How do I secure Terraform deployments?"
> "What are ACME Corp's security requirements?"
> "Explain OPA admission control"
```

**Note**: Jade chat automatically selects the right collection based on your question!

---

## 🧪 Via LangGraph Workflow

```python
from GP_RAG.jade_rag_langgraph import JadeRAGAgent

# Create agent
agent = JadeRAGAgent()

# Ask question (agent retrieves knowledge automatically)
response = agent.query("How do I implement pod security policies?")
print(response['answer'])

# Structured reasoning
response = agent.query("Recommend fixes for exposed S3 bucket")
print(f"Reasoning: {response['reasoning']}")
print(f"Answer: {response['answer']}")
print(f"Sources: {response.get('sources', [])}")
```

---

## 🛠️ Adding New Knowledge

### Option 1: Simple Drop & Learn

```bash
# Drop markdown file in processed/
cp my-new-security-guide.md /home/jimmie/linkops-industries/GP-copilot/GP-Backend/GP-RAG/processed/security-docs/

# Re-embed
CUDA_VISIBLE_DEVICES="" python3 reembed_processed_files.py
```

### Option 2: Direct Embedding

```python
from GP_RAG.core import rag_engine

# Add documents directly
documents = [{
    "content": "Your markdown content here...",
    "metadata": {
        "source": "my-guide.md",
        "category": "patterns",
        "author": "Security Team"
    },
    "id": "unique-doc-id-123"
}]

rag_engine.add_security_knowledge("patterns", documents)
```

### Option 3: Automated Learning (Watch Directory)

```bash
# Start file watcher
python3 dynamic_learner.py

# Drop files into processed/ - automatically embedded!
```

---

## 📊 Check ChromaDB Stats

```python
from GP_RAG.core import rag_engine

stats = rag_engine.get_stats()
print(f"Total documents: {stats['total_documents']}")

for collection, count in stats['collections'].items():
    if count > 0:
        print(f"  {collection}: {count} documents")
```

---

## 🔧 Troubleshooting

### Issue: "CUDA error: no kernel image available"
**Cause**: RTX 5080 GPU (sm_120) not compatible with PyTorch (supports sm_50-sm_90)

**Fix**: Force CPU mode
```bash
CUDA_VISIBLE_DEVICES="" python3 your_script.py
```

### Issue: "No results found"
**Cause 1**: Using wrong collection name (full name instead of short name)
```python
# ❌ WRONG
results = rag_engine.query_knowledge("query", "security_patterns", n_results=5)

# ✅ CORRECT
results = rag_engine.query_knowledge("query", "patterns", n_results=5)
```

**Cause 2**: Knowledge not embedded yet
```bash
# Re-embed all files
CUDA_VISIBLE_DEVICES="" python3 reembed_processed_files.py --verify
```

### Issue: "Collection not found"
**Valid collection names** (SHORT names only):
- `patterns` - Security patterns, guides
- `client` - Client knowledge
- `docs` - Documentation
- `compliance` - Compliance frameworks
- `cks` - CKS knowledge
- `scans` - Scan findings
- `projects` - Project context

---

## 🎓 AWS AI Practitioner Exam Alignment

This RAG system demonstrates key concepts:

### Domain 1: Fundamentals of AI/ML
- Vector embeddings (sentence-transformers)
- Similarity search (ChromaDB)
- Model inference (all-MiniLM-L6-v2)

### Domain 2: Generative AI
- RAG architecture (Retrieval + Generation)
- Knowledge bases
- Context augmentation

### Domain 3: Foundation Models
- Embedding models
- LLM integration (via LangGraph)
- Multi-collection retrieval

### Domain 4: Responsible AI
- Data organization (client data isolated)
- Transparency (metadata tracking)
- Reliability (verification tests)

**See [LEARNING_GUIDE.md](LEARNING_GUIDE.md) for full study path!**

---

## 📁 File Locations

```
GP-copilot/
├── GP-Backend/GP-RAG/
│   ├── processed/              ← Source markdown files (25 files)
│   ├── reembed_processed_files.py  ← Embedding script
│   ├── core/__init__.py        ← Import layer from GP-AI
│   └── mlops/                  ← Your ML models (TO BUILD)
│
├── GP-Frontend/GP-AI/core/
│   ├── rag_engine.py           ← RAG implementation (SOURCE OF TRUTH)
│   └── rag_graph_engine.py     ← Knowledge graph
│
└── GP-DATA/knowledge-base/
    ├── chroma/                 ← ChromaDB (2.5MB, 121 docs) ✅
    └── security_graph.pkl      ← NetworkX graph
```

---

## 🚀 Next Steps for MLOps

Now that RAG knowledge is embedded, you can build ML models that USE this knowledge:

### Model 1: Policy Ranker
**Input**: OPA violation
**Output**: Priority score (1-10)
**Training Data**: Historical violations + embedded patterns
**Uses RAG**: Retrieve similar violations for context

### Model 2: Fix Classifier
**Input**: Security finding
**Output**: Fix type (automated/manual/skip)
**Training Data**: Past fixes + scan results
**Uses RAG**: Retrieve fix patterns from security guides

### Model 3: Latency Regressor
**Input**: Scan parameters
**Output**: Predicted scan time (seconds)
**Training Data**: Historical scan logs
**Uses RAG**: Retrieve similar scan configurations

### Model 4: Policy Drafter
**Input**: Resource description
**Output**: Draft OPA policy
**Training Data**: Existing policies + security guides
**Uses RAG**: Retrieve policy templates and patterns

**Location**: `/home/jimmie/linkops-industries/GP-copilot/GP-Backend/GP-RAG/mlops/`

**See [LEARNING_GUIDE.md](LEARNING_GUIDE.md) for week-by-week implementation plan!**

---

## ✅ Verification

Run this to verify everything works:

```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-Backend/GP-RAG

# Test retrieval
CUDA_VISIBLE_DEVICES="" python3 -c "
from core import rag_engine

results = rag_engine.query_knowledge('Kubernetes security', 'patterns', n_results=1)
print(f'✅ Found: {results[0][\"content\"][:100]}...')

stats = rag_engine.get_stats()
print(f'📊 Total docs: {stats[\"total_documents\"]}')
"
```

Expected output:
```
✅ Found: # Kubernetes Security Comprehensive Guide...
📊 Total docs: 121
```

---

## 📖 Related Docs

- [EMBEDDING_SUCCESS_REPORT.md](EMBEDDING_SUCCESS_REPORT.md) - Full embedding report
- [CORE_DIRECTORY_ANALYSIS.md](CORE_DIRECTORY_ANALYSIS.md) - Architecture cleanup
- [PROCESSED_FILES_ANALYSIS.md](PROCESSED_FILES_ANALYSIS.md) - Why files needed re-embedding
- [LEARNING_GUIDE.md](LEARNING_GUIDE.md) - AWS AI Practitioner study guide

---

**Status**: ✅ Fully operational
**ChromaDB Location**: `/home/jimmie/linkops-industries/GP-copilot/GP-DATA/knowledge-base/chroma/`
**Total Documents**: 121 (31 docs + 87 patterns + 3 client)
**Last Verified**: 2025-10-16
