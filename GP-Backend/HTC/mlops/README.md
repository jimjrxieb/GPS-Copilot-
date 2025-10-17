# GP-RAG MLOps - Machine Learning Operations

**Vision**: Learning models for Jade that predict better quality OPA policies and learn from troubleshooting to improve confidence.

---

## 📁 Directory Structure

```
mlops/
├── 1-data/                     ← Training datasets
│   ├── policies/               ← Policy corpus (50-100 policies)
│   │   ├── index.jsonl         ← Policy metadata
│   │   ├── gatekeeper/         ← OPA Gatekeeper policies
│   │   └── conftest/           ← Conftest policy packs
│   ├── fixtures/               ← Test cases
│   │   ├── positive/           ← Known good K8s manifests
│   │   └── negative/           ← Known bad K8s manifests
│   └── failures/               ← Learning data
│       └── failure_log.jsonl   ← Troubleshooting history
│
├── 2-features/                 ← Feature engineering
│   ├── extract.py              ← K8s resource feature extraction
│   └── schemas.py              ← Data schemas (Pydantic)
│
├── 3-models/                   ← Machine learning models
│   ├── policy_ranker/          ← Task ranker (start here!)
│   │   ├── heuristic.py        ← Rule-based baseline
│   │   ├── train.py            ← ML training
│   │   ├── model.py            ← Model class
│   │   └── evaluate.py         ← Metrics (hit@5, precision)
│   ├── fix_classifier/         ← Manifest vs policy decision
│   │   ├── train.py
│   │   ├── model.py
│   │   └── evaluate.py
│   ├── latency_regressor/      ← Webhook timeout prediction
│   │   ├── train.py
│   │   ├── model.py
│   │   └── evaluate.py
│   └── policy_drafter/         ← RAG-grounded generation
│       ├── drafter.py          ← LLM + RAG
│       ├── test_runner.py      ← OPA test execution
│       └── guardrails.py       ← Validation & safety
│
├── 4-troubleshooting/          ← Failure analysis
│   ├── classifiers.py          ← Failure type detection
│   ├── counterexample.py       ← Minimal failing case
│   ├── fix_recommender.py      ← Suggest fixes
│   └── rego_linter.py          ← Static analysis
│
├── 5-monitoring/               ← Observability
│   ├── drift_detector.py       ← Evidently drift reports
│   └── metrics.py              ← Prometheus metrics
│
├── 6-api/                      ← REST API (FastAPI)
│   ├── app.py                  ← Main application
│   ├── routes/
│   │   ├── analyze.py          ← POST /analyze
│   │   ├── propose.py          ← POST /propose
│   │   ├── autofix.py          ← POST /autofix
│   │   ├── troubleshoot.py     ← POST /troubleshoot
│   │   └── drift.py            ← GET /drift
│   └── schemas.py              ← Pydantic models
│
└── 7-mlflow/                   ← Experiment tracking
    ├── experiments/            ← MLflow runs
    └── artifacts/              ← Saved models
```

---

## 🎯 The 4 Machine Learning Models

### 1. Policy Ranker (Task Ranker) - START HERE!

**Purpose**: Ranks top-5 most applicable policies for a Kubernetes resource

**Location**: `3-models/policy_ranker/`

**Type**: Multi-label classification (LogisticRegression or GradientBoosting)

**Input Features**:
```python
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

**Output**:
```python
[
  ("deny-privileged-pods", 0.92),      # High confidence
  ("require-resource-limits", 0.78),
  ("deny-latest-tag", 0.71),
  ("require-network-policy", 0.65),
  ("deny-hostpath-volumes", 0.58)
]
```

**Success Metric**: hit@5 >= 0.85 (correct policy in top-5, 85% of time)

**Build Order**:
1. `heuristic.py` - Rule-based baseline (no ML)
2. `train.py` - Train LogisticRegression model
3. `evaluate.py` - Measure hit@k, precision
4. `model.py` - Production class

---

### 2. Fix Strategy Classifier

**Purpose**: Decides whether to patch manifest or change policy when something fails

**Location**: `3-models/fix_classifier/`

**Type**: Binary classification (manifest_patch vs policy_change)

**Input Features**:
```python
{
  "severity": "HIGH",
  "developer_revert_history": 3,     # How many times reverted
  "FP_score": 0.02,                  # False positive likelihood
  "policy_reliability": "medium"      # Historical success rate
}
```

**Output**: "manifest_patch" or "policy_change"

**Learning Signal**: Developer acceptance/rejection from `failure_log.jsonl`

**Build Order**:
1. Collect failure logs (bootstrap with manual labeling)
2. `train.py` - Train RandomForest
3. `evaluate.py` - Precision/recall
4. `model.py` - Production class

---

### 3. Latency Regressor

**Purpose**: Predicts webhook execution time (prevents timeouts)

**Location**: `3-models/latency_regressor/`

**Type**: Regression (Linear or tree-based)

**Input Features**:
```python
{
  "rego_ast_size": 1500,           # Lines of code
  "comprehension_depth": 3,        # Nested loop depth
  "array_scan_ops": 12             # Array iterations
}
```

**Output**: Estimated milliseconds (e.g., 45.3ms)

**Use Case**: Warn if policy will timeout (>500ms)

**Build Order**:
1. Instrument webhooks for timing data
2. `train.py` - Train linear regression
3. `evaluate.py` - MAE, R² score
4. `model.py` - Production class

---

### 4. Policy Drafter (RAG + LLM)

**Purpose**: Generates Rego policies + tests from examples

**Location**: `3-models/policy_drafter/`

**Type**: LLM (Qwen2.5-7B) + RAG (already working!)

**Input**:
- Kubernetes resource (Pod, Deployment, etc.)
- Top-5 similar policies (from Policy Ranker + RAG)

**Output**:
```python
{
  "rego_package": "kubernetes.admission",
  "rego_code": "deny[msg] { ... }",
  "tests": [
    {"name": "test_deny_privileged", "input": {...}, "expected": "deny"}
  ],
  "rationale": "This policy prevents privilege escalation..."
}
```

**Guardrails**:
1. Schema validation (must be valid Rego)
2. Test pass rate >= 95%
3. False positive rate <= 5%
4. Human approval required

**Build Order**:
1. `drafter.py` - RAG retrieval + LLM prompt
2. `test_runner.py` - Execute `opa test`
3. `guardrails.py` - Validation checks

---

## 🚀 Getting Started (Step-by-Step)

### Week 1-2: Data Preparation

**Goal**: Create policy corpus with metadata

```bash
# 1. Create policy index
touch mlops/1-data/policies/index.jsonl

# 2. Port policies from GP-CONSULTING
cp /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/1-Security-Assessment/cd-scanners/opa/*.rego \
   mlops/1-data/policies/gatekeeper/

# 3. Add metadata for each policy
cat >> mlops/1-data/policies/index.jsonl << 'EOF'
{"id":"deny-privileged-pods","kind":["Pod","Deployment"],"tags":["cis:1.1.0"],"features":["securityContext.privileged=true"],"reliability":"high"}
{"id":"require-resource-limits","kind":["Pod","Deployment"],"tags":["cis:2.1.0"],"features":["resources.limits.missing"],"reliability":"high"}
{"id":"deny-latest-tag","kind":["Pod","Deployment"],"tags":["best-practice"],"features":["image.tag=latest"],"reliability":"medium"}
EOF

# 4. Create test fixtures
mkdir -p mlops/1-data/fixtures/{positive,negative}

# Positive example (should pass all policies)
cat > mlops/1-data/fixtures/positive/secure-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
      - name: app
        image: myapp:v1.2.3
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
        securityContext:
          allowPrivilegeEscalation: false
          privileged: false
EOF

# Negative example (should fail policies)
cat > mlops/1-data/fixtures/negative/insecure-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insecure-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest        # ❌ latest tag
        securityContext:
          privileged: true         # ❌ privileged
EOF
```

---

### Week 3-4: First Model - Policy Ranker

**Goal**: Build heuristic baseline, then ML model

```bash
# 1. Feature extractor
cat > mlops/2-features/extract.py << 'EOF'
#!/usr/bin/env python3
"""
Feature extraction from Kubernetes resources
"""
from typing import Dict, Any

def extract_features(resource: Dict[str, Any]) -> Dict[str, Any]:
    """Extract features for ML model"""
    features = {
        "resource_kind": resource.get("kind", "Unknown"),
        "namespace": resource.get("metadata", {}).get("namespace", "default"),
    }

    # Security context features
    spec = resource.get("spec", {})
    if "template" in spec:  # Deployment/StatefulSet
        containers = spec["template"]["spec"].get("containers", [])
    else:  # Pod
        containers = spec.get("containers", [])

    for container in containers:
        sec_ctx = container.get("securityContext", {})
        features["securityContext.privileged"] = sec_ctx.get("privileged", False)
        features["securityContext.allowPrivilegeEscalation"] = sec_ctx.get("allowPrivilegeEscalation", True)

        # Image features
        image = container.get("image", "")
        features["image.tag"] = "latest" if ":latest" in image or ":" not in image else "versioned"

    return features

if __name__ == "__main__":
    # Test
    test_resource = {
        "kind": "Deployment",
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "image": "nginx:latest",
                        "securityContext": {"privileged": True}
                    }]
                }
            }
        }
    }

    features = extract_features(test_resource)
    print(features)
EOF

chmod +x mlops/2-features/extract.py

# 2. Heuristic ranker (baseline)
cat > mlops/3-models/policy_ranker/heuristic.py << 'EOF'
#!/usr/bin/env python3
"""
Heuristic policy ranker (rule-based baseline)
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple

def load_policies() -> List[Dict]:
    """Load policy corpus"""
    policies_file = Path(__file__).parent.parent.parent / "1-data/policies/index.jsonl"
    if not policies_file.exists():
        return []
    return [json.loads(line) for line in policies_file.read_text().splitlines()]

def rank_policies_heuristic(features: Dict, top_n: int = 5) -> List[Tuple[str, float]]:
    """
    Rule-based policy ranking (no ML)

    Scoring rules:
    - Kind match: +1.0
    - Feature match: +0.5 per feature
    - Reliability: high=+0.3, medium=+0.1
    """
    policies = load_policies()
    scores = []

    for policy in policies:
        score = 0.0

        # Kind match
        if features.get("resource_kind") in policy.get("kind", []):
            score += 1.0

        # Feature match
        for policy_feature in policy.get("features", []):
            # Simple substring match
            if policy_feature.split("=")[0] in str(features):
                score += 0.5

        # Reliability bonus
        if policy.get("reliability") == "high":
            score += 0.3
        elif policy.get("reliability") == "medium":
            score += 0.1

        scores.append((policy["id"], score))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]

if __name__ == "__main__":
    # Test
    test_features = {
        "resource_kind": "Deployment",
        "securityContext.privileged": True,
        "image.tag": "latest"
    }

    results = rank_policies_heuristic(test_features)
    print("Top-5 Policy Recommendations:")
    for policy_id, score in results:
        print(f"  {policy_id}: {score:.2f}")
EOF

chmod +x mlops/3-models/policy_ranker/heuristic.py

# 3. Run it!
python3 mlops/3-models/policy_ranker/heuristic.py
```

---

### Week 5-6: RAG-Grounded Drafter

**Goal**: Use existing RAG to generate policies

```bash
# Policy drafter with RAG
cat > mlops/3-models/policy_drafter/drafter.py << 'EOF'
#!/usr/bin/env python3
"""
RAG-grounded policy drafter
"""
import sys
from pathlib import Path

# Add GP-RAG to path
gp_rag_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(gp_rag_root))

from jade_rag_langgraph import JadeRAGAgent

def draft_policy(resource: dict, policy_ids: list) -> dict:
    """
    Generate Rego policy using RAG + LLM

    Args:
        resource: Kubernetes resource
        policy_ids: Top-5 policy IDs from ranker

    Returns:
        {
          "rego_code": "...",
          "tests": [...],
          "rationale": "..."
        }
    """
    # Use RAG to retrieve similar policies
    agent = JadeRAGAgent()
    query = f"Show me examples of {policy_ids[0]} policy with tests"
    context = agent.query(query)

    print(f"RAG Confidence: {context['confidence']:.2f}")
    print(f"Retrieved sources: {len(context['sources'])}")

    # TODO: Prompt LLM with context + resource
    # TODO: Parse generated Rego
    # TODO: Run tests
    # TODO: Validate

    return {
        "rego_code": "# Generated policy here",
        "tests": [],
        "rationale": context['response']
    }

if __name__ == "__main__":
    test_resource = {"kind": "Pod"}
    result = draft_policy(test_resource, ["deny-privileged-pods"])
    print(result)
EOF

chmod +x mlops/3-models/policy_drafter/drafter.py

# Run it!
python3 mlops/3-models/policy_drafter/drafter.py
```

---

## 📊 Success Metrics

### Model Performance Targets:

| Model | Metric | Target |
|-------|--------|--------|
| Policy Ranker | hit@5 | >= 0.85 |
| Policy Ranker | inference_ms | <= 100 |
| Fix Classifier | accuracy | >= 0.80 |
| Fix Classifier | precision | >= 0.75 |
| Latency Regressor | MAE | <= 50ms |
| Latency Regressor | R² | >= 0.70 |
| Policy Drafter | test_pass_rate | >= 0.95 |
| Policy Drafter | false_positive_rate | <= 0.05 |

### System Performance Targets:

- CI job latency (p95): <= 60 seconds
- Time to first fix: <= 10 minutes
- Policy coverage rate: >= 85%
- Drift alert precision: >= 80%

---

## 🔗 Integration with GP-Copilot

### Data Sources:

```
GP-CONSULTING/1-Security-Assessment/
├── ci-scanners/          → Findings feed knowledge graph
├── cd-scanners/          → Policies feed policy corpus
└── runtime-monitors/     → Metrics feed drift detector

GP-DATA/
├── active/scans/         → Training data (violations)
├── active/fixes/         → Training data (acceptance/rejection)
└── knowledge-base/       → Vector DB (RAG)
```

### Model Consumers:

```
GP-CONSULTING/2-App-Fixes/
├── fixers/               → Use Fix Classifier decisions
└── validators/           → Use Policy Ranker recommendations

GP-CONSULTING/6-Auto-Agents/
└── *_agent.py            → Use all models for decisions
```

---

## 📚 Documentation

- **[../README_MLOPS.md](../README_MLOPS.md)** - Quick reference
- **[../MLOPS_LEARNING_ARCHITECTURE.md](../MLOPS_LEARNING_ARCHITECTURE.md)** - Deep dive
- **[../MLOPS_IMPLEMENTATION_STATUS.md](../MLOPS_IMPLEMENTATION_STATUS.md)** - What exists vs planned
- **[../LEARNING_GUIDE.md](../LEARNING_GUIDE.md)** - AWS AI Practitioner exam alignment
- **[mlops2.json](mlops2.json)** - Complete technical specification

---

## 🎯 Next Steps

1. ✅ Directory structure created
2. ⏳ Port 10-20 policies from GP-CONSULTING
3. ⏳ Add metadata to `1-data/policies/index.jsonl`
4. ⏳ Build feature extractor (`2-features/extract.py`)
5. ⏳ Build heuristic ranker (`3-models/policy_ranker/heuristic.py`)
6. ⏳ Evaluate baseline (hit@5?)
7. ⏳ Train ML model (`3-models/policy_ranker/train.py`)
8. ⏳ Set up MLflow tracking

**Start with**: Policy Ranker (the task ranker you mentioned!)

---

Last updated: 2025-10-16
