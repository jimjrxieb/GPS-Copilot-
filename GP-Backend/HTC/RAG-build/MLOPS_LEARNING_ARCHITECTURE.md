# MLOps Learning Architecture - Jade's Intelligence Evolution

**Purpose**: Machine learning models that help Jade learn from troubleshooting experiences to generate better quality OPA policies and Kubernetes manifests over time.

**Your Vision**: "Kube and policy as code predictors learning and create better and higher quality opa and manifests. Learn from troubleshooting so jade can have better confidence. I believe there is a task ranker in there as well."

---

## Overview 🧠

This is **NOT** just automation - this is a **learning system** that gets smarter over time.

### The Core Problem It Solves:

1. **Static policies lag behind reality** - Kubernetes environments change faster than humans can write policies
2. **Jade needs to learn from failures** - Every troubleshooting session should make Jade smarter
3. **Confidence must improve** - Jade should know when it's right vs. guessing
4. **Quality prediction** - Predict which policies will work before deploying them

---

## 4 Machine Learning Models 🤖

### 1. **Policy Ranker** (The Task Ranker You Mentioned!)

**What it does**: Ranks which policies are most applicable to a given Kubernetes resource

**Type**: Logistic Regression or Gradient Boosting (start simple)

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
- Top-5 most applicable policies (hit@5 >= 0.85 accuracy)
- Confidence scores for each policy

**How it learns**:
- Tracks which policies actually fixed issues
- Multi-label classification (one resource needs multiple policies)
- Deterministic with fixed seed for reproducibility

**Success Metrics**:
```json
{
  "policy_recommendation_hit_at_5": ">= 0.85",
  "precision@k": "measured",
  "inference_ms": "fast enough for CI"
}
```

---

### 2. **Fix Strategy Classifier**

**What it does**: Decides whether to patch the manifest or change the policy when something fails

**Type**: Binary classifier

**Inputs**:
```json
{
  "severity": "HIGH",
  "developer_revert_history": 3,
  "FP_score": 0.02,
  "policy_reliability": "medium"
}
```

**Outputs**:
- `manifest_patch` - Fix the YAML
- `policy_change` - Policy is wrong, fix the Rego

**How it learns from troubleshooting**:
- Tracks when developers revert Jade's suggestions
- High revert history = policy might be wrong
- Low FP score + high reliability = trust the policy, patch manifest
- High FP score = policy needs refinement

**This is KEY to confidence improvement!**

---

### 3. **Latency Regressor**

**What it does**: Predicts if a policy will be too slow in production (webhook timeout risk)

**Type**: Linear regression or small tree model

**Inputs**:
```json
{
  "rego_ast_size": 1500,
  "comprehension_depth": 3,
  "array_scan_ops": 12
}
```

**Outputs**:
- Estimated milliseconds for webhook execution
- Risk warning if > p95 threshold

**How it prevents failures**:
- Analyzes Rego complexity BEFORE deploying
- Warns about policies that will timeout webhooks
- Learns from actual webhook latency data

**Success Metric**:
```json
{
  "webhook_latency_ms_estimate_p95": "<= acceptable threshold"
}
```

---

### 4. **Prompted Policy Drafter** (RAG-Grounded LLM)

**What it does**: Uses LLM + RAG to draft or adapt Rego policies with tests

**Type**: Qwen2.5-7B-Instruct + Grounded RAG (already in GP-RAG!)

**Grounding Sources**:
- `policies/index.jsonl` - Curated policy corpus
- Exemplar Rego code from successful policies
- Unit tests from working constraints

**Guardrails** (Prevents hallucination):
```python
1. Schema validation - Must match OPA structure
2. Unit tests - Must pass `opa test`
3. FP budget - Must stay under 5% false positive rate
4. Restricted to retrieved exemplars - NO free-text policy invention
```

**How it learns**:
- RAG retrieves similar working policies
- LLM adapts them to new context
- Grounding prevents making up dangerous policies
- Test loop validates before suggesting

**Success Metric**:
```json
{
  "rego_test_pass_rate": ">= 0.95",
  "false_positive_rate": "<= 0.05"
}
```

---

## The Learning Feedback Loop 🔄

### How Jade Gets Smarter Over Time:

```
┌─────────────────────────────────────────────────────────┐
│  1. Jade Proposes Policy or Fix                         │
│     (Using Policy Ranker + Fix Classifier)              │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  2. Test in CI                                          │
│     • opa test (unit tests)                             │
│     • conftest (integration)                            │
│     • SARIF report                                      │
└─────────────────┬───────────────────────────────────────┘
                  ↓
         ┌────────┴────────┐
         │                 │
     SUCCESS            FAILURE
         │                 │
         ↓                 ↓
┌─────────────────┐  ┌─────────────────────────────────┐
│ 3a. Log Success │  │ 3b. Troubleshoot & Learn       │
│ • Policy works  │  │ • Classify failure type         │
│ • Increase conf │  │ • Generate counterexample       │
│ • Track metrics │  │ • Log to failure_log.jsonl      │
└─────────────────┘  └─────────────────┬───────────────┘
                                       ↓
                     ┌─────────────────────────────────────┐
                     │ 4. Human Accepts or Reverts?        │
                     │ • Accepted = Good learning signal   │
                     │ • Reverted = Update Fix Classifier  │
                     └─────────────────┬───────────────────┘
                                       ↓
                     ┌─────────────────────────────────────┐
                     │ 5. Retrain Models                   │
                     │ • Policy Ranker learns patterns     │
                     │ • Fix Classifier learns mistakes    │
                     │ • Latency Regressor learns perf     │
                     └─────────────────────────────────────┘
```

---

## Troubleshooting Intelligence 🔧

### The `/troubleshoot` API Endpoint:

**Request**:
```json
{
  "policy_id": "deny-privileged-pods",
  "rego_code": "package kubernetes.admission...",
  "inputs": [{"kind": "Pod", "spec": {...}}],
  "logs": "Error: evaluation_error..."
}
```

**Response**:
```json
{
  "failure_type": "logic",
  "culprit_lines": [42, 43],
  "counterexample": {
    "kind": "Pod",
    "spec": {"containers": [{"securityContext": {"privileged": true}}]}
  },
  "suggested_patch": "Change line 42 to: allow { not input.spec.containers[_].securityContext.privileged }"
}
```

### Failure Classification:

1. **Parse errors** - Syntax mistakes in Rego
2. **Logic errors** - Policy doesn't do what it should
3. **Performance** - Too slow (webhook timeout risk)
4. **Real violations** - Policy is correct, manifest is wrong

### How Jade Learns from Failures:

Every failure is logged to `data/failures/failure_log.jsonl`:

```json
{
  "ts": "2025-10-16T10:30:00Z",
  "policy_id": "deny-privileged-pods",
  "failure_type": "logic",
  "culprit_lines": [42],
  "counterexample": {...},
  "suggested_patch": "...",
  "accepted": true  // Human accepted the fix
}
```

**This dataset trains the models!**

---

## Confidence Scoring System 📊

### How Jade Knows Its Confidence:

```python
confidence_score = (
    policy_ranker_score * 0.4 +        # How well does policy match?
    reliability_score * 0.3 +          # Historical success rate
    fp_score * 0.2 +                   # False positive likelihood
    latency_risk_score * 0.1           # Will it timeout?
)
```

### Confidence Levels:

- **High (>0.85)**: "I'm confident this will work"
- **Medium (0.60-0.85)**: "This should work, but test carefully"
- **Low (<0.60)**: "I'm guessing, please review"

### As Jade learns from troubleshooting:
- Successful fixes → Increase reliability score
- Reverted fixes → Decrease confidence for similar patterns
- Performance issues → Update latency risk model
- False positives → Refine policy applicability

**Result**: Jade gets more confident over time for patterns it has seen!

---

## Drift Monitoring 📈

### The `/drift` Endpoint Tracks:

```json
{
  "coverage_rate": 0.87,  // % of resources covered by policies
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

### Evidently Drift Reports:

Tracks distribution shifts in:
1. **Resource mix** - Are new types of resources appearing?
2. **Feature distributions** - Are security contexts changing?
3. **Violation patterns** - Are new vulnerability types emerging?

**When drift detected**:
- Alert Security Engineer
- Trigger model retraining
- Update policy corpus
- Adjust confidence scores

---

## MLflow Integration 🔬

### Model Registry Structure:

```
mlflow/
├── ranker_experiments/
│   ├── policy_ranker_v1  ← LogisticRegression baseline
│   ├── policy_ranker_v2  ← GradientBoosting improved
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

### Tracked Artifacts:

1. **Models** - Serialized sklearn/torch models
2. **Confusion matrices** - Classification performance
3. **Drift reports** - Evidently HTML reports
4. **Policy exemplars** - RAG corpus snapshots
5. **Failure logs** - Training data backups

### Metrics Logged:

```python
mlflow.log_metric("hit_at_5", 0.87)
mlflow.log_metric("precision_at_k", 0.82)
mlflow.log_metric("false_positive_rate", 0.03)
mlflow.log_metric("ci_latency_p95", 45.2)
mlflow.log_metric("drift_alert_precision", 0.85)
```

---

## Training Pipeline 🏋️

### Datasets:

```
kube-pac-copilot/data/
├── fixtures/
│   ├── positive/          # Known good manifests
│   ├── negative/          # Known bad manifests
├── failures/
│   └── failure_log.jsonl  # Troubleshooting history
└── policies/
    └── index.jsonl        # Curated policy corpus
```

### Training Trigger Events:

1. **Weekly scheduled retraining** - Keep models fresh
2. **Drift threshold exceeded** - Immediate retrain
3. **New failure patterns** - Update after 50+ new failures
4. **Manual trigger** - After policy corpus update

### Evaluation Metrics:

```json
{
  "policy_recommendation_hit_at_5": ">= 0.85",
  "rego_test_pass_rate": ">= 0.95",
  "false_positive_rate": "<= 0.05",
  "ci_job_latency_seconds_p95": "<= 60",
  "time_to_first_fix_minutes": "<= 10",
  "drift_alert_precision": ">= 0.80"
}
```

---

## Integration with GP-Copilot 🔗

### How MLOps Connects to Existing Components:

```
┌─────────────────────────────────────────────────────────┐
│  GP-RAG (Vector Search + Knowledge Graph)               │
│  • 1,658 findings loaded                                │
│  • 328+ documents in ChromaDB                           │
│  • Qwen2.5-7B LLM                                       │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  MLOps Learning Layer (THIS!)                           │
│  • Policy Ranker - Predicts best policies               │
│  • Fix Classifier - Decides manifest vs policy change   │
│  • Latency Regressor - Prevents timeouts               │
│  • Troubleshooter - Learns from failures                │
└─────────────────┬───────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│  GP-CONSULTING (Execution)                              │
│  • Scanners generate findings                           │
│  • Fixers apply changes                                 │
│  • OPA validates policies                               │
│  • Gatekeeper enforces                                  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow Example:

1. **Scanner finds issue**: Privileged container in FINANCE-project
2. **GP-RAG retrieves context**: "Similar issue fixed in LinkOps-MLOps"
3. **Policy Ranker**: "deny-privileged-pods policy matches (confidence: 0.92)"
4. **Fix Classifier**: "Manifest patch recommended (not policy issue)"
5. **Latency Regressor**: "Policy safe for production (estimated 8ms)"
6. **Troubleshooter**: Generates test case, validates fix
7. **Jade applies fix**: Updates securityContext in manifest
8. **Result logged**: Success → Increase confidence for similar cases

---

## API Endpoints 🌐

### FastAPI Microservice:

```python
# Feature extraction
POST /analyze
{
  "repo_path": "/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project",
  "bundle_glob": "infrastructure/k8s/**/*.yaml",
  "kinds": ["Deployment", "Pod", "Role", "NetworkPolicy"]
}
→ Returns: violations, recommendations, SARIF report

# Policy ranking
POST /propose
{
  "resource_json": {"kind": "Deployment", "spec": {...}},
  "top_n": 5
}
→ Returns: Top 5 policies with confidence scores + Rego code

# Intelligent fixing
POST /autofix
{
  "violation": {...},
  "strategy": "auto|manifest|policy"
}
→ Returns: Manifest diff, policy diff, rationale

# Troubleshooting
POST /troubleshoot
{
  "policy_id": "deny-privileged-pods",
  "rego_code": "...",
  "inputs": [{...}],
  "logs": "Error: evaluation_error..."
}
→ Returns: Failure type, culprit lines, counterexample, suggested patch

# Drift monitoring
GET /drift
→ Returns: Coverage rate, violation trends, resource mix, alerts

# Health check
GET /health
→ Returns: Status, version
```

---

## Real-World Example: Learning from FINANCE-Project 💡

### Scenario: Jade Learns from Hardcoded Secret Fix

**Initial State** (Low Confidence):
```
Jade finds hardcoded API key in FINANCE-project deployment.yaml
Policy Ranker: "deny-hardcoded-secrets" (confidence: 0.55 - LOW)
Fix Classifier: "Unsure if manifest or policy issue"
Jade suggests: "Use Kubernetes Secret"
```

**Human Applies Fix**:
```yaml
# Before
env:
  - name: API_KEY
    value: "sk-1234567890abcdef"  # Hardcoded!

# After
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: api-credentials
        key: api-key
```

**Outcome**: Fix works! Test passes. Deployed successfully.

**Learning Update**:
```json
{
  "ts": "2025-10-16T14:30:00Z",
  "policy_id": "deny-hardcoded-secrets",
  "failure_type": "real",  // Policy was correct, manifest was wrong
  "accepted": true,
  "manifest_patch_successful": true
}
```

**Next Time** (Increased Confidence):
```
Jade finds similar pattern in another project
Policy Ranker: "deny-hardcoded-secrets" (confidence: 0.88 - HIGH!)
Fix Classifier: "Manifest patch" (learned from history)
Jade confidently suggests: "Use Kubernetes Secret (similar to FINANCE-project fix)"
```

**This is learning in action!**

---

## Roadmap 🗺️

### Phase 1 (Weeks 1-2) - MVP:
- ✅ Add policies corpus (10-20 constraints)
- ✅ Feature extractor + retrieval + heuristic ranker
- ✅ Conftest runner + SARIF + PR comment
- ✅ Baseline Grafana dashboard

### Phase 2 (Weeks 3-4) - Learning:
- 🔄 RAG-grounded policy drafter
- 🔄 Troubleshooter: linter, counterexample, fix recommender
- 🔄 Fix strategy classifier v0
- 🔄 MLflow integration

### Phase 3 (Weeks 5-6) - Production:
- ⏳ Nightly drift job + Evidently reports
- ⏳ Latency regressor + webhook warnings
- ⏳ RBAC/NetPol specific rules
- ⏳ Docs: playbooks, runbooks, API spec

### Phase 4+ - Advanced:
- 🔮 Kyverno parity
- 🔮 RBAC least-privilege recommender
- 🔮 Graph reasoning for reachability
- 🔮 IDE plugin (VSCode) + Chat UX

---

## Success Metrics 🎯

### Quantitative Goals:

```json
{
  "policy_recommendation_hit_at_5": "0.85+",     // Ranker accuracy
  "rego_test_pass_rate": "0.95+",                // Generated policies work
  "false_positive_rate": "0.05 or less",         // Low noise
  "ci_job_latency_seconds_p95": "60 or less",    // Fast feedback
  "time_to_first_fix_minutes": "10 or less",     // Quick turnaround
  "drift_alert_precision": "0.80+"               // Accurate drift detection
}
```

### Qualitative Goals:

- Jade suggests fixes **before** humans notice issues
- Confidence scores **match reality** (high confidence = usually right)
- Developers **trust Jade's suggestions** (low revert rate)
- Policies **don't break production** (no webhook timeouts)
- Security posture **improves over time** (violation trends down)

---

## Key Differences from Static Automation ⚡

| Static Automation | MLOps Learning System |
|-------------------|----------------------|
| Fixed rules | Learns from experience |
| Same confidence always | Confidence improves over time |
| Repeats same mistakes | Remembers failures |
| No context awareness | Uses RAG for context |
| Binary pass/fail | Probabilistic with confidence |
| No performance prediction | Predicts latency before deploy |
| Manual policy updates | Auto-adapts to drift |
| No troubleshooting help | Generates counterexamples |

---

## Summary ✨

**This is NOT just policy automation - this is a learning intelligence system!**

### What Makes This Special:

1. **4 ML Models Working Together**:
   - Policy Ranker → Picks best policies
   - Fix Classifier → Decides what to fix
   - Latency Regressor → Prevents timeouts
   - Policy Drafter → RAG-grounded generation

2. **Learning Feedback Loop**:
   - Every success increases confidence
   - Every failure teaches new patterns
   - Human feedback refines models
   - Drift detection triggers retraining

3. **Confidence Evolution**:
   - Starts uncertain (0.55 confidence)
   - Learns from troubleshooting
   - Gets confident (0.88+) for known patterns
   - Admits when it doesn't know

4. **Your Vision Realized**:
   ✅ "Learning models for Jade" - 4 ML models + LLM
   ✅ "Create better quality OPA" - Policy Ranker + Drafter
   ✅ "Learn from troubleshooting" - failure_log.jsonl training
   ✅ "Better confidence" - Confidence scoring system
   ✅ "Task ranker" - Policy Ranker model

---

**Next Steps**:

1. Review this architecture - does it match your vision?
2. Decide on implementation priority (which model first?)
3. Set up MLflow for experiment tracking
4. Start collecting failure logs for training data
5. Build Phase 1 MVP (feature extraction + basic ranker)

**Current Status**: Blueprint complete, ready for implementation!

---

Last updated: 2025-10-16
