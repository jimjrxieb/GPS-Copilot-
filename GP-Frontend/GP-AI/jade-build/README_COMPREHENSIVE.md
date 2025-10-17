# 🤖 GP-AI - Jade AI Security Intelligence Engine

## Overview

GP-AI is the **intelligent reasoning layer** of the GuidePoint Security Platform, powering **Jade AI** - an autonomous security consultant that combines local Large Language Models (LLMs) with security domain expertise to provide AI-powered analysis, remediation, and automation.

**Status**: ✅ Production Ready
**Size**: 1.1MB (60 files, 26 Python modules)
**Model**: Qwen2.5-7B-Instruct (local, offline)
**Last Updated**: 2025-10-07

---

## Purpose & Philosophy

### The Vision: Local AI Security Intelligence

**Problem**: Cloud-based AI security tools require:
- External API calls (data leakage risk)
- Internet connectivity (not offline-capable)
- Subscription costs (recurring fees)
- Limited customization (black box models)

**Solution**: GP-AI provides:
- ✅ **Local-First**: All models run on your hardware
- ✅ **Offline-Capable**: No internet required for analysis
- ✅ **Data Privacy**: Code never leaves your infrastructure
- ✅ **Customizable**: Fine-tune models on your patterns
- ✅ **Cost-Effective**: One-time hardware investment

### Architecture Philosophy

```
┌─────────────────────────────────────────────────────────────┐
│                    JADE AI ARCHITECTURE                     │
├─────────────────┬───────────────────┬───────────────────────┤
│   REASONING     │      KNOWLEDGE    │      AUTOMATION       │
│                 │                   │                       │
│  🧠 LLM Engine  │  🔍 RAG System    │  🤖 Agentic Workflows │
│  Qwen2.5-7B     │  ChromaDB         │  LangGraph            │
│  GPU-Optimized  │  Semantic Search  │  Multi-Step           │
│  Security-Tuned │  Context Aware    │  Human-in-Loop        │
└─────────────────┴───────────────────┴───────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐      ┌─────▼─────┐     ┌─────▼─────┐
   │ SCANNERS │      │  GP-DATA  │     │ GP-PROJECTS│
   │ (Input)  │◄────►│ (Storage) │◄───►│  (Targets) │
   │ Trivy    │      │ Results   │     │  Code Repos│
   │ Bandit   │      │ Vectors   │     │  IaC Files │
   │ Gitleaks │      │ Audit     │     │  K8s YAML  │
   └──────────┘      └───────────┘     └────────────┘
```

---

## Directory Structure

```
GP-AI/ (~1.1MB, 60 files)
├── core/                       # 🧠 Core AI Reasoning Engines
│   ├── ai_security_engine.py   # Main security analysis engine (401 LOC)
│   ├── rag_engine.py            # RAG knowledge retrieval (370 LOC)
│   └── security_reasoning.py    # Security domain logic (354 LOC)
│
├── models/                     # 🤖 LLM Model Management
│   ├── model_manager.py         # Model loading & inference (299 LOC)
│   └── gpu_config.py            # GPU/CUDA optimization (115 LOC)
│
├── agents/                     # 🎯 Autonomous Agent Workflows
│   ├── jade_orchestrator.py     # LangGraph-based orchestration (372 LOC)
│   └── troubleshooting_agent.py # Domain-specific troubleshooting (450 LOC)
│
├── cli/                        # 💻 Command-Line Interfaces
│   ├── jade-cli.py              # Main Jade CLI (jade <command>) (383 LOC)
│   ├── jade_chat.py             # Interactive chat mode (850 LOC)
│   ├── jade_explain_gha.py      # GitHub Actions explainer (195 LOC)
│   ├── jade_analyze_gha.py      # GHA deep analysis (854 LOC)
│   ├── gha_analyzer.py          # GHA parser module (618 LOC)
│   └── simple_gha_explainer.py  # Quick GHA troubleshooter (240 LOC)
│
├── api/                        # 🌐 REST API Server
│   ├── main.py                  # FastAPI application (219 LOC)
│   ├── approval_routes.py       # Human-in-the-loop workflows (240 LOC)
│   └── secrets_routes.py        # Secrets management endpoints (227 LOC)
│
├── integrations/               # 🔌 External Tool Integrations
│   ├── tool_registry.py         # Dynamic tool discovery (422 LOC)
│   ├── scan_integrator.py       # Scanner output normalization (335 LOC)
│   └── jade_gatekeeper_integration.py # OPA Gatekeeper integration
│
├── workflows/                  # 🔄 Pre-built Security Workflows
│   └── approval_workflow.py     # Human-in-the-loop approvals (447 LOC)
│
├── config/                     # ⚙️ Configuration & Prompts
│   ├── jade_prompts.py          # AI system prompts (265 LOC)
│   └── routing_config.json      # Intent routing configuration
│
├── engines/                    # 🔧 LLM Adapters
│   └── llm_adapter.py           # LLM provider abstraction (267 LOC)
│
├── _local_data/                # 📦 Local Runtime Data
│   ├── ai-models/               # Downloaded model cache
│   └── audit/                   # Local audit logs
│
├── ARCHITECTURE.md             # Detailed component design
├── QUICK_START.md              # Getting started guide
├── COMPLETE_JADE_MAP.md        # Full system map
├── CLEANUP_SUMMARY.md          # Historical cleanup notes
└── README.md                   # Main documentation

Total: 26 Python files, ~9,255 lines of code
```

---

## Key Components

### 1. Core Engines (`core/`)

#### **AI Security Engine** (`ai_security_engine.py`)

The main orchestrator for AI-powered security analysis.

**Capabilities**:
- **Vulnerability Analysis**: Deep CVE impact assessment with CVSS scoring
- **Attack Path Modeling**: Identify exploitation chains
- **Remediation Generation**: AI-suggested fixes with code examples
- **Compliance Mapping**: Automatic alignment to CIS, NIST, PCI-DSS, SOC2
- **Risk Scoring**: Contextual risk assessment based on environment

**Usage**:
```python
from GP_AI.core.ai_security_engine import AISecurityEngine

engine = AISecurityEngine()
result = engine.analyze_vulnerability({
    "cve_id": "CVE-2024-1234",
    "severity": "CRITICAL",
    "package": "openssl",
    "version": "1.1.1",
    "context": {"exposed_to_internet": True}
})

print(result['analysis'])      # LLM-generated analysis
print(result['remediation'])   # Actionable fix steps
print(result['risk_score'])    # Contextual risk (0-100)
```

#### **RAG Engine** (`rag_engine.py`)

Knowledge-augmented reasoning via Retrieval-Augmented Generation.

**Capabilities**:
- **Semantic Search**: Vector similarity search across security knowledge
- **Context Injection**: Relevant historical data injected into LLM prompts
- **Multi-Collection**: Separate knowledge bases (scans, docs, policies)
- **Auto-Sync**: Continuous ingestion from GP-DATA
- **Fast Queries**: 100-200ms response time

**Usage**:
```python
from GP_AI.core.rag_engine import RAGEngine

rag = RAGEngine()
results = rag.query(
    "How do I fix SQL injection in Python?",
    collection="security",
    limit=5
)

for doc in results:
    print(f"Source: {doc['source']}")
    print(f"Content: {doc['content'][:200]}...")
    print(f"Relevance: {doc['score']}")
```

**Vector Collections**:
- `jade-knowledge` - Security documentation, best practices
- `scan-results` - Historical scan findings
- `compliance-mappings` - Regulatory framework mappings
- `remediation-patterns` - Successful fix patterns

#### **Security Reasoning** (`security_reasoning.py`)

Domain-specific deterministic logic complementing LLM reasoning.

**Capabilities**:
- **CVE Analysis**: CVSS score parsing, impact assessment
- **Policy Violation Interpretation**: OPA/Gatekeeper policy explanation
- **Threat Modeling**: Attack vector identification
- **Risk Scoring**: Deterministic risk calculation algorithms

**Usage**:
```python
from GP_AI.core.security_reasoning import SecurityReasoning

reasoning = SecurityReasoning()
threat_analysis = reasoning.analyze_threat({
    "finding": "Hardcoded AWS credentials",
    "location": "config.py:42",
    "exposed": True
})

print(threat_analysis['severity'])    # CRITICAL
print(threat_analysis['attack_path']) # ["Credential Discovery", "Lateral Movement"]
print(threat_analysis['impact'])      # Full AWS account compromise
```

---

### 2. Model Layer (`models/`)

#### **Model Manager** (`model_manager.py`)

LLM lifecycle management and inference.

**Supported Models**:
- **Qwen2.5-7B-Instruct** (Default, Recommended)
  - Size: ~7GB
  - Speed: 1-3s per query (GPU)
  - Quality: Excellent for security reasoning
  - Location: `~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/`

- **Llama-3.1-8B-Instruct** (Alternative)
  - Size: ~8GB
  - Speed: 2-4s per query (GPU)
  - Quality: Strong general reasoning

- **DeepSeek-Coder-6.7B** (Code-focused)
  - Size: ~6.7GB
  - Speed: 1-2s per query (GPU)
  - Quality: Best for code analysis

**Usage**:
```python
from GP_AI.models.model_manager import ModelManager

manager = ModelManager(model_name="Qwen/Qwen2.5-7B-Instruct")
manager.load_model()  # ~5-10s on first run

response = manager.generate(
    prompt="Explain this vulnerability: SQL injection in user login",
    max_tokens=256,
    temperature=0.7
)

print(response['text'])
print(f"Inference time: {response['time_ms']}ms")
```

**GPU Configuration** (`gpu_config.py`):
```python
from GP_AI.models.gpu_config import GPUConfig

config = GPUConfig()
config.detect_hardware()

if config.has_cuda():
    print(f"GPU: {config.gpu_name}")
    print(f"VRAM: {config.vram_gb} GB")
    print(f"CUDA: {config.cuda_version}")
else:
    print("CPU fallback mode")
```

---

### 3. Agents (`agents/`)

#### **Jade Orchestrator** (`jade_orchestrator.py`)

Multi-step autonomous reasoning using LangGraph.

**Workflow Types**:
- **Scan → Analyze → Report**: Basic security assessment
- **Scan → Analyze → Fix → Verify**: Autonomous remediation
- **Scan → Analyze → Generate Policy**: Policy-as-code creation

**Usage**:
```python
from GP_AI.agents.jade_orchestrator import JadeOrchestrator

orchestrator = JadeOrchestrator()
result = orchestrator.execute(
    task="scan and fix Python security issues",
    target="GP-PROJECTS/MyApp",
    auto_approve=False  # Require human approval for fixes
)

print(f"Steps completed: {' → '.join(result['steps'])}")
print(f"Issues found: {result['findings_count']}")
print(f"Issues fixed: {result['fixes_applied']}")
print(f"Effectiveness: {result['fix_effectiveness']}%")
```

**Agentic Workflow Graph**:
```
    ┌─────────┐
    │  START  │
    └────┬────┘
         │
    ┌────▼────┐
    │  SCAN   │ - Select and run appropriate scanners
    └────┬────┘
         │
    ┌────▼────┐
    │ ANALYZE │ - LLM analyzes results, makes decisions
    └────┬────┘
         │
    ┌────▼────┐
    │ DECIDE  │ - Route based on decision
    └─┬───┬─┬─┘
      │   │ │
┌─────▼   │ └──────┐
│  FIX    │  REPORT │
└────┬────┘         │
     │              │
┌────▼────┐         │
│ VERIFY  │         │
└────┬────┘         │
     │              │
┌────▼──────────────▼┐
│      REPORT        │
└────────────────────┘
```

#### **Troubleshooting Agent** (`troubleshooting_agent.py`)

Domain-specific problem-solving for Kubernetes, Terraform, and OPA.

**Capabilities**:
- Kubernetes pod crash diagnosis
- Terraform validation errors
- OPA policy violations
- Log analysis and pattern detection

---

### 4. CLI Tools (`cli/`)

#### **Main CLI** (`jade-cli.py`)

Primary command-line interface for Jade.

**Commands**:
```bash
# Security scanning
jade scan <project>              # Run security scan with AI analysis
jade scan GP-PROJECTS/MyApp --scanners trivy,bandit

# Knowledge queries
jade query "question"             # Query RAG knowledge base
jade query "How to fix CVE-2024-1234?"

# Agentic workflows
jade agent "task"                 # Execute autonomous workflow
jade agent "scan and fix terraform issues"

# Interactive mode
jade chat                         # Natural language interface

# Project management
jade projects                     # List all projects
jade project add /path/to/project
jade project scan <name>

# GitHub Actions intelligence
jade explain workflow_run <id>    # Explain GHA failure
jade analyze-gha <repo> <run_id>  # Deep GHA analysis
```

#### **Chat Mode** (`jade_chat.py`)

Natural language conversational interface.

**Features**:
- **Pattern Matching + LLM**: Hybrid intent recognition
- **Context-Aware**: Remembers active project in session
- **Command Execution**: Translates NL → structured commands
- **Rich Formatting**: Beautiful terminal output

**Example Session**:
```bash
$ jade chat

🤖 Jade AI Security Consultant

> Show me critical findings in MyApp
🔍 Searching scan results...
Found 3 CRITICAL issues in MyApp:
  1. CVE-2024-1234 in openssl (CVSS: 9.8)
  2. Hardcoded AWS credentials in config.py:42
  3. SQL injection in auth.py:156

> Fix the hardcoded credentials
🔧 Applying fix for hardcoded credentials...
✅ Fixed: Moved credentials to environment variables
📝 Updated: config.py, .env.example
🔒 Recommendation: Rotate credentials in AWS Secrets Manager

> Scan for secrets across all projects
🔍 Running gitleaks across all projects...
...
```

#### **GitHub Actions Intelligence** (`jade_explain_gha.py`, `jade_analyze_gha.py`)

AI-powered GitHub Actions workflow analysis.

**Capabilities**:
- Parse workflow YAML and execution logs
- Identify failure root causes
- Suggest fixes for common issues
- Security analysis of workflow secrets

**Usage**:
```bash
# Quick explanation
jade explain workflow_run 12345

# Deep analysis
jade analyze-gha myorg/myrepo 12345

# Output:
# 🔍 Analyzing workflow run 12345...
#
# Root Cause: Python dependency conflict (pip install failed)
# Step Failed: "Install dependencies" (line 42)
# Error: "ERROR: Cannot install package X (conflicts with Y)"
#
# 🔧 Suggested Fixes:
# 1. Pin dependency versions in requirements.txt
# 2. Use requirements.lock for reproducibility
# 3. Update conflicting package Y to >= 2.0.0
```

---

### 5. API Server (`api/`)

FastAPI-based REST API for external integrations.

**Start Server**:
```bash
cd GP-AI
uvicorn api.main:app --reload --port 8000
```

**Endpoints**:

#### **POST /api/analyze** - Security Analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target": "GP-PROJECTS/MyApp",
    "scanners": ["trivy", "bandit"],
    "depth": "deep"
  }'

# Response:
{
  "status": "success",
  "findings": [...],
  "risk_score": 78,
  "compliance": {"SOC2": "FAIL", "CIS": "PARTIAL"}
}
```

#### **POST /api/query** - Knowledge Query
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to fix SQL injection in Python?",
    "context": {"language": "python"}
  }'

# Response:
{
  "answer": "To fix SQL injection in Python...",
  "sources": ["bandit_security_guide.md", "owasp_top10.md"],
  "confidence": 0.92
}
```

#### **POST /api/approval** - Human-in-the-Loop Workflow
```bash
curl -X POST http://localhost:8000/api/approval \
  -H "Content-Type: application/json" \
  -d '{
    "action": "delete_secrets",
    "target": "config.py",
    "requires_approval": true
  }'

# Response:
{
  "approval_id": "abc123",
  "status": "pending",
  "approval_url": "http://localhost:8000/approve/abc123"
}
```

#### **GET /api/secrets/{project}** - Secrets Management
```bash
curl http://localhost:8000/api/secrets/MyApp

# Response:
{
  "secrets_found": 5,
  "secrets": [
    {"type": "aws_access_key", "location": "config.py:42", "severity": "CRITICAL"}
  ]
}
```

---

### 6. Integrations (`integrations/`)

#### **Tool Registry** (`tool_registry.py`)

Dynamic scanner/fixer discovery and registration.

**Usage**:
```python
from GP_AI.integrations.tool_registry import ToolRegistry

# Auto-discover tools
ToolRegistry.discover_tools()

# List available tools
tools = ToolRegistry.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['capabilities']}")

# Execute tool
result = ToolRegistry.execute_tool(
    "scan_secrets_gitleaks",
    target_path="."
)
```

#### **Scan Integrator** (`scan_integrator.py`)

Normalize and aggregate multi-scanner outputs.

**Features**:
- Severity normalization (all scanners → common scale)
- Deduplication (same issue found by multiple scanners)
- GP-DATA sync (auto-save to centralized storage)
- Format conversion (scanner-specific → unified JSON)

**Usage**:
```python
from GP_AI.integrations.scan_integrator import ScanIntegrator

integrator = ScanIntegrator()
results = integrator.aggregate([
    bandit_results,
    trivy_results,
    gitleaks_results
])

print(f"Deduplicated findings: {len(results['findings'])}")
print(f"Critical: {results['stats']['critical']}")
print(f"Saved to: {results['output_path']}")
```

---

## Data Flow Architecture

### Scan & Analyze Flow

```
User: "jade scan GP-PROJECTS/MyApp"
         ↓
1. CLI (jade-cli.py) parses command
         ↓
2. Tool Registry discovers scanners (bandit, trivy, gitleaks)
         ↓
3. Scan Integrator runs tools → GP-DATA/active/results/
         ↓
4. RAG Engine indexes findings → ChromaDB
         ↓
5. AI Security Engine analyzes with LLM
         ↓
6. Output: Risk scores, remediations, compliance mappings
```

### Chat Mode Flow

```
User: "Show me critical CVEs in MyApp"
         ↓
1. jade_chat.py receives natural language
         ↓
2. Pattern matching + LLM intent classification
         ↓
3. RAG Engine queries knowledge base
         ↓
4. AI Security Engine reasons about findings
         ↓
5. Response synthesized with context
         ↓
6. Pretty-printed to terminal (Rich formatting)
```

### Agentic Workflow Flow

```
User: "jade agent 'scan and fix python issues'"
         ↓
1. Jade Orchestrator receives task
         ↓
2. LangGraph decomposes into steps (scan → analyze → fix → verify)
         ↓
3. For each step:
   - Select appropriate tool
   - Execute with parameters
   - Evaluate result
   - Decide next action
         ↓
4. Human approval gate (if HIGH/CRITICAL changes)
         ↓
5. Apply fixes → Verify → Learn patterns
         ↓
6. Generate report → GP-DATA/active/reports/
```

---

## Configuration

### Model Selection

Edit `GP-PLATFORM/james-config/gp_data_config.py`:

```python
# Default model (Recommended)
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# High-performance alternatives
# DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
# DEFAULT_MODEL = "deepseek-ai/deepseek-coder-6.7b-instruct"
# DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
```

### Environment Variables

```bash
# Model configuration
export GP_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
export GP_MODEL_CACHE="$HOME/.cache/huggingface"

# API server
export GP_API_PORT=8000
export GP_API_HOST="0.0.0.0"

# RAG configuration
export CHROMA_PATH="/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/chroma_db"

# GPU settings
export CUDA_VISIBLE_DEVICES=0  # Use first GPU
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
```

### RAG Collections

Knowledge bases are auto-synced from:
- `GP-DATA/active/scans/` - Scan results
- `GP-KNOWLEDGE-HUB/knowledge-base/` - Security documentation
- `GP-RAG/unprocessed/` - New knowledge to index

### System Prompts

Located in [config/jade_prompts.py](config/jade_prompts.py):
- Security expert persona
- Reasoning templates
- Domain-specific instructions

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 16GB | 32GB |
| **GPU** | None (CPU fallback) | NVIDIA 8GB+ VRAM |
| **Disk** | 10GB | 20GB (multiple models) |
| **CUDA** | - | 11.8+ |
| **OS** | Linux, macOS, Windows | Linux (best performance) |

---

## Performance Metrics

| Operation | Time (GPU) | Time (CPU) |
|-----------|-----------|-----------|
| **Model Loading** | 5-10s | 15-30s |
| **Single Query** | 1-3s | 5-10s |
| **RAG Search** | 100-200ms | 100-200ms |
| **Full Scan Analysis** | 3-5s | 10-20s |
| **Batch Processing (10)** | 15-30s | 60-120s |

---

## Security & Privacy

✅ **Local-First**: All models run locally, no cloud API calls
✅ **No Data Leakage**: Code never sent to external services
✅ **Encrypted Storage**: Secrets in GP-DATA/audit/ encrypted at rest
✅ **Audit Trail**: All AI decisions logged to evidence.jsonl
✅ **Approval Gates**: Human-in-the-loop for destructive actions
✅ **PII Scrubbing**: Automatic removal from prompts

---

## Integration Points

### Data Sources (Input)
- **GP-DATA/active/results/** - Scanner outputs
- **GP-KNOWLEDGE-HUB/knowledge-base/** - Security documentation
- **GP-PROJECTS/** - User code repositories
- **GitHub API** - Actions logs (via gh CLI)

### Data Destinations (Output)
- **GP-DATA/active/results/** - AI-enhanced findings
- **GP-DATA/active/audit/** - Decision audit trail
- **GP-DATA/active/chroma_db/** - Vector embeddings
- **Terminal/API** - User-facing outputs

### External Tools
- **GP-CONSULTING/scanners/** - Invokes security tools
- **GP-CONSULTING/fixers/** - Applies AI-generated fixes
- **bin/** - Security tool binaries

---

## Observability

### Audit Logging

```bash
# View AI decisions
cat GP-DATA/active/audit/jade-evidence.jsonl | jq .

# Check recent queries
tail -20 GP-DATA/active/audit/jade-evidence.jsonl | jq '.action'

# Statistics dashboard
jade-stats
```

### Metrics Tracked
- Total queries processed
- LLM confidence scores
- Fix success rates
- Error rates by component
- Model inference times

---

## Usage Examples

### Example 1: Interactive Security Consulting

```bash
jade chat

> Scan MyApp for secrets
🔍 Running gitleaks on GP-PROJECTS/MyApp...
Found 3 secrets:
  1. AWS Access Key (config.py:42)
  2. GitHub Token (.env:7)
  3. API Secret (utils.py:89)

> Fix the AWS credentials
🔧 Applying fix...
✅ Moved to environment variables
📝 Created .env.example template
🔒 Recommendation: Rotate in AWS Secrets Manager
```

### Example 2: Autonomous Workflow

```python
from GP_AI.agents.jade_orchestrator import JadeOrchestrator

orchestrator = JadeOrchestrator()
result = orchestrator.execute(
    task="scan and fix python security issues",
    target="GP-AI/",
    auto_approve=False
)

# Output:
# 🔍 Step 1: Scanning GP-AI/...
# ✅ Scan complete: 12 issues found
#
# 🧠 Step 2: Analyzing scan results...
# ✅ Analysis complete: 8 auto-fixable
#
# 🔧 Step 3: Applying fixes (8 issues)...
# ✅ Fixes applied: 8/8 successful
#
# ✓ Step 4: Verifying fixes...
# ✅ Verification: 66.7% effectiveness
#
# 📚 Step 5: Learning patterns...
# ✅ Learned 8 patterns
```

### Example 3: API Integration

```bash
# Start API server
cd GP-AI
uvicorn api.main:app --reload --port 8000

# Query knowledge base
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How to fix CVE-2024-1234?"}'

# Run security scan
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"target": "GP-PROJECTS/MyApp", "scanners": ["trivy", "bandit"]}'
```

---

## Troubleshooting

### Model Loading Fails

```bash
# Download manually
huggingface-cli download Qwen/Qwen2.5-7B-Instruct

# Check cache
ls ~/.cache/huggingface/hub/
```

### GPU Not Detected

```bash
nvidia-smi  # Check GPU
python -c "import torch; print(torch.cuda.is_available())"
```

### RAG No Results

```bash
# Rebuild vector DB
cd GP-DATA && python simple_sync.py
```

### API Port Conflict

```bash
# Use different port
uvicorn api.main:app --port 8001
```

### Slow Inference

```bash
# Check GPU utilization
nvidia-smi -l 1

# Enable GPU optimizations
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"

# Use smaller model
export GP_MODEL_NAME="deepseek-ai/deepseek-coder-6.7b"
```

---

## Related Components

- **[GP-DATA/](../GP-DATA/)** - Centralized data management and RAG storage
- **[GP-CONSULTING/](../GP-CONSULTING/)** - Security scanners and fixers
- **[GP-PLATFORM/](../GP-PLATFORM/)** - Shared configuration (james-config)
- **[GP-RAG/](../GP-RAG/)** - Document ingestion pipelines
- **[GP-KNOWLEDGE-HUB/](../GP-KNOWLEDGE-HUB/)** - Security knowledge base
- **[bin/](../bin/)** - Security tool binaries
- **[ai-env/](../ai-env/)** - Python virtual environment

---

## Quick Reference

```bash
# Interactive chat
jade chat

# Scan project
jade scan GP-PROJECTS/MyApp

# Query knowledge
jade query "CVE-2024-1234 impact?"

# List projects
jade projects

# Explain GHA failure
jade explain workflow_run 12345

# Stats dashboard
jade-stats

# API server
cd GP-AI && uvicorn api.main:app --reload

# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Rebuild RAG
cd ../GP-DATA && python simple_sync.py
```

---

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed component design
- **[QUICK_START.md](QUICK_START.md)** - Getting started guide
- **[COMPLETE_JADE_MAP.md](COMPLETE_JADE_MAP.md)** - Full system map
- **[cli/CHAT_MODE_README.md](cli/CHAT_MODE_README.md)** - Chat interface docs
- **[../START_HERE.md](../START_HERE.md)** - Platform overview
- **[../GP-DOCS/](../GP-DOCS/)** - Complete platform documentation

---

## Key Features Summary

### 🧠 AI-Powered Security Analysis
- **Vulnerability Assessment**: Deep CVE impact analysis with CVSS scoring
- **Attack Path Modeling**: Identify exploitation chains
- **Remediation Generation**: AI-suggested fixes with code examples
- **Compliance Mapping**: Automatic alignment to CIS, NIST, PCI-DSS

### 🔍 RAG Knowledge System
- **Vector Search**: Semantic search across 4 knowledge collections
- **Auto-Sync**: Continuous ingestion from GP-DATA
- **Context-Aware**: Injects relevant historical data into LLM prompts
- **Fast**: 100-200ms query time

### 🤖 Autonomous Agents
- **Multi-Step Reasoning**: LangGraph-based task decomposition
- **Tool Selection**: Automatically chooses appropriate scanners
- **Self-Healing**: Retries with adjusted strategies on failure
- **Human-in-the-Loop**: Approval gates for destructive actions

### 💬 Natural Language Interface
- **Conversational**: "Show me secrets in project X"
- **Intent Recognition**: Pattern + LLM hybrid classification
- **Project Context**: Remembers active project in session
- **Command Execution**: Translates NL → structured commands

---

**Status**: ✅ Production Ready
**Last Updated**: 2025-10-07
**Version**: 2.1
**Lines of Code**: ~9,255 Python LOC
**Maintained by**: LinkOps Industries - JADE AI Security Platform Team