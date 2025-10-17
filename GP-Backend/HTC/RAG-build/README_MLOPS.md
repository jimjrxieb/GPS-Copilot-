# GP-RAG MLOps - Quick Reference

**Your Vision**: Learning models for Jade that predict better quality OPA policies and learn from troubleshooting to improve confidence.

---

## 📚 Documentation Map

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[README.md](README.md)** | GP-RAG user guide | First time using RAG |
| **[RAG_ARCHITECTURE_EXPLAINED.md](RAG_ARCHITECTURE_EXPLAINED.md)** | How RAG + Graph + LangGraph works | Understanding the foundation |
| **[MLOPS_LEARNING_ARCHITECTURE.md](MLOPS_LEARNING_ARCHITECTURE.md)** | ML models design & learning loops | Understanding the vision |
| **[MLOPS_IMPLEMENTATION_STATUS.md](MLOPS_IMPLEMENTATION_STATUS.md)** | What exists vs what's planned | Starting implementation |
| **This file** | Quick reference & shortcuts | Daily use |

---

## ⚡ Quick Commands

### Using RAG (What Works Today)

```bash
# Add new knowledge (easiest way)
cp ~/my-document.md GP-RAG/unprocessed/
python3 GP-RAG/simple_learn.py

# Start file watcher (continuous learning)
python3 GP-RAG/dynamic_learner.py watch

# Query knowledge
python3 -c "
from GP_RAG.jade_rag_langgraph import JadeRAGAgent
agent = JadeRAGAgent()
result = agent.query('What is our password policy?')
print(f\"Confidence: {result['confidence']:.2f}\")
print(result['response'])
"

# Check stats
python3 -c "
from GP_RAG.dynamic_learner import DynamicLearner
learner = DynamicLearner()
stats = learner.get_stats()
print(f\"Total chunks: {stats['total_chunks']}\")
print(f\"Categories: {stats['categories']}\")
"
```

---

## 🧠 The 4 ML Models

### 1. Policy Ranker (Task Ranker)
- **Status**: 🔄 Designed, not implemented
- **Purpose**: Ranks top-5 policies for a resource
- **Input**: K8s resource features (privileged, hostPath, etc.)
- **Output**: Policy recommendations with confidence scores
- **Target**: hit@5 >= 0.85

### 2. Fix Strategy Classifier
- **Status**: 🔄 Designed, not implemented
- **Purpose**: Decides manifest patch vs policy change
- **Input**: Severity, revert history, FP score, reliability
- **Output**: "manifest_patch" or "policy_change"
- **Learning**: From developer acceptance/rejection

### 3. Latency Regressor
- **Status**: 🔄 Designed, not implemented
- **Purpose**: Predicts webhook timeout risk
- **Input**: Rego AST size, comprehension depth, array ops
- **Output**: Estimated milliseconds
- **Use**: Warns before deploying slow policies

### 4. Policy Drafter
- **Status**: 🔄 LLM ready (Qwen2.5), needs workflow
- **Purpose**: Generates Rego + tests from examples
- **Input**: Resource + similar policies (RAG)
- **Output**: Rego code + unit tests + rationale
- **Guardrails**: Schema validation, test pass rate, FP limit

---

## 🎯 Current Status

### ✅ What Works (Production Ready):

| Component | Location | Status |
|-----------|----------|--------|
| Vector Search | `core/jade_engine.py` | ✅ 328+ docs |
| Knowledge Graph | `GP-DATA/knowledge-base/security_graph.pkl` | ✅ 1,658 findings |
| LangGraph | `jade_rag_langgraph.py` | ✅ Reasoning workflows |
| Basic Confidence | `jade_rag_langgraph.py:413-425` | ✅ Simple scoring |
| Dynamic Learning | `dynamic_learner.py` | ✅ File watcher |
| Simple Learning | `simple_learn.py` | ✅ Drop & learn |

### 🔄 What's Planned (Blueprint Complete):

| Component | Design Doc | Implementation |
|-----------|-----------|----------------|
| Policy Ranker | `mlops2.json:216-223` | ⏳ Not started |
| Fix Classifier | `mlops2.json:224-229` | ⏳ Not started |
| Latency Regressor | `mlops2.json:230-235` | ⏳ Not started |
| Policy Drafter | `mlops2.json:236-240` | ⏳ Needs workflow |
| Troubleshooter | `mlops2.json:158-163` | ⏳ Not started |
| MLflow Registry | `mlops2.json:75-76` | ⏳ Not started |
| Drift Monitor | `mlops2.json:59,165-169` | ⏳ Not started |
| FastAPI Service | `mlops2.json:139-176` | ⏳ Not started |

---

## 🚀 Implementation Priority

### Phase 1: Policy Ranker (Start Here!)

**Why first?**
- ✅ Immediate value
- ✅ Simple baseline (heuristic → ML)
- ✅ Clear metrics (hit@5)
- ✅ Foundation for other models

**Steps**:
```bash
# 1. Create policy corpus
mkdir -p kube-pac-copilot/policies/{gatekeeper,conftest}
touch kube-pac-copilot/policies/index.jsonl

# 2. Port existing policies from GP-CONSULTING
# Add metadata (kind, features, reliability)

# 3. Build heuristic ranker (baseline)
python kube-pac-copilot/src/rank/heuristic.py

# 4. Collect training data (bootstrap with manual labeling)

# 5. Train ML model
python kube-pac-copilot/src/rank/train.py

# 6. Evaluate
python kube-pac-copilot/src/rank/evaluate.py
```

**Timeline**: 1-2 weeks

---

### Phase 2: Fix Classifier + Troubleshooter

**Why second?**
- ✅ Enables learning from failures
- ✅ Improves confidence over time
- ✅ Real feedback loop

**Steps**:
```bash
# 1. Implement failure logging
# Log every fix attempt with outcome

# 2. Build troubleshooter
python kube-pac-copilot/src/troubleshoot/classifiers.py

# 3. Generate counterexamples
python kube-pac-copilot/src/troubleshoot/counterexample.py

# 4. Train Fix Classifier
python kube-pac-copilot/src/troubleshoot/train_classifier.py

# 5. Set up MLflow tracking
mlflow server --backend-store-uri sqlite:///mlflow.db
```

**Timeline**: 2-3 weeks

---

### Phase 3: Production Readiness

**Why third?**
- ✅ Makes everything robust
- ✅ Enables monitoring
- ✅ Production deployment

**Steps**:
```bash
# 1. FastAPI service
uvicorn kube-pac-copilot.api.app:app --reload

# 2. Drift monitoring
python kube-pac-copilot/src/drift/monitor.py

# 3. Latency regressor
python kube-pac-copilot/src/troubleshoot/train_latency.py

# 4. CI/CD integration
# Add .github/workflows/policy_scan.yml

# 5. Docker Compose deployment
docker-compose up
```

**Timeline**: 2-3 weeks

---

## 🔍 How to Check Current State

### RAG Stats:
```python
from GP_RAG.core.jade_engine import rag_engine
stats = rag_engine.get_stats()
print(f"Documents: {stats['total_documents']}")
print(f"Collections: {list(stats['collections'].keys())}")
```

### Knowledge Graph Stats:
```python
import pickle
from pathlib import Path

graph_file = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/knowledge-base/security_graph.pkl")
if graph_file.exists():
    with open(graph_file, 'rb') as f:
        graph = pickle.load(f)
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")
else:
    print("Graph not found")
```

### Confidence System:
```python
from GP_RAG.jade_rag_langgraph import JadeRAGAgent

agent = JadeRAGAgent()
result = agent.query("Test query")

print(f"Confidence: {result['confidence']:.2f}")
print(f"Domain: {result['domain']}")
print(f"Sources: {len(result['sources'])}")
print(f"Reasoning steps: {len(result['reasoning'])}")
```

---

## 📊 Training Data Needed

### For Policy Ranker:
- **Dataset**: `policies/index.jsonl`
- **Format**: `{"id": "...", "kind": [...], "features": [...], "reliability": "..."}`
- **Minimum**: 50-100 labeled policies
- **Status**: 🔄 Need to create

### For Fix Classifier:
- **Dataset**: `data/failures/failure_log.jsonl`
- **Format**: `{"policy_id": "...", "failure_type": "...", "accepted": true, ...}`
- **Minimum**: 200-500 failure events
- **Status**: 🔄 Need to start collecting

### For Latency Regressor:
- **Dataset**: Webhook timing logs
- **Format**: `{"policy_id": "...", "ast_size": 1200, "actual_latency_ms": 45.3}`
- **Minimum**: 100-200 executions
- **Status**: 🔄 Need to instrument webhooks

---

## 🎓 Key Concepts

### Confidence Evolution:
```
Initial (No History)
├── Confidence: 0.55 (LOW)
├── Based on: RAG distance only
└── Behavior: Uncertain suggestions

After 10 Successes
├── Confidence: 0.75 (MEDIUM)
├── Based on: RAG distance + historical success
└── Behavior: More assertive

After 50 Successes
├── Confidence: 0.92 (HIGH)
├── Based on: All factors (ranker + reliability + FP + latency)
└── Behavior: Confident recommendations
```

### Learning Loop:
```
1. Jade suggests fix (using Policy Ranker)
2. Run tests in CI (opa test + conftest)
3. Developer accepts or reverts
4. Log outcome to failure_log.jsonl
5. Retrain models weekly (or on drift)
6. Confidence improves for similar patterns
```

### Model Interaction:
```
User submits K8s manifest
    ↓
Feature Extractor → {privileged: true, hostPath: false, ...}
    ↓
Policy Ranker → Top-5 policies with scores
    ↓
Policy Drafter → Generate Rego + tests
    ↓
Latency Regressor → Check performance risk
    ↓
Test Runner → opa test + conftest
    ↓
    ├─ Pass → Log success, increase confidence
    └─ Fail → Troubleshooter → Classify → Fix Classifier → Recommend action
```

---

## 🐛 Troubleshooting

### "No module named 'watchdog'"
```bash
pip install watchdog
# OR use simple_learn.py instead (no watchdog needed)
```

### "ChromaDB not found"
```bash
# Check database location
ls -la GP-DATA/knowledge-base/chroma/

# Reinitialize if needed
python3 GP-AI/core/rag_engine.py
```

### "Confidence always 0.3"
This is expected when:
- No retrieved knowledge (query doesn't match anything)
- Empty RAG database

Check:
```python
result = agent.query("test")
print(f"Retrieved: {len(result.get('retrieved_knowledge', []))}")
# If 0, add more documents to RAG
```

### "Import errors"
```bash
# Ensure correct directory
cd /home/jimmie/linkops-industries/GP-copilot

# Activate virtual environment
source ai-env/bin/activate

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"
```

---

## 🔗 Related Components

### GP-CONSULTING Integration:
```
GP-CONSULTING/1-Security-Assessment/
├── ci-scanners/          → Findings feed into RAG
├── cd-scanners/          → Findings feed into RAG
└── runtime-monitors/     → Findings feed into RAG

GP-CONSULTING/2-App-Fixes/
├── fixers/               → Apply recommendations from ML models
└── validators/           → Test fixes, log outcomes

GP-CONSULTING/6-Auto-Agents/
└── *_agent.py            → Use RAG + ML models for decisions
```

### GP-DATA Integration:
```
GP-DATA/
├── active/scans/         → Input to knowledge graph
├── active/fixes/         → Training data for Fix Classifier
├── knowledge-base/
│   ├── chroma/           → Vector database (RAG)
│   └── security_graph.pkl → Knowledge graph
└── metadata/             → Model metadata
```

---

## 📝 Next Steps

1. **Review Documentation**:
   - [ ] Read [MLOPS_LEARNING_ARCHITECTURE.md](MLOPS_LEARNING_ARCHITECTURE.md)
   - [ ] Read [MLOPS_IMPLEMENTATION_STATUS.md](MLOPS_IMPLEMENTATION_STATUS.md)
   - [ ] Understand current vs target state

2. **Decide Priority**:
   - [ ] Which model to build first? (Recommended: Policy Ranker)
   - [ ] Timeline? (Suggested: 6-week phased approach)
   - [ ] Resources needed? (Training data, compute)

3. **Set Up Infrastructure**:
   - [ ] Create policy corpus structure
   - [ ] Set up MLflow server
   - [ ] Create training data collection pipeline
   - [ ] Set up Grafana dashboards

4. **Start Implementation**:
   - [ ] Build heuristic ranker (baseline)
   - [ ] Port policies from GP-CONSULTING
   - [ ] Collect initial training data
   - [ ] Train Policy Ranker v1
   - [ ] Evaluate and iterate

---

## 🎯 Success Criteria

When MLOps is complete, you'll have:

✅ **Policy Ranker**: Top-5 recommendations (hit@5 >= 0.85)
✅ **Fix Classifier**: Smart manifest vs policy decisions
✅ **Latency Regressor**: No webhook timeouts
✅ **Policy Drafter**: RAG-grounded Rego generation (95% test pass)
✅ **Troubleshooter**: Automated failure analysis + counterexamples
✅ **Learning Loop**: Confidence improves from troubleshooting
✅ **Drift Monitor**: Environment change detection
✅ **MLflow Tracking**: Model versioning and experiment management
✅ **CI Integration**: GitHub Actions with SARIF reports
✅ **Production API**: FastAPI service with health checks

**Result**: Jade learns from experience, gets smarter over time, and generates better quality policies! 🚀

---

Last updated: 2025-10-16
