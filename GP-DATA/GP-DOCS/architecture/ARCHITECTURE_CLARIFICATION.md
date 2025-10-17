# GP-JADE Architecture Clarification

## Executive Summary

**THE BRAIN:** GP-AI is the intended orchestration layer, but GP-CONSULTING-AGENTS contains the actual workflow implementations. They need to be fully integrated.

**Current State:** Components exist separately but aren't fully connected into the agentic workflow you envisioned.

---

## Component Breakdown

### 1. GP-RAG (Knowledge Base) ✅ COMPLETE
**Role:** Vector database + retrieval engine
**Status:** Fully functional with 77,527 documents

**What It Does:**
- Stores embedded security knowledge (OPA, Kubernetes, Terraform, CKS, compliance, etc.)
- Provides RAG retrieval for Jade's decision-making
- ChromaDB vector store with sentence-transformers embeddings

**Key Files:**
- [core/jade_engine.py](GP-RAG/core/jade_engine.py) - RAG + LangGraph engine
- [tools/ingest.py](GP-RAG/tools/ingest.py) - Knowledge ingestion
- [vector-store/](GP-RAG/vector-store/) - 77K+ embedded documents

**API:**
```python
from GP_RAG.core.jade_engine import JadeRAGAgent
agent = JadeRAGAgent()
results = agent.query("Create OPA policy for root prevention")
```

---

### 2. GP-AI (Integration Layer) 🔄 PARTIALLY COMPLETE
**Role:** AI orchestration, API server, and integration hub
**Status:** Has components but NOT fully connected to workflows

**What It Does:**
- **API Server** ([api/main.py](GP-AI/api/main.py)): FastAPI endpoints for scan/query/ingest
- **Jade Enhanced** ([jade_enhanced.py](GP-AI/jade_enhanced.py)): Main AI interface with context integration
- **Engines:** RAG, reasoning, and security analysis engines
- **Integrations:** Scan results, tool registry, Gatekeeper

**Key Files:**
- [api/main.py](GP-AI/api/main.py:1) - FastAPI server with `/api/v1/scan`, `/api/v1/query` endpoints
- [jade_enhanced.py](GP-AI/jade_enhanced.py:1) - Enhanced Jade with full data access
- [engines/rag_engine.py](GP-AI/engines/rag_engine.py) - RAG query interface
- [integrations/scan_results_integrator.py](GP-AI/integrations/scan_results_integrator.py) - Scan data bridge
- [integrations/tool_registry.py](GP-AI/integrations/tool_registry.py) - Tool awareness

**Current Gap:** API exists but doesn't call GP-CONSULTING-AGENTS workflows

---

### 3. GP-CONSULTING-AGENTS (Workflow Brain) ✅ COMPLETE
**Role:** Security scanners, fixers, agents, and workflow orchestration
**Status:** Fully implemented - THIS IS WHERE THE BRAIN LIVES

**What It Does:**

#### **Scanners** (11 tools):
- [scanners/bandit_scanner.py](GP-CONSULTING-AGENTS/scanners/bandit_scanner.py) - Python SAST
- [scanners/trivy_scanner.py](GP-CONSULTING-AGENTS/scanners/trivy_scanner.py) - Container/IaC scanning
- [scanners/semgrep_scanner.py](GP-CONSULTING-AGENTS/scanners/semgrep_scanner.py) - Multi-language SAST
- [scanners/gitleaks_scanner.py](GP-CONSULTING-AGENTS/scanners/gitleaks_scanner.py) - Secrets detection
- [scanners/checkov_scanner.py](GP-CONSULTING-AGENTS/scanners/checkov_scanner.py) - IaC security
- [scanners/tfsec_scanner.py](GP-CONSULTING-AGENTS/scanners/tfsec_scanner.py) - Terraform scanning
- [scanners/kube_bench_scanner.py](GP-CONSULTING-AGENTS/scanners/kube_bench_scanner.py) - CIS Kubernetes
- [scanners/run_all_scanners.py](GP-CONSULTING-AGENTS/scanners/run_all_scanners.py) - **Orchestrator**

#### **Agents** (15 specialists):
- [agents/cks_agent.py](GP-CONSULTING-AGENTS/agents/cks_agent.py) - Certified Kubernetes Security expert
- [agents/cka_agent.py](GP-CONSULTING-AGENTS/agents/cka_agent.py) - Kubernetes Administrator expert
- [agents/sast_agent.py](GP-CONSULTING-AGENTS/agents/sast_agent.py) - Static analysis specialist
- [agents/secrets_agent.py](GP-CONSULTING-AGENTS/agents/secrets_agent.py) - Secrets management
- [agents/container_agent.py](GP-CONSULTING-AGENTS/agents/container_agent.py) - Container security
- [agents/iac_agent.py](GP-CONSULTING-AGENTS/agents/iac_agent.py) - Infrastructure as Code
- [agents/devsecops_agent.py](GP-CONSULTING-AGENTS/agents/devsecops_agent.py) - CI/CD security
- [agents/dfir_agent.py](GP-CONSULTING-AGENTS/agents/dfir_agent.py) - Digital forensics
- [agents/research_agent.py](GP-CONSULTING-AGENTS/agents/research_agent.py) - Security research
- [agents/qa_agent.py](GP-CONSULTING-AGENTS/agents/qa_agent.py) - Quality assurance
- [agents/client_support_agent.py](GP-CONSULTING-AGENTS/agents/client_support_agent.py) - Client interaction
- [agents/kubernetes_fixer.py](GP-CONSULTING-AGENTS/agents/kubernetes_fixer.py) - K8s remediation
- [agents/kubernetes_troubleshooter.py](GP-CONSULTING-AGENTS/agents/kubernetes_troubleshooter.py) - K8s debugging
- [agents/kubernetes_validator.py](GP-CONSULTING-AGENTS/agents/kubernetes_validator.py) - K8s validation

#### **Workflows** (The Complete Pipeline):
- [workflows/full_workflow.py](GP-CONSULTING-AGENTS/workflows/full_workflow.py:1) - **7-step complete workflow:**
  1. Pre-scan baseline documentation
  2. Security scan (all tools)
  3. Apply fixes
  4. CKS-level cluster deployment/testing
  5. Post-scan verification
  6. Generate documentation
  7. RAG integration

- [workflows/scan_workflow.py](GP-CONSULTING-AGENTS/workflows/scan_workflow.py:1) - Scanner orchestration
- [workflows/fix_workflow.py](GP-CONSULTING-AGENTS/workflows/fix_workflow.py:1) - Fixer orchestration
- [workflows/deploy_test_workflow.py](GP-CONSULTING-AGENTS/workflows/deploy_test_workflow.py) - Deployment validation

**Key Insight:** I incorrectly said these workflows were "missing" - they exist and are complete!

---

### 4. GP-DATA (Storage Layer) ✅ COMPLETE
**Role:** Centralized data storage for all scan results, reports, and knowledge
**Location:** `/home/jimmie/linkops-industries/GP-copilot/GP-DATA`

**Structure:**
```
GP-DATA/
├── active/           # Current scan results
├── archive/          # Historical data
├── knowledge-base/   # Documentation and research
├── metadata/         # Scan metadata and tracking
└── research/         # Security research data
```

---

## The Agentic Workflow You Want

```
User → Jade Chat/CLI → Scanner → Report → Jade → Fixes → Verification → User
         ↑                ↓                    ↓               ↓
         └────────────── Memory (RAG) ←───────┴───────────────┘
```

### What EXISTS:
✅ **GP-RAG**: 77K+ documents ready for retrieval
✅ **GP-CONSULTING-AGENTS**: Complete scan→fix→verify workflows
✅ **GP-AI**: API server with scan/query endpoints
✅ **Agents**: 15 specialized security agents
✅ **Scanners**: 11 security tools with orchestration
✅ **GP-DATA**: Centralized storage

### What's MISSING (Integration Gaps):
❌ **GP-AI doesn't call GP-CONSULTING-AGENTS workflows**
❌ **CLI interface needs to trigger full_workflow.py**
❌ **Jade doesn't use RAG results to inform fix decisions**
❌ **No LangGraph workflow connecting all pieces**
❌ **API endpoints exist but don't execute complete workflows**

---

## Correct Architecture

### **THE BRAIN = GP-AI + GP-CONSULTING-AGENTS (Integrated)**

```
┌─────────────────────────────────────────────────────┐
│                      USER                            │
│              (CLI / Web UI / API)                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│                    GP-AI                             │
│              (Orchestration Layer)                   │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  jade_enhanced.py                            │  │
│  │  - Receives user query                       │  │
│  │  - Analyzes with RAG context                 │  │
│  │  - Calls GP-CONSULTING-AGENTS workflows      │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  FastAPI Server (api/main.py)                       │
│  - /api/v1/scan    - /api/v1/query                 │
│  - /api/v1/fix     - /api/v1/verify                │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│    GP-RAG        │    │ GP-CONSULTING-   │
│  (Knowledge)     │    │    AGENTS        │
│                  │    │  (Execution)     │
│ - 77K+ docs      │    │                  │
│ - Retrieval      │    │ workflows/       │
│ - Embeddings     │    │ ├─ full_workflow │
│                  │    │ ├─ scan_workflow │
│                  │    │ └─ fix_workflow  │
│                  │    │                  │
│                  │    │ scanners/        │
│                  │    │ agents/          │
│                  │    │ fixers/          │
└──────────────────┘    └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
            ┌──────────────────┐
            │     GP-DATA      │
            │  (Storage)       │
            │                  │
            │ - Scan results   │
            │ - Reports        │
            │ - Metadata       │
            └──────────────────┘
```

---

## Deployment Requirements

### Python Dependencies
**Core Requirements:**
```txt
# LLM & RAG
torch>=2.6.0
transformers>=4.36.0
langchain>=0.3.0
langgraph>=0.2.0
sentence-transformers>=2.2.2
chromadb>=0.4.22

# API & Web
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.0.0

# Security Tools Integration
python-jose[cryptography]>=3.4.0
pyyaml>=6.0.1
requests>=2.31.0

# Data Processing
numpy>=1.24.0
pandas>=2.0.0
```

### Qwen Models (Too Large for GitHub)
**Location:** `~/.cache/huggingface/hub/`

**Currently Downloaded:**
- ✅ Qwen2.5-7B-Instruct (14GB)
- ✅ Qwen2.5-3B-Instruct (6GB)
- ✅ Qwen2.5-1.5B-Instruct (3GB)

**Setup Script Needed:** [setup_models.sh](setup_models.sh) to download on new machines

### Security Tool Binaries
**Location:** `/home/jimmie/linkops-industries/GP-copilot/bin/`

**Currently Installed:**
- ✅ bandit
- ✅ trivy
- ✅ semgrep
- ✅ gitleaks
- ✅ checkov
- ✅ tfsec
- ✅ opa
- ✅ kubescape

**Setup Script Needed:** [setup_tools.sh](setup_tools.sh) to download on new machines

---

## What Needs To Be Done

### 1. Connect GP-AI to GP-CONSULTING-AGENTS ⚠️ CRITICAL
**File to modify:** [GP-AI/jade_enhanced.py](GP-AI/jade_enhanced.py:1)

**Add method:**
```python
def execute_full_security_workflow(self, project_path: str) -> Dict:
    """Execute complete scan → fix → verify workflow"""
    from GP_CONSULTING_AGENTS.workflows.full_workflow import EnhancedSecurityWorkflow

    # Get RAG context for project type
    project_context = self.rag_engine.query_knowledge(
        f"Security best practices for {project_path}",
        n_results=5
    )

    # Execute workflow
    workflow = EnhancedSecurityWorkflow()
    results = workflow.execute_complete_workflow(project_path)

    # Analyze results with RAG
    analysis = self.analyze_with_context(
        f"Analyze these scan results and recommend fixes",
        project=project_path
    )

    return {
        "workflow_results": results,
        "ai_analysis": analysis
    }
```

### 2. Update API Endpoints ⚠️ CRITICAL
**File to modify:** [GP-AI/api/main.py](GP-AI/api/main.py:101)

**Change `/api/v1/scan` endpoint** (line 101) to call full workflow:
```python
@app.post("/api/v1/scan", response_model=ScanResponse)
async def scan_project(request: ScanRequest):
    from jade_enhanced import JadeEnhanced
    from GP_CONSULTING_AGENTS.workflows.full_workflow import EnhancedSecurityWorkflow

    jade = JadeEnhanced()
    results = jade.execute_full_security_workflow(request.project_path)
    # ... format and return
```

### 3. Create CLI Interface 📝 NEW FILE NEEDED
**Create:** `GP-AI/cli/jade-cli.py`

```python
#!/usr/bin/env python3
"""Jade CLI - Interactive Security Workflow"""
import sys
from jade_enhanced import JadeEnhanced

def main():
    jade = JadeEnhanced()

    if sys.argv[1] == "scan":
        project = sys.argv[2]
        results = jade.execute_full_security_workflow(project)
        print(f"✅ Scan complete: {results['summary']}")

    elif sys.argv[1] == "query":
        question = " ".join(sys.argv[2:])
        answer = jade.analyze_with_context(question)
        print(answer)

if __name__ == "__main__":
    main()
```

### 4. Create Setup Scripts 📝 NEW FILES NEEDED

**Create:** `setup_models.sh`
```bash
#!/bin/bash
echo "📥 Downloading Qwen models..."
python3 -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
model_name = 'Qwen/Qwen2.5-7B-Instruct'
print(f'Downloading {model_name}...')
AutoTokenizer.from_pretrained(model_name)
AutoModelForCausalLM.from_pretrained(model_name)
print('✅ Model downloaded to ~/.cache/huggingface/')
"
```

**Create:** `setup_tools.sh`
```bash
#!/bin/bash
echo "📥 Downloading security tools..."
mkdir -p bin && cd bin

# Trivy
wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.tar.gz
tar -xzf trivy_Linux-64bit.tar.gz

# Gitleaks
wget https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz
tar -xzf gitleaks_linux_x64.tar.gz

# Add to PATH
echo 'export PATH=$PATH:$PWD/bin' >> ~/.bashrc
```

**Create:** `requirements.txt` (root level)
```txt
# Core LLM
torch>=2.6.0
transformers>=4.36.0
langchain>=0.3.0
langgraph>=0.2.0

# RAG
sentence-transformers>=2.2.2
chromadb>=0.4.22

# API
fastapi>=0.109.0
uvicorn>=0.27.0

# Security
python-jose[cryptography]>=3.4.0
pyyaml>=6.0.1
```

---

## Summary

### ✅ What Works:
- RAG retrieval (77K+ documents)
- Individual scanners
- Individual agents
- Complete workflow scripts
- API server structure

### ❌ What's Broken:
- GP-AI doesn't call GP-CONSULTING-AGENTS
- No end-to-end agentic loop
- CLI doesn't exist
- Setup scripts missing

### 🎯 Next Steps:
1. Connect GP-AI to workflows (1 hour)
2. Create CLI interface (30 min)
3. Create setup scripts (30 min)
4. Test end-to-end workflow (1 hour)
5. Document and push to GitHub

**Total Time to Complete:** ~3 hours of integration work