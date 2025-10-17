# GP-AI Quick Start Guide

## 🚀 For Interviewers & Demos

### What is GP-AI?

GP-AI is the **intelligent brain** of the GuidePoint Security Platform. It uses local LLMs (Qwen2.5-7B) to provide:
- AI-powered security analysis
- Knowledge-augmented reasoning (RAG)
- Natural language interface (Jade Chat)
- Autonomous agent workflows

**Key Differentiator**: Everything runs **locally** - no cloud API calls, full data privacy.

---

## 📁 Directory Structure

```
GP-AI/
├── core/           # AI engines (security analysis, RAG, reasoning)
├── models/         # LLM management (Qwen2.5, GPU config)
├── agents/         # Autonomous workflows (orchestration, troubleshooting)
├── cli/            # Command-line interfaces (jade-cli, jade chat)
├── api/            # REST API server (FastAPI)
├── integrations/   # Tool registry and scanner normalization
├── workflows/      # Pre-built workflows (approvals, automation)
└── config/         # System prompts and routing
```

---

## ⚡ Quick Demo Commands

### 1. Interactive Chat (Best for Demos)
```bash
jade chat
```
Then try:
- `"I want to scan my project quickly"`
- `"Show me the last scan results"`
- `"What security issues did we find?"`

### 2. Direct Security Scan
```bash
jade scan GP-PROJECTS/Terraform_CICD_Setup
```

### 3. RAG Knowledge Query
```bash
jade query "How do I prevent SQL injection in Python?"
```

### 4. Agentic Workflow
```bash
jade agent "Kubernetes pod crashlooping - help me debug"
```

### 5. List Available Projects
```bash
jade projects
```

---

## 🎯 Demo Talking Points

### 1. **Local AI Processing**
> "Unlike competitors using OpenAI/Claude APIs, we run everything locally using Qwen2.5-7B. This means:
> - No data leaves your network
> - No API costs
> - Full control over the model
> - HIPAA/SOC2 compliant by design"

### 2. **RAG-Powered Knowledge**
> "The RAG engine automatically ingests scan results, security docs, and compliance frameworks. When you ask a question, it:
> - Searches across all knowledge bases
> - Retrieves relevant context
> - Augments the LLM prompt
> - Returns answers with source citations"

**Show this**:
```bash
jade query "Show me all CRITICAL findings from last week"
```

### 3. **Natural Language Interface**
> "Jade Chat uses pattern matching + LLM intent recognition. You can say:
> - 'I want to scan my project' (natural language)
> - 'jade scan GP-PROJECTS/MyApp' (direct command)
> - 'quick scan DVWA' (shorthand)
>
> It understands context and executes the right tools."

**Show this**:
```bash
jade chat
> "scan my terraform project"
```

### 4. **Agentic Workflows**
> "Using LangGraph, Jade can perform multi-step reasoning:
> - Intent classification
> - Domain detection (k8s, terraform, opa)
> - Tool selection and execution
> - Multi-turn conversations"

**Show this**:
```bash
jade agent "I'm getting OPA policy violations on my Terraform plan"
```

### 5. **Professional Architecture**
> "Clean separation of concerns:
> - **Core** - AI engines
> - **Models** - LLM management
> - **Agents** - Autonomous workflows
> - **CLI** - User interfaces
> - **API** - External integrations
> - **Integrations** - Tool registry
>
> Each component is independently testable and documented."

---

## 📊 Key Metrics to Show

```bash
# System health
jade stats

# Knowledge base size
curl http://localhost:8000/api/v1/knowledge/stats

# Recent scan results
ls -lh GP-DATA/active/scans/ | head -10
```

**Expected Output**:
- Model: Qwen2.5-7B-Instruct
- Knowledge Base: 500+ documents
- Collections: scan_findings, documentation, compliance_frameworks
- Tools: bandit, trivy, semgrep, gitleaks, opa
- GPU: CUDA detected (if available)

---

## 🔧 Troubleshooting Quick Fixes

### Model not loading?
```bash
# Check if model is downloaded
ls ~/.cache/huggingface/hub/models--Qwen*/

# Download manually
python GP-AI/models/model_manager.py
```

### GPU not detected?
```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### RAG returning no results?
```bash
# Sync knowledge base
cd GP-DATA
python simple_sync.py
```

### Scan command not working in chat?
Fixed! Updated `jade_chat.py` to include proper `PYTHONPATH`.

---

## 🎨 Interview Demo Flow

### 1. Introduction (2 min)
"Let me show you our AI security platform. Everything you'll see runs locally - no cloud dependencies."

### 2. Interactive Chat Demo (3 min)
```bash
jade chat
> "show me the projects"
> "I want to scan Terraform_CICD_Setup quickly"
> "what did we find?"
```

### 3. Knowledge Query (2 min)
```bash
jade query "What are the top security best practices for RDS?"
```

### 4. Architecture Walkthrough (3 min)
Open `GP-AI/ARCHITECTURE.md` and explain:
- Core engines
- RAG integration
- Agentic workflows
- Clean separation

### 5. Code Quality (2 min)
Show:
- `GP-AI/README.md` - Professional documentation
- `GP-AI/core/ai_security_engine.py` - Clean code
- `GP-AI/api/main.py` - REST API design

### 6. Q&A (remaining time)

---

## 📝 Common Interview Questions

**Q: Why not use OpenAI/Claude?**
A: "Data privacy and cost. Running locally means no PII leaves the network, and no per-request API costs. We can fine-tune the model for security-specific tasks."

**Q: How does RAG improve accuracy?**
A: "RAG injects relevant context from our knowledge bases. Instead of relying on the model's training data, it searches scan results, security docs, and compliance frameworks in real-time."

**Q: What's the performance impact?**
A: "Model loads in 5-10s (once), inference is 1-3s per query on GPU, RAG queries are 100-200ms. Total scan analysis is 30-60s including scanner execution."

**Q: How do you handle hallucinations?**
A: "Three ways:
1. RAG grounds responses in real data
2. Security reasoning layer validates LLM outputs
3. Human approval workflows for critical actions"

**Q: Can this scale?**
A: "Yes - we can deploy multiple API instances, use GPU clusters, and the RAG engine supports sharding. Currently handles single-tenant, designed for multi-tenant."

---

## 🎓 Technical Deep Dive (If Asked)

### RAG Architecture
```
User Query → Embedding → Vector Search → Top-K Results → LLM Prompt Injection → Response
```

### Agent Workflow
```
Input → Intent Classifier → Domain Detector → RAG Query → Tool Selection → Execution → Synthesis
```

### Model Stack
```
Qwen2.5-7B-Instruct (default)
├── Tokenizer: Qwen2Tokenizer
├── Model: AutoModelForCausalLM
├── Precision: FP16 (GPU) / FP32 (CPU)
└── Inference: Transformers pipeline
```

---

## ✅ Pre-Demo Checklist

- [ ] Model downloaded: `ls ~/.cache/huggingface/hub/models--Qwen*/`
- [ ] Knowledge synced: `python GP-DATA/simple_sync.py`
- [ ] API running: `uvicorn GP-AI.api.main:app --reload` (optional)
- [ ] Sample project scanned: `jade scan GP-PROJECTS/DVWA`
- [ ] Recent results: `ls GP-DATA/active/scans/ | tail -5`

---

## 📚 Related Documentation

- `README.md` - High-level overview
- `ARCHITECTURE.md` - Detailed system design
- `GP-DATA/README.md` - Data management
- `GP-CONSULTING-AGENTS/README.md` - Security scanners

---

**Status**: ✅ Demo Ready
**Last Updated**: 2025-10-04
**Questions?**: Contact GuidePoint Security Team