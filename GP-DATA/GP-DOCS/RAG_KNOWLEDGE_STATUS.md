# RAG & Knowledge Graph Status Summary

**Date**: 2025-10-07
**Current Status**: Dual RAG System (Vectors + Graph) Operational

---

## Current Knowledge Base

### 📊 Vector Store (ChromaDB): **591 vectors**

| Collection | Vectors | Content Type |
|------------|---------|--------------|
| **cks_knowledge** | 63 | Kubernetes security, CKS exam prep |
| **compliance_frameworks** | 78 | OPA policies, Rego language, compliance |
| **security_patterns** | 122 | ArgoCD, Helm, K8s automation, DevOps |
| **troubleshooting** | 208 | Troubleshooting guides (pre-existing) |
| **dynamic_learning** | 83 | Dynamic learning content (pre-existing) |
| **documentation** | 37 | Documentation (pre-existing) |
| **scan_findings** | 0 | **NOT YET INGESTED** ⚠️ |
| **client_knowledge** | 0 | Empty |
| **project_context** | 0 | Empty |
| **TOTAL** | **591** | |

### 🕸️ Knowledge Graph (NetworkX): **272 nodes, 713 edges**

| Node Type | Count | Description |
|-----------|-------|-------------|
| **cks_concept** | 63 | CKS training concepts |
| **opa_concept** | 67 | OPA general concepts |
| **opa_policy** | 11 | Specific OPA policies |
| **devops_pattern** | 92 | DevOps patterns |
| **helm_pattern** | 21 | Helm-specific patterns |
| **k8s_pattern** | 8 | Kubernetes patterns |
| **argocd_pattern** | 1 | ArgoCD patterns |
| **cis_benchmark** | 5 | CIS Kubernetes benchmarks |
| **owasp_category** | 4 | OWASP Top 10 categories |
| **TOTAL** | **272** | |

**Edge Types**: 713 relationships
- `maps_to`: Knowledge → CIS benchmarks
- `validates`: OPA policies → CIS benchmarks
- `implements`: OPA → CKS concepts
- `applies_to`: Patterns → CKS concepts
- `categorized_as`: Patterns → OWASP categories

---

## What's Missing: Scan Results

### 🔍 Available but NOT Ingested

**Location**: `/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/scans/`

**Total Scan Files**: 119 JSON files
**Estimated Findings**: **~18,271 security findings**

**Scanners**:
- Bandit (Python SAST)
- Trivy (container/dependency vulnerabilities)
- Semgrep (SAST patterns)
- Gitleaks (secret detection)
- Checkov (IaC security)
- tfsec (Terraform security)
- OPA (policy violations)
- kube-hunter (Kubernetes security)

**Why Not Ingested Yet**:
- ChromaDB duplicate ID errors
- Need to fix ID generation in `ingest_scan_results.py`
- Estimated ingestion time: 10-15 minutes for all 119 files

---

## Architecture Comparison

### Current: Dual RAG System

```
┌──────────────────────────────┐     ┌──────────────────────────────┐
│   Vector RAG (ChromaDB)      │     │  Graph RAG (NetworkX)        │
│                              │     │                              │
│  591 documents               │     │  272 nodes                   │
│  9 collections               │     │  713 edges                   │
│                              │     │                              │
│  Query: Semantic similarity  │     │  Query: Relationship hops    │
│  Speed: Fast (<100ms)        │     │  Speed: Fast (graph traverse)│
│  Use: "Find similar docs"    │     │  Use: "Find connected concepts"│
└──────────────────────────────┘     └──────────────────────────────┘
```

### What Each System Excels At

**Vector RAG (ChromaDB)**:
- ✅ Semantic search ("Find documents about RBAC wildcards")
- ✅ Similarity matching ("What's similar to this vulnerability?")
- ✅ Fast retrieval
- ❌ No relationship awareness
- ❌ No multi-hop reasoning

**Graph RAG (NetworkX)**:
- ✅ Relationship traversal ("Show me CKS concepts related to CIS-5.1.3")
- ✅ Multi-hop reasoning ("CVE → CWE → OPA Policy → Fix")
- ✅ Compliance mapping
- ❌ No semantic similarity
- ❌ Requires explicit relationships

**Combined Power**:
- Use vectors to find relevant documents
- Use graph to find related concepts and compliance mappings
- Best of both worlds for Jade's AI reasoning

---

## Answer to Your Question

> "yes and have it set up so it always does. how many vectors do we have now?"

### Vectors: **591**

**Breakdown**:
- 263 from JSONL training files (CKS, OPA, cloud) ← **NEW**
- 328 pre-existing (troubleshooting, docs, learning)

### Graph Nodes: **272** (also new!)

**What's Auto-Graphed**:
- ✅ JSONL knowledge → Graph relationships
- ✅ CIS benchmark connections
- ✅ OWASP category mappings
- ✅ Cross-knowledge relationships

### What's NOT Yet Added: **~18,271 scan findings**

**Issue**: Duplicate ID errors in scan ingestion
**Fix Required**: Update `ingest_scan_results.py` with better ID generation
**Estimated Time**: 15 minutes to fix + 10 minutes to ingest

---

## Created Infrastructure

### 1. Vector Ingestion: `GP-RAG/ingest_jade_knowledge.py`

**Features**:
- Processes JSONL (conversation + document formats)
- Auto-classification by file name
- ChromaDB metadata compatibility
- CPU-only mode (RTX 5080 compatibility)
- Dry-run testing

**Usage**:
```bash
python GP-RAG/ingest_jade_knowledge.py
python GP-RAG/ingest_jade_knowledge.py --file cks-training1.jsonl
python GP-RAG/ingest_jade_knowledge.py --dry-run
```

### 2. Graph Ingestion: `GP-RAG/graph_ingest_knowledge.py`

**Features**:
- Extracts knowledge from RAG collections
- Creates semantic relationships
- Links to CIS benchmarks
- Links to OWASP categories
- Cross-knowledge connections

**Usage**:
```bash
python GP-RAG/graph_ingest_knowledge.py
python GP-RAG/graph_ingest_knowledge.py --dry-run
```

**Results**: 272 nodes, 713 edges added to graph

### 3. Scan Ingestion: `GP-RAG/ingest_scan_results.py` (IN PROGRESS)

**Features**:
- Parses Bandit, Trivy, Semgrep, etc.
- Converts findings to RAG documents
- Links findings to CVEs/CWEs in graph
- Batch processing

**Status**: ⚠️ Needs duplicate ID fix

**Usage** (when fixed):
```bash
python GP-RAG/ingest_scan_results.py --limit 20  # Test with 20 files
python GP-RAG/ingest_scan_results.py            # Process all 119 files
```

---

## Auto-Ingestion Setup

### Option 1: Manual Workflow (Current)

```bash
# When adding new JSONL knowledge
cd GP-RAG
python ingest_jade_knowledge.py              # → Vectors
python graph_ingest_knowledge.py            # → Graph

# When new scans complete
python ingest_scan_results.py               # → Vectors + Graph
```

### Option 2: Auto-Trigger (Future - Recommended)

**Hook into scan completion**:
```python
# In scan_workflow.py or similar
def on_scan_complete(scan_file):
    # Auto-ingest to RAG
    subprocess.run(['python', 'GP-RAG/ingest_scan_results.py',
                   '--file', scan_file])
```

**File watcher for JSONL** (from `auto_sync.py`):
```python
# Already exists in GP-RAG/auto_sync.py
# Monitors GP-RAG/unprocessed/jade-knowledge/
# Can be extended to auto-run ingestion
```

### Option 3: Scheduled Sync (Cron)

```bash
# Add to crontab
*/30 * * * * cd /home/jimmie/linkops-industries/GP-copilot/GP-RAG && python ingest_scan_results.py
```

---

## Next Steps to Reach Full Capacity

### Immediate (Fix Scan Ingestion)

1. **Fix duplicate IDs** in `ingest_scan_results.py`
   - Use timestamp + counter instead of hash
   - Test with `--limit 5`

2. **Ingest all 119 scan files**
   - Will add **~18,000 findings**
   - New total: **~18,591 vectors**

3. **Update knowledge graph**
   - Link findings → CVEs
   - Link findings → CWEs
   - Connect to OWASP categories

### Short-term (Auto-Ingestion)

4. **Integrate with scan workflows**
   - Hook `scan_workflow.py` to auto-ingest
   - Real-time RAG updates

5. **Add file watcher**
   - Monitor GP-RAG/unprocessed/
   - Auto-process new JSONL files

### Long-term (Scaling)

6. **Incremental ingestion**
   - Only add new findings (avoid re-processing)
   - Track ingested scan IDs

7. **Graph query interface**
   - Jade chat integration
   - "Show me all CKS concepts related to this CVE"
   - Multi-hop compliance mapping

8. **Knowledge versioning**
   - Track knowledge updates
   - Re-embedding when needed

---

## Expected Final State

### When Scan Ingestion Completes

**Vectors**: **~18,591**
- 591 current (training + docs)
- ~18,000 scan findings

**Graph Nodes**: **~20,000+**
- 272 current (knowledge concepts)
- ~18,000 findings
- ~1,000 CVEs
- ~500 CWEs
- ~10 OWASP categories

**Graph Edges**: **~40,000+**
- 713 current (knowledge relationships)
- ~18,000 finding → CVE links
- ~18,000 finding → CWE links
- ~2,000 CVE → CWE links

---

## Demo Capabilities

### Current (591 vectors, 272 nodes)

✅ "What are CKS best practices for RBAC?"
✅ "Show me OPA policies for pod security"
✅ "How do I automate ArgoCD syncs?"
✅ "Which CIS benchmarks relate to RBAC?"

### After Scan Ingestion (~18,591 vectors, ~20,000 nodes)

✅ "What vulnerabilities did we find in project X?"
✅ "Show me all HIGH severity Bandit findings"
✅ "Which CVEs affect our Python dependencies?"
✅ "Map this finding to OWASP Top 10"
✅ "Show CKS concepts related to CVE-2024-XXXX"
✅ "Find all findings that violate CIS-5.1.3"

---

## File Locations

**Ingestion Scripts**:
- `GP-RAG/ingest_jade_knowledge.py` ← Vector ingestion for JSONL
- `GP-RAG/graph_ingest_knowledge.py` ← Graph building from vectors
- `GP-RAG/ingest_scan_results.py` ← Scan results (needs fix)

**Data Storage**:
- Vectors: `GP-DATA/knowledge-base/chroma/`
- Graph: `GP-DATA/knowledge-base/security_graph.pkl`
- Scan Results: `GP-DATA/active/scans/` (119 files)

**RAG Engine**:
- `GP-AI/core/rag_engine.py` ← Vector RAG
- `GP-AI/core/rag_graph_engine.py` ← Graph RAG (infrastructure exists)

---

## Summary

**What We Have**:
- ✅ 591 vectors (training knowledge)
- ✅ 272 graph nodes with 713 relationships
- ✅ Auto-graphing pipeline working
- ✅ Dual RAG architecture operational

**What's Pending**:
- ⚠️ 18,271 scan findings (need duplicate ID fix)
- ⚠️ Auto-ingestion hooks
- ⚠️ Jade chat graph query integration

**Current Capability**: Jade can answer training/knowledge questions using both semantic search and graph relationships

**Future Capability** (after scan ingestion): Jade can answer questions about actual vulnerabilities found in your projects, map them to compliance frameworks, and suggest fixes based on real scan data

---

**Status**: PARTIALLY COMPLETE
**Blockers**: Scan ingestion duplicate IDs
**ETA to Full Ingestion**: 30 minutes (15min fix + 15min ingest)
**Total Expected Vectors**: ~18,591
**Total Expected Graph Nodes**: ~20,000+
