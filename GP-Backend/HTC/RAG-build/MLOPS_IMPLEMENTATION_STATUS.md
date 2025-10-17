# MLOps Implementation Status - What Exists vs What's Planned

**Date**: 2025-10-16
**Owner**: Jimmie Coleman / LinkOps Industries

---

## Executive Summary 🎯

**Your Vision**: "Learning models for Jade - kube and policy as code predictors that learn and create better and higher quality OPA and manifests. Learn from troubleshooting so Jade can have better confidence. Task ranker included."

**Current Status**:
- ✅ **Foundation Built**: RAG + Knowledge Graph + LangGraph (fully operational)
- ✅ **Basic Confidence Scoring**: Implemented in jade_rag_langgraph.py
- ✅ **Dynamic Learning**: File watcher system operational
- 🔄 **ML Models**: Blueprint complete (mlops2.json), implementation pending
- ⏳ **Task Ranker**: Designed but not implemented
- ⏳ **Troubleshooting Loop**: Architecture ready, needs build

---

## What Exists Today ✅

### 1. **RAG Foundation** (Fully Operational)

**Location**: `GP-Backend/GP-RAG/core/jade_engine.py`

**Components**:
- ChromaDB vector database (18MB, 328+ documents)
- 9 collections: security_patterns, compliance_frameworks, cks_knowledge, documentation, client_knowledge, scan_findings, project_context, troubleshooting, dynamic_learning
- Semantic search with relevance scoring
- Metadata filtering

**Usage**:
```python
from GP_RAG.jade_rag_langgraph import JadeRAGAgent
agent = JadeRAGAgent()
result = agent.query("What is our password policy?")
# Returns: response, confidence, sources, reasoning
```

**Status**: ✅ Production-ready

---

### 2. **Knowledge Graph** (Fully Operational)

**Location**: `GP-DATA/knowledge-base/security_graph.pkl`

**Stats**:
- **1,696 nodes**: 1,658 findings, 15 CWEs, 10 OWASP, 6 tools, 3 projects
- **3,741 edges**: instance_of, categorized_as, detected_by, found_in, fixed_by
- **Real data**: From Trivy, Bandit, Semgrep, Gitleaks, Checkov scans

**Query Examples**:
```python
# Find all SQL injection findings
graph.query("SQL Injection")

# Get all findings from Trivy
graph.neighbors("Trivy", relationship="detected_by")

# Find CVE relationships
graph.path_between("CVE-2023-1234", "OWASP-A03")
```

**Status**: ✅ Production-ready with real findings

---

### 3. **LangGraph Workflow** (Fully Operational)

**Location**: `GP-Backend/GP-RAG/jade_rag_langgraph.py`

**Features**:
- Multi-step reasoning workflow
- Combines vector search + graph traversal
- Qwen2.5-7B-Instruct LLM
- Reasoning chain tracking
- Source citations

**Workflow Steps**:
```
1. classify_domain()     → Detect query type (security, k8s, opa, compliance)
2. graph_traverse()      → Search knowledge graph for relationships
3. retrieve_knowledge()  → Vector search in ChromaDB
4. reason()              → LLM reasoning with context
5. draft_response()      → Generate answer
6. enhance_response()    → Add sources + confidence score
```

**Status**: ✅ Production-ready

---

### 4. **Basic Confidence Scoring** (Operational but Simple)

**Location**: `GP-Backend/GP-RAG/jade_rag_langgraph.py` (lines 413-425)

**Current Implementation**:
```python
def enhance_response(self, state: JadeState) -> JadeState:
    """Enhance response with sources and confidence"""
    knowledge = state["retrieved_knowledge"]
    if knowledge:
        avg_score = sum(doc["relevance_score"] for doc in knowledge) / len(knowledge)
        confidence = min(0.95, max(0.5, 1.0 - avg_score))  # Lower score = higher relevance
    else:
        confidence = 0.3

    state["confidence"] = confidence
    return state
```

**Current Logic**:
- Based ONLY on RAG retrieval scores
- Range: 0.3 (no knowledge) to 0.95 (perfect match)
- Simple inverse relationship with distance metric

**Limitations**:
- ❌ Doesn't learn from troubleshooting history
- ❌ No historical success/failure tracking
- ❌ No policy reliability scores
- ❌ No false positive tracking
- ❌ Static calculation (doesn't improve over time)

**Status**: ✅ Basic version works, needs ML upgrade

---

### 5. **Dynamic Learning System** (Fully Operational)

**Location**: `GP-Backend/GP-RAG/dynamic_learner.py`

**Features**:
- File watcher daemon (watchdog library)
- Automatic document ingestion
- Smart chunking (markdown headers, 2000 char chunks)
- Knowledge type detection
- Archive to processed/

**Supported Formats**: .md, .txt, .json, .yaml, .yml, .log, .pdf (PDF parsing TODO)

**Usage**:
```bash
# Start watcher (continuous)
python3 GP-RAG/dynamic_learner.py watch

# One-time sync
python3 GP-RAG/dynamic_learner.py sync

# Demo mode
python3 GP-RAG/dynamic_learner.py demo
```

**Directories Watched**:
```
GP-RAG/unprocessed/
├── client-docs/      → client_documentation
├── compliance/       → compliance
├── policies/         → policy
├── scan-results/     → scan_findings
├── security-docs/    → security
└── james-os-knowledge/ → system_knowledge
```

**Status**: ✅ Production-ready

---

### 6. **Simple Learning Script** (Fully Operational)

**Location**: `GP-Backend/GP-RAG/simple_learn.py`

**Purpose**: Easiest way to add documents without watchdog dependency

**Usage**:
```bash
# 1. Drop file
cp ~/my-document.md GP-RAG/unprocessed/

# 2. Learn from it
python3 GP-RAG/simple_learn.py
```

**What it does**:
1. Finds all .md and .txt files in unprocessed/
2. Reads content (skips files < 50 chars)
3. Adds to RAG with metadata
4. Moves to processed/
5. Shows stats

**Status**: ✅ Production-ready

---

## What's Planned (Blueprint Complete) 🔄

### 7. **Policy Ranker Model** (THE TASK RANKER!)

**Location**: Designed in `mlops2.json` lines 216-223

**Purpose**: Machine learning model that ranks which policies are most applicable

**Type**: Logistic Regression or Gradient Boosting

**Inputs**:
```json
{
  "resource_kind": "Deployment",
  "securityContext.privileged": true,
  "securityContext.allowPrivilegeEscalation": true,
  "image.tag": "latest",
  "volume.hostPath": true,
  "rbac.wildcard_verbs": false,
  "netpol_present": false
}
```

**Outputs**:
- Top-5 policy recommendations
- Confidence score for each
- Applicability ranking

**Success Metrics**:
- hit@5 >= 0.85 (Top-5 includes correct policy 85% of time)
- inference_ms < 100ms (fast enough for CI)

**Training Data Required**:
```
kube-pac-copilot/policies/index.jsonl
{
  "id": "deny-privileged-pods",
  "kind": ["Pod", "Deployment"],
  "tags": ["cis:1.1.0", "mitre:T1611"],
  "features": ["securityContext.privileged=true"],
  "example_inputs": [...],
  "reliability": "high"
}
```

**Status**: 🔄 Design complete, implementation needed

---

### 8. **Fix Strategy Classifier**

**Location**: Designed in `mlops2.json` lines 224-229

**Purpose**: Decides whether to patch manifest or change policy when something fails

**Type**: Binary classifier (manifest_patch vs policy_change)

**Inputs**:
```python
{
  "severity": "HIGH",
  "developer_revert_history": 3,     # How many times dev reverted Jade's suggestions
  "FP_score": 0.02,                  # False positive likelihood
  "policy_reliability": "medium"      # Historical success rate
}
```

**Output**:
- `manifest_patch` → Fix the YAML (policy is correct)
- `policy_change` → Policy is wrong, fix the Rego

**How It Learns from Troubleshooting**:
```
1. Jade suggests fix
2. Developer accepts or reverts
3. Log to failure_log.jsonl with "accepted": true/false
4. High revert rate = policy might be wrong
5. Model learns: "For this pattern, change policy not manifest"
```

**This is KEY to confidence improvement!**

**Status**: 🔄 Design complete, implementation needed

---

### 9. **Latency Regressor**

**Location**: Designed in `mlops2.json` lines 230-235

**Purpose**: Predicts if a Rego policy will timeout in webhook (performance issue)

**Type**: Linear regression or small tree

**Inputs**:
```python
{
  "rego_ast_size": 1500,           # Lines of Rego code
  "comprehension_depth": 3,        # Nested loops depth
  "array_scan_ops": 12             # Number of array iterations
}
```

**Output**: Estimated milliseconds for webhook execution

**Use Case**:
```python
# Before deploying policy
latency = latency_regressor.predict(policy_ast_features)
if latency > 500:  # ms
    print("⚠️  WARNING: Policy may timeout webhooks!")
    print("Recommendation: Optimize comprehensions or cache results")
```

**Training Data**: Actual webhook latency logs from production

**Status**: 🔄 Design complete, implementation needed

---

### 10. **Prompted Policy Drafter** (RAG-Grounded LLM)

**Location**: Designed in `mlops2.json` lines 236-240

**Purpose**: Uses LLM + RAG to draft or adapt Rego policies with unit tests

**Type**: Qwen2.5-7B-Instruct + Grounded RAG (already available!)

**Grounding Sources**:
1. `policies/index.jsonl` - Curated policy corpus
2. Exemplar Rego code from successful policies
3. Unit tests from working constraints

**Guardrails** (Prevents Hallucination):
```python
1. Schema validation      → Must match OPA structure
2. Unit tests             → Must pass `opa test`
3. FP budget              → Must stay under 5% false positive rate
4. Restricted retrieval   → NO free-text policy invention
```

**Workflow**:
```
1. RAG retrieves 3-5 similar working policies
2. LLM adapts them to new context
3. Generate unit tests (positive + negative cases)
4. Run `opa test` to validate
5. If pass rate < 95%, regenerate with feedback
6. Return policy + tests + rationale
```

**Status**: 🔄 LLM ready (Qwen2.5), needs policy corpus + workflow

---

### 11. **Troubleshooting Intelligence**

**Location**: Designed in `mlops2.json` lines 158-163

**Purpose**: Classify failures, generate counterexamples, suggest fixes

**API Endpoint**: `POST /troubleshoot`

**Request**:
```json
{
  "policy_id": "deny-privileged-pods",
  "rego_code": "package kubernetes.admission...",
  "inputs": [{"kind": "Pod", "spec": {...}}],
  "logs": "Error: evaluation_error at line 42..."
}
```

**Response**:
```json
{
  "failure_type": "logic",              // parse|logic|perf|real
  "culprit_lines": [42, 43],
  "counterexample": {                   // Minimal failing case
    "kind": "Pod",
    "spec": {"containers": [{"securityContext": {"privileged": true}}]}
  },
  "suggested_patch": "Change line 42 to: allow { not input.spec.containers[_].securityContext.privileged }"
}
```

**Failure Types**:
1. **Parse** - Syntax errors in Rego
2. **Logic** - Policy doesn't do what it should
3. **Performance** - Too slow (webhook timeout risk)
4. **Real** - Policy is correct, manifest is wrong

**Learning Loop**:
```
1. Troubleshooter analyzes failure
2. Suggests fix
3. Human accepts or rejects
4. Log to failure_log.jsonl:
   {
     "ts": "2025-10-16T10:30:00Z",
     "policy_id": "deny-privileged-pods",
     "failure_type": "logic",
     "suggested_patch": "...",
     "accepted": true  ← KEY LEARNING SIGNAL
   }
5. Fix Classifier learns from accepted vs rejected patterns
```

**Status**: 🔄 Design complete, implementation needed

---

### 12. **MLflow Model Registry**

**Location**: Designed in `mlops2.json` lines 75-76, 256-259

**Purpose**: Track model versions, experiments, artifacts, metrics

**Structure**:
```
mlflow/
├── ranker_experiments/
│   ├── policy_ranker_v1  ← Baseline (LogisticRegression)
│   ├── policy_ranker_v2  ← Improved (GradientBoosting)
│   └── policy_ranker_v3  ← Current production
├── fix_classifier_experiments/
│   ├── fix_classifier_v1
│   └── fix_classifier_v2
├── latency_regression/
│   └── latency_regressor_v1
└── prompt_tuning/
    ├── prompt_v1_baseline
    ├── prompt_v2_with_examples
    └── prompt_v3_production
```

**Tracked Metrics**:
```python
mlflow.log_metric("hit_at_5", 0.87)
mlflow.log_metric("precision_at_k", 0.82)
mlflow.log_metric("false_positive_rate", 0.03)
mlflow.log_metric("ci_latency_p95", 45.2)
mlflow.log_metric("rego_test_pass_rate", 0.96)
```

**Artifacts Logged**:
- Serialized models (sklearn/torch)
- Confusion matrices
- Drift reports (Evidently HTML)
- Policy exemplar snapshots
- Failure log backups

**Status**: 🔄 Design complete, needs setup

---

### 13. **Drift Monitoring**

**Location**: Designed in `mlops2.json` lines 59, 165-169

**Purpose**: Detect when environment changes (new resource types, violation patterns)

**API Endpoint**: `GET /drift`

**Response**:
```json
{
  "coverage_rate": 0.87,              // % resources with policies
  "violation_trend": [
    {"date": "2025-10-14", "count": 42},
    {"date": "2025-10-15", "count": 38},
    {"date": "2025-10-16", "count": 25}  // Improving!
  ],
  "resource_mix": {
    "Deployment": 45,
    "Pod": 120,
    "Role": 18,
    "NetworkPolicy": 8
  },
  "alerts": [
    {
      "type": "coverage_drop",
      "message": "NetworkPolicy coverage dropped from 90% to 60%",
      "severity": "HIGH"
    }
  ]
}
```

**Evidently Integration**:
- Tracks distribution shifts in resource features
- Detects new security context patterns
- Alerts when violation types change
- Triggers model retraining

**When Drift Detected**:
1. Alert security engineer
2. Trigger model retraining job
3. Update policy corpus
4. Adjust confidence scores

**Status**: 🔄 Design complete, implementation needed

---

### 14. **FastAPI Microservice**

**Location**: Designed in `mlops2.json` lines 139-176

**Purpose**: REST API for all MLOps functionality

**Endpoints**:

```python
POST /analyze
# Feature extraction + violation detection
Request: {"repo_path": "...", "bundle_glob": "**/*.yaml", "kinds": [...]}
Response: {"violations": [...], "recommendations": [...], "sarif_path": "..."}

POST /propose
# Policy ranking (uses Policy Ranker model)
Request: {"resource_json": {...}, "top_n": 5}
Response: {"candidates": [{"policy_id": "...", "score": 0.92, "rego_code": "..."}]}

POST /autofix
# Intelligent fixing (uses Fix Classifier)
Request: {"violation": {...}, "strategy": "auto"}
Response: {"manifest_diff": "...", "policy_diff": "...", "rationale": "..."}

POST /troubleshoot
# Failure analysis + counterexamples
Request: {"policy_id": "...", "rego_code": "...", "logs": "..."}
Response: {"failure_type": "logic", "culprit_lines": [42], "suggested_patch": "..."}

GET /drift
# Environment monitoring
Response: {"coverage_rate": 0.87, "violation_trend": [...], "alerts": [...]}

GET /health
# System health check
Response: {"status": "ok", "version": "1.0"}
```

**Stack**:
- FastAPI (async)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- Docker Compose (deployment)

**Status**: 🔄 Design complete, implementation needed

---

## Implementation Roadmap 🗺️

### Phase 1: MVP (Weeks 1-2) - Foundation

**Goal**: Get basic policy recommendation working with CI integration

**Tasks**:
1. ✅ Set up policy corpus structure
   ```bash
   mkdir -p kube-pac-copilot/policies/{gatekeeper,conftest}
   touch kube-pac-copilot/policies/index.jsonl
   ```

2. ✅ Create 10-20 curated OPA policies with metadata
   ```json
   {"id": "deny-privileged-pods", "kind": ["Pod"], "tags": ["cis:1.1.0"], ...}
   {"id": "require-resource-limits", "kind": ["Deployment"], ...}
   {"id": "deny-default-namespace", "kind": ["Pod", "Deployment"], ...}
   ...
   ```

3. ⏳ Feature extractor
   ```python
   # kube-pac-copilot/src/features/extract.py
   def extract_k8s_features(resource: Dict) -> Dict:
       return {
           "resource_kind": resource["kind"],
           "securityContext.privileged": ...,
           "securityContext.allowPrivilegeEscalation": ...,
           "image.tag": ...,
           "volume.hostPath": ...,
           ...
       }
   ```

4. ⏳ Heuristic ranker (before ML model)
   ```python
   # kube-pac-copilot/src/rank/heuristic.py
   def rank_policies(features: Dict, corpus: List[Dict]) -> List[Tuple[str, float]]:
       """Simple rule-based ranker as baseline"""
       scores = []
       for policy in corpus:
           score = match_features(features, policy["features"])
           scores.append((policy["id"], score))
       return sorted(scores, key=lambda x: x[1], reverse=True)[:5]
   ```

5. ⏳ Conftest runner + SARIF output
   ```bash
   conftest test --policy kube-pac-copilot/policies/conftest/ \
                 --output sarif \
                 infrastructure/k8s/**/*.yaml > report.sarif
   ```

6. ⏳ GitHub Actions workflow
   ```yaml
   # .github/workflows/policy_scan.yml
   name: Policy Scan
   on: [pull_request]
   jobs:
     scan:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - run: python kube-pac-copilot/src/features/extract.py
         - run: conftest test --output sarif
         - uses: github/codeql-action/upload-sarif@v2
   ```

7. ⏳ Basic Grafana dashboard
   ```json
   // grafana/dashboards/policy_health.json
   {
     "panels": [
       {"title": "Policy Coverage %", "metric": "policy_coverage_rate"},
       {"title": "Violations Over Time", "metric": "violation_count"},
       {"title": "False Positive Rate", "metric": "fp_rate"}
     ]
   }
   ```

**Deliverables**:
- [ ] 10-20 working OPA policies
- [ ] Feature extraction working
- [ ] Heuristic policy ranker (no ML yet)
- [ ] CI integration with SARIF
- [ ] Basic Grafana dashboard

**Status**: 🔄 0% complete

---

### Phase 2: Learning (Weeks 3-4) - ML Models

**Goal**: Add ML-based policy ranking and troubleshooting

**Tasks**:

1. ⏳ Build Policy Ranker Model v1
   ```python
   # kube-pac-copilot/src/rank/model.py
   from sklearn.linear_model import LogisticRegression
   from sklearn.model_selection import train_test_split

   # Load training data
   X_train, y_train = load_policy_applicability_dataset()

   # Train
   ranker = LogisticRegression(multi_class='multilabel')
   ranker.fit(X_train, y_train)

   # Evaluate
   hit_at_5 = evaluate_hit_at_k(ranker, X_test, y_test, k=5)
   print(f"Hit@5: {hit_at_5}")  # Target: >= 0.85

   # Save to MLflow
   mlflow.sklearn.log_model(ranker, "policy_ranker_v1")
   mlflow.log_metric("hit_at_5", hit_at_5)
   ```

2. ⏳ RAG-grounded policy drafter
   ```python
   # kube-pac-copilot/src/policy_gen/drafter.py
   from GP_RAG.jade_rag_langgraph import JadeRAGAgent

   def draft_policy(resource: Dict, top_policies: List[str]) -> Dict:
       """Use RAG + LLM to draft adapted policy"""

       # Retrieve similar policies
       agent = JadeRAGAgent()
       context = agent.query(f"Show me examples of {top_policies[0]}")

       # Prompt LLM with grounding
       prompt = f"""
       Given these working policies:
       {context['response']}

       Adapt them for this resource:
       {json.dumps(resource, indent=2)}

       Generate:
       1. Rego constraint code
       2. Unit tests (positive + negative cases)
       3. Rationale
       """

       draft = llm.generate(prompt)
       return parse_draft(draft)
   ```

3. ⏳ Troubleshooter components
   ```python
   # kube-pac-copilot/src/troubleshoot/classifiers.py
   def classify_failure(logs: str) -> str:
       """Classify failure type"""
       if "parse error" in logs:
           return "parse"
       elif "timeout" in logs or "deadline exceeded" in logs:
           return "perf"
       elif "undefined" in logs or "incorrect result" in logs:
           return "logic"
       else:
           return "real"

   # kube-pac-copilot/src/troubleshoot/counterexample.py
   def generate_counterexample(policy: str, logs: str) -> Dict:
       """Generate minimal failing input"""
       # Use `opa eval --trace` to find counterexample
       result = subprocess.run([
           "opa", "eval", "--trace", "--input", "...", policy
       ], capture_output=True)
       return parse_trace_for_counterexample(result.stdout)
   ```

4. ⏳ Fix Strategy Classifier v0
   ```python
   # kube-pac-copilot/src/troubleshoot/fix_recommender.py
   from sklearn.ensemble import RandomForestClassifier

   # Load training data from failure_log.jsonl
   X, y = load_failure_history()
   # X = [severity, revert_count, FP_score, reliability]
   # y = ["manifest_patch" or "policy_change"]

   classifier = RandomForestClassifier()
   classifier.fit(X, y)

   # Predict fix strategy
   strategy = classifier.predict([[severity, revert_count, fp_score, reliability]])
   ```

5. ⏳ MLflow integration
   ```bash
   # Start MLflow server
   mlflow server --backend-store-uri sqlite:///mlflow.db \
                 --default-artifact-root ./mlflow-artifacts

   # Track experiments
   mlflow.set_experiment("ranker_experiments")
   with mlflow.start_run():
       mlflow.log_param("model_type", "LogisticRegression")
       mlflow.log_metric("hit_at_5", 0.87)
       mlflow.sklearn.log_model(ranker, "policy_ranker_v1")
   ```

**Deliverables**:
- [ ] Policy Ranker ML model (hit@5 >= 0.85)
- [ ] RAG-grounded policy drafter
- [ ] Troubleshooter (failure classification + counterexamples)
- [ ] Fix Strategy Classifier v0
- [ ] MLflow tracking operational

**Status**: 🔄 0% complete

---

### Phase 3: Production (Weeks 5-6) - Monitoring & Polish

**Goal**: Add drift monitoring, latency prediction, production readiness

**Tasks**:

1. ⏳ Nightly drift job
   ```python
   # kube-pac-copilot/src/drift/monitor.py
   from evidently import ColumnMapping
   from evidently.report import Report
   from evidently.metrics import DataDriftTable, DatasetDriftMetric

   def detect_drift():
       # Load baseline (Week 1 snapshot)
       baseline = load_resource_snapshot("2025-10-01")

       # Load current snapshot
       current = load_resource_snapshot("today")

       # Compare distributions
       report = Report(metrics=[DataDriftTable(), DatasetDriftMetric()])
       report.run(reference_data=baseline, current_data=current)

       # Save report
       report.save_html("drift_report.html")

       # Push metrics to Prometheus
       if report.drift_detected:
           prometheus.push_metric("drift_alert", 1)
   ```

2. ⏳ Latency regressor
   ```python
   # kube-pac-copilot/src/troubleshoot/latency.py
   from sklearn.linear_model import LinearRegression

   def predict_webhook_latency(rego_code: str) -> float:
       """Predict milliseconds for webhook execution"""

       # Extract features
       ast = parse_rego(rego_code)
       features = {
           "ast_size": len(ast.nodes),
           "comprehension_depth": max_depth(ast),
           "array_scan_ops": count_ops(ast, "array_scan")
       }

       # Predict
       latency_ms = latency_regressor.predict([features.values()])
       return latency_ms[0]
   ```

3. ⏳ RBAC/NetPol specific rules
   ```rego
   # policies/gatekeeper/rbac-least-privilege.rego
   package kubernetes.admission

   deny[msg] {
       input.kind == "Role"
       input.rules[_].verbs[_] == "*"
       msg = "RBAC wildcard verbs not allowed (least privilege)"
   }

   # policies/gatekeeper/network-policy-required.rego
   deny[msg] {
       input.kind == "Deployment"
       not has_network_policy(input.metadata.name)
       msg = "Deployment must have matching NetworkPolicy"
   }
   ```

4. ⏳ Documentation
   ```markdown
   # docs/playbooks/policy-failure-runbook.md
   ## Symptom: Policy test failing in CI

   ### Step 1: Classify failure type
   curl -X POST /troubleshoot -d '{"policy_id": "...", "logs": "..."}'

   ### Step 2: Review counterexample
   # API returns minimal failing input

   ### Step 3: Decide fix strategy
   # Use Fix Classifier recommendation

   ### Step 4: Apply fix
   # If manifest_patch: Update YAML
   # If policy_change: Refine Rego

   ### Step 5: Log outcome
   echo '{"accepted": true, ...}' >> failure_log.jsonl
   ```

**Deliverables**:
- [ ] Nightly drift job with Evidently
- [ ] Latency regressor (webhook timeout prediction)
- [ ] RBAC + NetworkPolicy rules
- [ ] Complete documentation (playbooks, runbooks, API spec)

**Status**: 🔄 0% complete

---

### Phase 4+: Advanced Features (Future)

**Future Enhancements**:

1. ⏳ Kyverno parity mode
   - Support Kyverno policies alongside OPA
   - Translate between Rego and Kyverno YAML

2. ⏳ RBAC least-privilege recommender
   - Analyze actual API calls
   - Recommend minimal permissions
   - Generate Role/RoleBinding

3. ⏳ Graph reasoning for reachability
   - Use knowledge graph for policy dependencies
   - Detect conflicting policies
   - Recommend policy composition

4. ⏳ IDE plugin (VSCode)
   - Inline policy suggestions
   - Real-time Rego linting
   - Chat interface for policy questions

**Status**: 🔮 Future backlog

---

## Key Differences: Current vs Target State

| Feature | Current (Today) | Target (MLOps Complete) |
|---------|----------------|-------------------------|
| **Policy Recommendation** | Manual selection | ML-ranked top-5 (hit@5 >= 0.85) |
| **Confidence Scoring** | Simple RAG distance | Multi-factor (ranker + reliability + FP + latency) |
| **Learning from Failures** | None | Fix Classifier learns from acceptance/revert history |
| **Fix Strategy** | Human decides | ML classifier recommends manifest vs policy change |
| **Performance Prediction** | None | Latency regressor warns before timeout |
| **Drift Detection** | None | Evidently monitors resource/violation distribution |
| **Policy Generation** | Manual Rego writing | RAG-grounded LLM drafts + tests |
| **Troubleshooting** | Manual debugging | Automated failure classification + counterexamples |
| **Model Tracking** | None | MLflow registry with experiments/metrics |
| **CI Integration** | Manual | GitHub Actions with SARIF + PR comments |

---

## Training Data Requirements 📊

### For Policy Ranker:

**Dataset**: `policies/index.jsonl`

**Format**:
```json
{
  "id": "deny-privileged-pods",
  "kind": ["Pod", "Deployment"],
  "tags": ["cis:1.1.0", "mitre:T1611"],
  "features": ["securityContext.privileged=true"],
  "example_inputs": [
    {"kind": "Pod", "spec": {"containers": [{"securityContext": {"privileged": true}}]}}
  ],
  "reliability": "high",
  "historical_success_rate": 0.95
}
```

**Minimum**: 50-100 policies with labeled applicability

**Current Status**: 🔄 Need to create policy corpus

---

### For Fix Strategy Classifier:

**Dataset**: `data/failures/failure_log.jsonl`

**Format**:
```json
{
  "ts": "2025-10-16T10:30:00Z",
  "policy_id": "deny-privileged-pods",
  "failure_type": "logic",
  "severity": "HIGH",
  "developer_revert_history": 0,
  "FP_score": 0.02,
  "policy_reliability": "high",
  "suggested_patch": "...",
  "accepted": true,           ← LABEL
  "fix_strategy": "manifest_patch"  ← LABEL
}
```

**Minimum**: 200-500 labeled failure events

**Current Status**: 🔄 Need to start collecting (bootstrap by manual labeling)

---

### For Latency Regressor:

**Dataset**: Webhook latency logs

**Format**:
```json
{
  "policy_id": "deny-privileged-pods",
  "rego_ast_size": 1200,
  "comprehension_depth": 2,
  "array_scan_ops": 8,
  "actual_latency_ms": 45.3  ← TARGET
}
```

**Minimum**: 100-200 webhook executions with timing data

**Current Status**: 🔄 Need to instrument webhooks for latency tracking

---

## Success Metrics Targets 🎯

### Model Performance:

```json
{
  "policy_ranker": {
    "hit_at_5": ">=0.85",              // Top-5 includes correct policy
    "precision_at_k": ">=0.80",
    "inference_ms": "<=100"
  },
  "fix_classifier": {
    "accuracy": ">=0.80",
    "precision": ">=0.75",             // Low false positives
    "recall": ">=0.80"                 // Catch most cases
  },
  "latency_regressor": {
    "mae": "<=50ms",                   // Mean absolute error
    "r2_score": ">=0.70"               // Explains 70% variance
  },
  "policy_drafter": {
    "rego_test_pass_rate": ">=0.95",   // Generated tests pass
    "false_positive_rate": "<=0.05"    // Low FP on safe fixtures
  }
}
```

### System Performance:

```json
{
  "ci_job_latency_seconds_p95": "<=60",        // Fast feedback loop
  "time_to_first_fix_minutes": "<=10",         // Quick turnaround
  "drift_alert_precision": ">=0.80",           // Accurate alerts
  "policy_coverage_rate": ">=0.85",            // Most resources covered
  "violation_trend": "decreasing"              // Improving over time
}
```

---

## Integration with Existing GP-Copilot 🔗

### Data Flow:

```
┌─────────────────────────────────────────────────────────┐
│  GP-CONSULTING (Scanners)                               │
│  • Trivy, Bandit, Semgrep, Gitleaks, Checkov           │
│  • Findings → GP-DATA/active/scans/                    │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GP-RAG (Foundation)                                    │
│  • Vector search (ChromaDB) - 328+ docs                 │
│  • Knowledge graph - 1,658 findings                     │
│  • LangGraph reasoning                                  │
│  • Basic confidence scoring                             │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  MLOps Layer (NEW!)                                     │
│  • Policy Ranker - Top-5 recommendations                │
│  • Fix Classifier - Manifest vs policy decision         │
│  • Latency Regressor - Performance prediction           │
│  • Policy Drafter - RAG-grounded generation             │
│  • Troubleshooter - Failure analysis                    │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GP-CONSULTING (Fixers)                                 │
│  • Apply manifest patches                               │
│  • Update Rego policies                                 │
│  • Validate with OPA test                               │
│  • Deploy to Gatekeeper                                 │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start: What to Build First? 🚀

### Recommendation: Start with Policy Ranker

**Why?**
1. ✅ Immediate value - Better policy recommendations
2. ✅ Simple baseline - Heuristic ranker first, then ML
3. ✅ Clear metrics - hit@5 easy to measure
4. ✅ Foundational - Other models depend on policy corpus

**Steps**:

```bash
# 1. Create policy corpus structure
mkdir -p kube-pac-copilot/policies/gatekeeper/templates
mkdir -p kube-pac-copilot/policies/conftest/policy_packs
touch kube-pac-copilot/policies/index.jsonl

# 2. Port existing policies from GP-CONSULTING
# GP-CONSULTING/1-Security-Assessment/cd-scanners/opa/
# → kube-pac-copilot/policies/

# 3. Add metadata to each policy
echo '{"id": "deny-privileged-pods", "kind": ["Pod"], ...}' >> policies/index.jsonl

# 4. Build heuristic ranker (baseline)
python kube-pac-copilot/src/rank/heuristic.py

# 5. Test on FINANCE-project
python -m pytest tests/test_ranker.py

# 6. Collect training data for ML model
# (Bootstrap: manual labeling of policy applicability)

# 7. Train Policy Ranker v1
python kube-pac-copilot/src/rank/train.py

# 8. Compare heuristic vs ML
python kube-pac-copilot/src/rank/evaluate.py
```

**Expected Timeline**: 1-2 weeks

---

## Summary ✨

### What You Have Built (Excellent Foundation!):

✅ **RAG System** - Vector search with ChromaDB (328+ docs)
✅ **Knowledge Graph** - 1,658 real findings with relationships
✅ **LangGraph Workflow** - Multi-step reasoning with Qwen2.5-7B
✅ **Basic Confidence** - Simple scoring based on retrieval
✅ **Dynamic Learning** - File watcher for instant knowledge updates
✅ **Clean Architecture** - 5 pillars (Backend, Consulting, Data, Frontend, Projects)

### What's Missing (Blueprint Complete, Ready to Build):

🔄 **Policy Ranker** - ML-based task ranking (THE KEY!)
🔄 **Fix Classifier** - Learn from troubleshooting history
🔄 **Latency Regressor** - Prevent webhook timeouts
🔄 **Policy Drafter** - RAG-grounded Rego generation
🔄 **Troubleshooter** - Automated failure analysis
🔄 **MLflow Registry** - Model versioning and tracking
🔄 **Drift Monitor** - Environment change detection
🔄 **FastAPI Service** - REST API for all features

### Your Vision: **ACHIEVABLE!**

All 4 ML models designed:
1. ✅ Policy Ranker (task ranker you mentioned!)
2. ✅ Fix Strategy Classifier (learns from troubleshooting!)
3. ✅ Latency Regressor (prevents failures!)
4. ✅ Prompted Policy Drafter (generates better quality OPA!)

**Result**: Jade gets smarter over time, confidence improves, quality increases! 🚀

---

**Next Action**: Review this document, decide which model to build first, then start implementation!

---

Last updated: 2025-10-16
