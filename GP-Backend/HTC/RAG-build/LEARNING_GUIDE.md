# Learning Guide: Building MLOps While Studying AWS AI Practitioner

**Perfect Timing!** Building this MLOps system aligns perfectly with AWS AI Practitioner exam prep.

---

## 🎓 AWS AI Practitioner Exam Coverage

The exam covers 4 domains - and **this project touches all of them!**

### Domain 1: Fundamentals of AI and ML (20%)

**You'll Practice**:
- ✅ ML lifecycle (train, test, deploy, monitor)
- ✅ Supervised learning (Policy Ranker, Fix Classifier)
- ✅ Regression (Latency Regressor)
- ✅ Model evaluation metrics (accuracy, precision, recall, hit@k)
- ✅ Overfitting prevention (train/test splits, cross-validation)

**Exam Topics**:
- Types of ML (supervised, unsupervised, reinforcement)
- ML workflow phases
- Model training and evaluation concepts

**What You'll Build**: All 4 ML models → Hands-on exam prep!

---

### Domain 2: Fundamentals of Generative AI (24%)

**You'll Practice**:
- ✅ RAG (Retrieval Augmented Generation) - Already working!
- ✅ LLM prompting (Qwen2.5-7B for policy drafting)
- ✅ Grounding strategies (prevent hallucination)
- ✅ Vector databases (ChromaDB)
- ✅ Embeddings for semantic search

**Exam Topics**:
- Foundation models and transformers
- Prompt engineering techniques
- RAG architecture patterns
- Vector databases and embeddings

**What You Have**: Production RAG system with 328+ docs!

---

### Domain 3: Applications of Foundation Models (28%)

**You'll Practice**:
- ✅ Text generation (Rego policy drafting)
- ✅ Question answering (Jade chat)
- ✅ Code generation (Rego is code!)
- ✅ Evaluation metrics (BLEU, ROUGE for text quality)
- ✅ Responsible AI (guardrails, validation, no auto-merge)

**Exam Topics**:
- Using foundation models for tasks
- Model selection criteria
- Evaluation and testing strategies
- Responsible AI practices

**What You'll Build**: RAG-grounded policy drafter with guardrails!

---

### Domain 4: Guidelines for Responsible AI (28%)

**You'll Practice**:
- ✅ Human oversight (no auto-merge, approval required)
- ✅ Bias detection (false positive tracking)
- ✅ Explainability (confidence scores, reasoning chains)
- ✅ Monitoring and drift detection
- ✅ Model versioning (MLflow)
- ✅ Audit logging (failure_log.jsonl)

**Exam Topics**:
- Fairness and bias mitigation
- Transparency and explainability
- Security and privacy
- Governance and compliance

**What You'll Build**: Complete responsible AI system with controls!

---

## 📁 Recommended Project Structure (Easy to Navigate!)

### Option A: Keep Everything in GP-RAG (Recommended for Learning)

**Why?**
- ✅ All ML/AI in one place
- ✅ Easy to understand: "Everything AI is here"
- ✅ Simple imports: `from GP_RAG.mlops.policy_ranker import PolicyRanker`
- ✅ Clear separation from consulting agents

**Structure**:
```
GP-Backend/GP-RAG/
├── README.md                          ← User guide
├── README_MLOPS.md                    ← ML quick reference
├── MLOPS_LEARNING_ARCHITECTURE.md     ← Deep dive
├── MLOPS_IMPLEMENTATION_STATUS.md     ← Current status
├── LEARNING_GUIDE.md                  ← This file!
│
├── core/                              ← Foundation (WORKING)
│   ├── jade_engine.py                 ← RAG engine
│   └── knowledge_graph.py             ← Graph operations
│
├── mlops/                             ← ML Models (TO BUILD)
│   ├── README.md                      ← MLOps overview
│   ├── mlops.md                       ← Original spec
│   ├── mlops2.json                    ← Complete blueprint
│   │
│   ├── 1-data/                        ← Training datasets
│   │   ├── policies/
│   │   │   ├── index.jsonl            ← Policy corpus
│   │   │   ├── gatekeeper/            ← OPA policies
│   │   │   └── conftest/              ← Conftest packs
│   │   ├── fixtures/
│   │   │   ├── positive/              ← Good manifests
│   │   │   └── negative/              ← Bad manifests
│   │   └── failures/
│   │       └── failure_log.jsonl      ← Learning data
│   │
│   ├── 2-features/                    ← Feature engineering
│   │   ├── extract.py                 ← K8s feature extraction
│   │   └── schemas.py                 ← Data schemas
│   │
│   ├── 3-models/                      ← ML models
│   │   ├── policy_ranker/
│   │   │   ├── heuristic.py           ← Baseline (start here!)
│   │   │   ├── train.py               ← ML training
│   │   │   ├── model.py               ← Model class
│   │   │   └── evaluate.py            ← Evaluation
│   │   ├── fix_classifier/
│   │   │   ├── train.py
│   │   │   ├── model.py
│   │   │   └── evaluate.py
│   │   ├── latency_regressor/
│   │   │   ├── train.py
│   │   │   ├── model.py
│   │   │   └── evaluate.py
│   │   └── policy_drafter/
│   │       ├── drafter.py             ← RAG + LLM
│   │       ├── test_runner.py         ← OPA test
│   │       └── guardrails.py          ← Validation
│   │
│   ├── 4-troubleshooting/             ← Failure analysis
│   │   ├── classifiers.py             ← Failure type
│   │   ├── counterexample.py          ← Minimal failing case
│   │   ├── fix_recommender.py         ← Suggest fixes
│   │   └── rego_linter.py             ← Static analysis
│   │
│   ├── 5-monitoring/                  ← Observability
│   │   ├── drift_detector.py          ← Evidently
│   │   └── metrics.py                 ← Prometheus
│   │
│   ├── 6-api/                         ← REST API
│   │   ├── app.py                     ← FastAPI
│   │   ├── routes/
│   │   │   ├── analyze.py
│   │   │   ├── propose.py
│   │   │   ├── autofix.py
│   │   │   ├── troubleshoot.py
│   │   │   └── drift.py
│   │   └── schemas.py                 ← Pydantic models
│   │
│   └── 7-mlflow/                      ← Experiment tracking
│       ├── experiments/               ← MLflow runs
│       └── artifacts/                 ← Saved models
│
├── jade_rag_langgraph.py              ← LangGraph workflow (WORKING)
├── dynamic_learner.py                 ← File watcher (WORKING)
├── simple_learn.py                    ← Drop & learn (WORKING)
│
└── unprocessed/                       ← Drop files here (WORKING)
    ├── client-docs/
    ├── compliance/
    ├── policies/
    ├── scan-results/
    └── security-docs/
```

**Clear Learning Path**:
1. Start in `mlops/1-data/` → Understand datasets
2. Move to `mlops/2-features/` → Learn feature engineering
3. Build `mlops/3-models/policy_ranker/heuristic.py` → Baseline
4. Train `mlops/3-models/policy_ranker/train.py` → ML model
5. Add `mlops/4-troubleshooting/` → Learning loop
6. Set up `mlops/7-mlflow/` → Experiment tracking

---

### Option B: Separate Project (If you want production-ready structure)

**When to use**: If you plan to deploy this as a standalone service.

```
GP-Backend/
├── GP-RAG/                    ← Foundation (keep as-is)
└── kube-pac-copilot/          ← New standalone project
    ├── README.md
    ├── docker-compose.yml
    ├── .github/workflows/
    ├── policies/
    ├── data/
    ├── src/
    ├── grafana/
    └── mlflow/
```

**Pros**: Clean separation, easier to open-source later
**Cons**: More complex imports, split codebase

---

## 🎯 My Recommendation: Option A (GP-RAG/mlops/)

**Why?**

### 1. **Learning Focus**
You're studying for AWS AI Practitioner - you want to:
- See RAG in action (already working in GP-RAG)
- Understand ML lifecycle (train → test → deploy)
- Practice with real models (Policy Ranker, etc.)
- Learn vector databases (ChromaDB already configured)

Having everything in one place makes connections clear!

### 2. **AWS Exam Alignment**

```
GP-RAG/
├── core/jade_engine.py           ← Domain 2: RAG, embeddings
├── jade_rag_langgraph.py         ← Domain 2: LLM prompting
├── mlops/3-models/               ← Domain 1: Supervised learning
├── mlops/4-troubleshooting/      ← Domain 1: Model evaluation
├── mlops/5-monitoring/           ← Domain 3: Monitoring
└── mlops/6-api/                  ← Domain 3: Deployment
```

**Every directory maps to exam content!**

### 3. **Easy Navigation**

```bash
# All AI/ML work in one place
cd GP-Backend/GP-RAG/

# Start with basics
cat README.md                      # Overview
cat README_MLOPS.md                # Quick reference

# Deep dive
cat MLOPS_LEARNING_ARCHITECTURE.md # Theory
cat LEARNING_GUIDE.md              # This file

# Build step-by-step
cd mlops/1-data/                   # Prepare datasets
cd mlops/2-features/               # Feature engineering
cd mlops/3-models/policy_ranker/   # Start here!
```

### 4. **Reuses Existing Foundation**

```python
# In mlops/3-models/policy_ranker/model.py
from GP_RAG.core.jade_engine import rag_engine  # Already works!
from GP_RAG.jade_rag_langgraph import JadeRAGAgent  # Already works!

# Build on top of working components
def draft_policy_with_rag(resource: Dict) -> str:
    agent = JadeRAGAgent()
    similar_policies = agent.query(f"Show policies for {resource['kind']}")
    return draft_from_examples(similar_policies)
```

---

## 📚 Learning Path (Aligned with AWS Exam)

### Week 1-2: Fundamentals + Data Prep (Domain 1)

**AWS Topics**: ML basics, data preparation, feature engineering

**What to Build**:
```bash
# 1. Create data structure
mkdir -p GP-RAG/mlops/1-data/{policies,fixtures,failures}

# 2. Port policies from GP-CONSULTING
# Learn: What makes a good training dataset?

# 3. Add metadata (feature engineering!)
# Learn: How to extract features from K8s resources?

# 4. Build feature extractor
# File: GP-RAG/mlops/2-features/extract.py
```

**AWS Exam Practice**:
- What are features? (K8s properties: privileged, hostPath, etc.)
- How to handle categorical data? (one-hot encoding for resource kinds)
- Train/test split strategies
- Data quality checks

---

### Week 3-4: First ML Model - Policy Ranker (Domain 1)

**AWS Topics**: Supervised learning, classification, evaluation metrics

**What to Build**:
```bash
# 1. Heuristic baseline (no ML yet)
# File: GP-RAG/mlops/3-models/policy_ranker/heuristic.py
# Learn: Rule-based systems vs ML

# 2. Train first ML model
# File: GP-RAG/mlops/3-models/policy_ranker/train.py
# Learn: sklearn, LogisticRegression, model.fit()

# 3. Evaluate
# File: GP-RAG/mlops/3-models/policy_ranker/evaluate.py
# Learn: accuracy, precision, recall, hit@k
```

**AWS Exam Practice**:
- What is supervised learning?
- Multi-label classification
- Evaluation metrics (hit@5, precision@k)
- Overfitting vs underfitting
- Hyperparameter tuning

**Code Example**:
```python
# GP-RAG/mlops/3-models/policy_ranker/train.py
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# Load data (AWS exam: data preparation)
X, y = load_policy_dataset()

# Split (AWS exam: train/test split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train (AWS exam: model training)
model = LogisticRegression(multi_class='ovr', max_iter=1000)
model.fit(X_train, y_train)

# Evaluate (AWS exam: metrics)
from sklearn.metrics import accuracy_score, precision_score
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Accuracy: {accuracy:.2f}")  # Target: >= 0.85
```

---

### Week 5-6: RAG + LLM (Domain 2 & 3)

**AWS Topics**: Foundation models, RAG, prompt engineering, responsible AI

**What to Build**:
```bash
# 1. Policy drafter with RAG
# File: GP-RAG/mlops/3-models/policy_drafter/drafter.py
# Learn: How RAG prevents hallucination

# 2. Guardrails
# File: GP-RAG/mlops/3-models/policy_drafter/guardrails.py
# Learn: Responsible AI - validation, testing, approval
```

**AWS Exam Practice**:
- What is RAG? (Retrieval Augmented Generation)
- How do embeddings work?
- Prompt engineering techniques
- Grounding strategies (prevent hallucination)
- Responsible AI guardrails

**Code Example**:
```python
# GP-RAG/mlops/3-models/policy_drafter/drafter.py
from GP_RAG.jade_rag_langgraph import JadeRAGAgent

def draft_policy(resource: Dict, top_policies: List[str]) -> Dict:
    """RAG-grounded policy generation (AWS exam: Domain 2)"""

    # Step 1: Retrieve similar policies (RAG)
    agent = JadeRAGAgent()
    context = agent.query(f"Show examples of {top_policies[0]}")

    # Step 2: Prompt engineering (AWS exam: prompt techniques)
    prompt = f"""
    You are a Kubernetes security expert. Generate a Rego policy.

    Context (similar working policies):
    {context['response']}

    Task: Create a policy for this resource:
    {json.dumps(resource, indent=2)}

    Requirements:
    1. Follow the pattern from examples above
    2. Include unit tests (positive and negative cases)
    3. Add rationale explaining the policy

    Output format:
    Package: kubernetes.admission
    Deny rule: [your rule here]
    Tests: [test cases]
    """

    # Step 3: Generate (Foundation model)
    draft = llm.generate(prompt)

    # Step 4: Guardrails (AWS exam: Responsible AI)
    if not validate_schema(draft):
        raise ValueError("Invalid Rego syntax")

    if not run_tests(draft):
        raise ValueError("Tests failed")

    if compute_fp_rate(draft) > 0.05:
        raise ValueError("False positive rate too high")

    return draft
```

---

### Week 7-8: Monitoring + Production (Domain 4)

**AWS Topics**: Model monitoring, drift detection, MLOps, governance

**What to Build**:
```bash
# 1. MLflow setup
# File: GP-RAG/mlops/7-mlflow/setup.py
# Learn: Experiment tracking, model registry

# 2. Drift detection
# File: GP-RAG/mlops/5-monitoring/drift_detector.py
# Learn: Data drift, model drift, Evidently

# 3. FastAPI service
# File: GP-RAG/mlops/6-api/app.py
# Learn: Model deployment, REST APIs
```

**AWS Exam Practice**:
- What is model drift?
- How to monitor models in production?
- A/B testing strategies
- Model versioning and rollback
- Governance and compliance

**Code Example**:
```python
# GP-RAG/mlops/5-monitoring/drift_detector.py
from evidently.report import Report
from evidently.metrics import DataDriftTable

def detect_drift():
    """Drift detection (AWS exam: Domain 4)"""

    # Load baseline (Week 1 data)
    baseline = load_snapshot("2025-10-01")

    # Load current (today's data)
    current = load_snapshot("today")

    # Detect drift
    report = Report(metrics=[DataDriftTable()])
    report.run(reference_data=baseline, current_data=current)

    # Alert if drift detected (AWS exam: monitoring)
    if report.drift_detected:
        print("⚠️  DRIFT DETECTED!")
        print("Resource mix has changed - retrain models?")

        # Log to MLflow (AWS exam: governance)
        mlflow.log_metric("drift_detected", 1)
        mlflow.log_artifact("drift_report.html")
```

---

## 🧪 Hands-On Labs (AWS Exam Prep)

### Lab 1: Train Your First Model (Week 3)

**Exam Domain**: 1 (Fundamentals of AI and ML)

**Goal**: Train Policy Ranker baseline

```bash
cd GP-Backend/GP-RAG/mlops/3-models/policy_ranker/

# Create training script
cat > train.py << 'EOF'
#!/usr/bin/env python3
"""
Lab 1: Train Policy Ranker
AWS AI Practitioner Exam: Domain 1 - Supervised Learning
"""
import json
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import mlflow

# Load policy corpus
policies_file = Path("../../1-data/policies/index.jsonl")
policies = [json.loads(line) for line in policies_file.read_text().splitlines()]

# Feature engineering (AWS exam: data preparation)
# TODO: Extract features from policies

# Train/test split (AWS exam: evaluation strategy)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model (AWS exam: supervised learning)
model = LogisticRegression()
model.fit(X_train, y_train)

# Evaluate (AWS exam: metrics)
accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"Accuracy: {accuracy:.2f}")

# Log to MLflow (AWS exam: experiment tracking)
mlflow.log_metric("accuracy", accuracy)
mlflow.sklearn.log_model(model, "policy_ranker_v1")
EOF

python train.py
```

**Learning Outcomes**:
- ✅ Understand supervised learning
- ✅ Know train/test split purpose
- ✅ Can evaluate model accuracy
- ✅ Familiar with experiment tracking

---

### Lab 2: Build RAG Pipeline (Week 5)

**Exam Domain**: 2 (Fundamentals of Generative AI)

**Goal**: Use existing RAG to draft policies

```python
#!/usr/bin/env python3
"""
Lab 2: RAG for Policy Drafting
AWS AI Practitioner Exam: Domain 2 - RAG Architecture
"""
from GP_RAG.jade_rag_langgraph import JadeRAGAgent

# Initialize RAG (AWS exam: vector databases)
agent = JadeRAGAgent()

# Query for similar policies (AWS exam: semantic search)
query = "Show me policies that deny privileged containers"
result = agent.query(query)

print(f"Confidence: {result['confidence']:.2f}")
print(f"Sources: {len(result['sources'])}")
print(f"\nResponse:\n{result['response']}")

# AWS exam question practice:
# Q: What is the purpose of the confidence score?
# A: Indicates quality of retrieved knowledge (0.3 = no match, 0.95 = perfect match)

# Q: How does RAG prevent hallucination?
# A: Grounds LLM responses in retrieved documents, restricts to known knowledge

# Q: What role do embeddings play?
# A: Convert text to vectors for semantic similarity search
```

**Learning Outcomes**:
- ✅ Understand RAG architecture
- ✅ Know how embeddings work
- ✅ Can explain grounding strategies
- ✅ Familiar with vector databases

---

### Lab 3: Implement Guardrails (Week 6)

**Exam Domain**: 4 (Guidelines for Responsible AI)

**Goal**: Add validation to prevent bad policies

```python
#!/usr/bin/env python3
"""
Lab 3: Responsible AI Guardrails
AWS AI Practitioner Exam: Domain 4 - Responsible AI
"""
import subprocess
import json

def validate_rego_policy(rego_code: str) -> dict:
    """
    Guardrails for responsible AI (AWS exam: governance)
    """
    results = {"valid": True, "errors": []}

    # Guardrail 1: Schema validation (AWS exam: quality control)
    if not rego_code.startswith("package kubernetes.admission"):
        results["valid"] = False
        results["errors"].append("Invalid package name")

    # Guardrail 2: Syntax check (AWS exam: validation)
    try:
        result = subprocess.run(
            ["opa", "check", "-"],
            input=rego_code.encode(),
            capture_output=True
        )
        if result.returncode != 0:
            results["valid"] = False
            results["errors"].append("Syntax error")
    except Exception as e:
        results["valid"] = False
        results["errors"].append(str(e))

    # Guardrail 3: Test coverage (AWS exam: testing)
    # Must have at least 2 tests (positive + negative)
    if "test_" not in rego_code:
        results["valid"] = False
        results["errors"].append("Missing tests")

    # Guardrail 4: Human approval required (AWS exam: oversight)
    results["requires_approval"] = True
    results["auto_merge_allowed"] = False

    return results

# Test the guardrails
policy = """
package kubernetes.admission

deny[msg] {
    input.kind == "Pod"
    input.spec.containers[_].securityContext.privileged == true
    msg = "Privileged containers not allowed"
}

test_deny_privileged {
    deny["Privileged containers not allowed"] with input as {
        "kind": "Pod",
        "spec": {"containers": [{"securityContext": {"privileged": true}}]}
    }
}
"""

result = validate_rego_policy(policy)
print(json.dumps(result, indent=2))
```

**Learning Outcomes**:
- ✅ Understand responsible AI principles
- ✅ Know validation strategies
- ✅ Can implement guardrails
- ✅ Familiar with human oversight requirements

---

## 📖 AWS Exam Study Resources

### Recommended Study Order:

**Week 1-2**: Focus on Domain 1 while building data prep
- AWS Skill Builder: "Introduction to Machine Learning"
- Build: `mlops/1-data/` and `mlops/2-features/`

**Week 3-4**: Focus on Domain 1 while building Policy Ranker
- AWS Skill Builder: "Developing Machine Learning Models"
- Build: `mlops/3-models/policy_ranker/`

**Week 5-6**: Focus on Domain 2 & 3 while building RAG drafter
- AWS Skill Builder: "Generative AI Fundamentals"
- Build: `mlops/3-models/policy_drafter/`

**Week 7-8**: Focus on Domain 4 while building monitoring
- AWS Skill Builder: "Responsible AI Practices"
- Build: `mlops/5-monitoring/` and `mlops/7-mlflow/`

### Exam Question Practice (Based on This Project):

**Domain 1 Questions**:
- Q: What is the purpose of train/test split?
  - A: Your Policy Ranker uses it to prevent overfitting!

- Q: What is precision vs recall?
  - A: Your Fix Classifier needs high precision (low false positives)!

**Domain 2 Questions**:
- Q: How does RAG work?
  - A: Your jade_rag_langgraph.py is a working example!

- Q: What are embeddings?
  - A: Your ChromaDB stores 328+ document embeddings!

**Domain 3 Questions**:
- Q: How to evaluate text generation quality?
  - A: Your policy drafter uses test pass rate (>= 95%)!

- Q: What is prompt engineering?
  - A: Your drafter uses few-shot examples from RAG!

**Domain 4 Questions**:
- Q: What are responsible AI guardrails?
  - A: Your system has: schema validation, testing, no auto-merge, audit logging!

- Q: What is model drift?
  - A: Your drift detector monitors resource distribution changes!

---

## ✅ Final Recommendation

**Yes, GP-Backend/GP-RAG/mlops/ is the PERFECT place to build this!**

### Why?

1. ✅ **Easy to Navigate**: Everything AI/ML in one directory
2. ✅ **AWS Exam Aligned**: Each subdirectory maps to exam domains
3. ✅ **Learning Focus**: Clear progression (data → features → models → production)
4. ✅ **Reuses Foundation**: Leverage working RAG + LLM
5. ✅ **Hands-On Practice**: Build real ML models, not toy examples

### Structure Summary:

```
GP-Backend/GP-RAG/
├── [Working] core/                   ← Foundation (RAG, Graph)
├── [Working] jade_rag_langgraph.py   ← LLM reasoning
├── [Working] dynamic_learner.py      ← Auto-learning
│
├── [Build This!] mlops/
│   ├── 1-data/           ← Week 1-2: Data prep (Domain 1)
│   ├── 2-features/       ← Week 1-2: Feature engineering (Domain 1)
│   ├── 3-models/         ← Week 3-6: ML models (Domain 1, 2, 3)
│   ├── 4-troubleshooting/ ← Week 5-6: Learning loop (Domain 1)
│   ├── 5-monitoring/     ← Week 7-8: Drift detection (Domain 4)
│   ├── 6-api/            ← Week 7-8: Deployment (Domain 3)
│   └── 7-mlflow/         ← Week 7-8: Experiment tracking (Domain 4)
│
└── [Reference] *.md files ← Study guides
```

### Next Steps:

1. **Start Small**: Build `mlops/3-models/policy_ranker/heuristic.py` first
2. **Learn by Doing**: Each model teaches AWS exam concepts
3. **Track Progress**: Use MLflow to see improvements
4. **Take Exam**: By Week 8, you'll have hands-on experience with all 4 domains!

**You'll learn AWS AI Practitioner concepts while building a real production system!** 🚀

---

Last updated: 2025-10-16
