# GP-AI: AI Security Intelligence Engine

> **Jade AI** - Intelligent security analysis, reasoning, and automation powered by local LLMs

## Overview

GP-AI is the intelligent reasoning layer of the GuidePoint Security Platform. It provides:

- 🧠 **AI Security Engine** - Deep security analysis and threat reasoning
- 🔍 **RAG Knowledge Base** - Context-aware security knowledge retrieval
- 🤖 **Agentic Workflows** - Multi-step autonomous security operations
- 💬 **Natural Language Interface** - Conversational security consulting via Jade Chat

## Architecture

```
GP-AI/
├── core/                    # Core AI engines and reasoning
│   ├── ai_security_engine.py    # Main security analysis engine
│   ├── rag_engine.py            # RAG knowledge retrieval
│   └── security_reasoning.py    # Security-specific reasoning logic
│
├── models/                  # LLM model management
│   ├── model_manager.py         # Model loading and inference
│   └── gpu_config.py            # GPU/CUDA configuration
│
├── agents/                  # Autonomous agent workflows
│   ├── jade_orchestrator.py     # LangGraph-based orchestration
│   └── troubleshooting_agent.py # Domain-specific troubleshooting
│
├── cli/                     # Command-line interfaces
│   ├── jade-cli.py              # Main Jade CLI (jade <command>)
│   └── jade_chat.py             # Interactive chat mode
│
├── api/                     # REST API interfaces
│   ├── main.py                  # FastAPI application
│   ├── approval_routes.py       # Human approval workflows
│   └── secrets_routes.py        # Secrets management endpoints
│
├── integrations/            # External tool integrations
│   ├── tool_registry.py         # Tool discovery and registration
│   └── scan_integrator.py       # Scanner result processing
│
├── workflows/               # Pre-built security workflows
│   └── approval_workflow.py     # Human-in-the-loop approvals
│
└── config/                  # Configuration and prompts
    ├── jade_prompts.py          # AI system prompts
    └── routing_config.json      # Intent routing configuration

```

## Key Components

### 1. Core Engines (`core/`)

**AI Security Engine** - Orchestrates security analysis
- Deep vulnerability analysis
- Attack path reasoning
- Remediation generation
- Compliance mapping

**RAG Engine** - Knowledge-augmented reasoning
- Semantic search across security knowledge
- Context injection for LLM queries
- Multi-collection knowledge bases
- Auto-sync with scan results

**Security Reasoning** - Domain-specific logic
- CVE analysis and impact assessment
- Policy violation interpretation
- Threat modeling
- Risk scoring

### 2. Model Layer (`models/`)

**Model Manager** - LLM lifecycle management
- Hugging Face model loading
- GPU/CPU optimization
- Inference API
- Model switching (Qwen2.5, Llama3, etc.)

**GPU Config** - Hardware optimization
- CUDA detection and setup
- Memory management
- Multi-GPU support
- Fallback to CPU

### 3. Agents (`agents/`)

**Jade Orchestrator** - Multi-step reasoning (LangGraph)
- Intent classification
- Tool selection and execution
- Multi-turn conversations
- Agentic workflows

**Troubleshooting Agent** - Domain-specific problem solving
- Kubernetes debugging
- Terraform validation
- OPA policy resolution
- Log analysis

### 4. CLI Tools (`cli/`)

**jade-cli.py** - Main command interface
```bash
jade scan <project>          # Security scan
jade query "question"        # RAG query
jade agent "task"            # Agentic workflow
jade chat                    # Interactive mode
jade projects                # List projects
```

**jade_chat.py** - Natural language interface
- Pattern matching + LLM intent recognition
- Context-aware project handling
- Command execution
- Result summarization

### 5. API Server (`api/`)

FastAPI-based REST API for external integrations:

- `POST /api/analyze` - Security analysis
- `POST /api/query` - RAG knowledge query
- `POST /api/approval` - Human approval workflows
- `GET /api/secrets` - Secrets detection and rotation

### 6. Integrations (`integrations/`)

**Tool Registry** - Dynamic tool discovery
- Scanner registration (Trivy, Bandit, etc.)
- Capability detection
- Tool versioning

**Scan Integrator** - Normalize scanner outputs
- Multi-scanner result aggregation
- Severity normalization
- Deduplication
- GP-DATA sync

## Usage

### Quick Start

```bash
# Interactive chat mode
jade chat

# Run security scan with AI analysis
jade scan GP-PROJECTS/MyApp

# Query knowledge base
jade query "How do I fix CVE-2024-1234?"

# Agentic workflow
jade agent "Analyze Kubernetes pod crashloop"
```

### API Mode

```bash
# Start API server
cd GP-AI
uvicorn api.main:app --reload --port 8000

# Query via API
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me critical findings"}'
```

### Python Integration

```python
from GP_AI.core.ai_security_engine import AISecurityEngine

engine = AISecurityEngine()
result = engine.analyze_vulnerability({
    "cve_id": "CVE-2024-1234",
    "severity": "CRITICAL",
    "package": "openssl"
})

print(result['analysis'])
print(result['remediation'])
```

## Configuration

### Model Selection

Edit `GP-PLATFORM/james-config/gp_data_config.py`:

```python
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"  # Default
# Alternatives:
# "meta-llama/Llama-3.1-8B-Instruct"
# "deepseek-ai/deepseek-coder-6.7b-instruct"
```

### RAG Collections

Knowledge bases are auto-synced from:
- `GP-DATA/active/scans/` - Scan results
- `GP-DATA/knowledge-base/` - Security documentation
- `GP-RAG/unprocessed/` - New knowledge to index

### System Prompts

Located in `config/jade_prompts.py`:
- Security expert persona
- Reasoning templates
- Domain-specific instructions

## Development

### Adding New Agents

```python
# agents/my_custom_agent.py
from GP_AI.agents.jade_orchestrator import JadeOrchestrator

class MyCustomAgent:
    def __init__(self):
        self.orchestrator = JadeOrchestrator()

    def analyze(self, context):
        return self.orchestrator.process(context)
```

### Adding Tool Integrations

```python
# integrations/my_tool.py
from GP_AI.integrations.tool_registry import ToolRegistry

@ToolRegistry.register
class MyTool:
    name = "my_tool"
    description = "Does something useful"

    def execute(self, **kwargs):
        # Implementation
        return results
```

## Data Flow

```
User Input (CLI/API)
    ↓
Intent Classification (LLM)
    ↓
RAG Knowledge Query (Vector Search)
    ↓
Security Reasoning Engine (LLM + Logic)
    ↓
Tool Execution (Scanners, Fixers)
    ↓
Result Synthesis (LLM)
    ↓
Output (JSON/Text/Actions)
    ↓
GP-DATA Persistence
```

## Dependencies

- `transformers` - Hugging Face models
- `torch` - PyTorch for inference
- `chromadb` - Vector database for RAG
- `fastapi` - REST API server
- `langchain` - Agent frameworks
- `rich` - CLI formatting

## Performance

- **Model Loading**: ~5-10s (first run)
- **Inference**: ~1-3s per query (GPU)
- **RAG Query**: ~100-200ms
- **Full Analysis**: ~3-5s

## Security

- ✅ Local models (no cloud API calls)
- ✅ Secrets stored in GP-DATA/audit/ (encrypted)
- ✅ Approval workflows for destructive actions
- ✅ Audit logging for all AI decisions
- ✅ No PII/credentials in model prompts

## Troubleshooting

**Model won't load**
```bash
# Download model manually
python GP-AI/models/model_manager.py --download
```

**GPU not detected**
```bash
# Check CUDA
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

**RAG returns no results**
```bash
# Sync knowledge base
cd GP-DATA
python simple_sync.py
```

## Directory Breakdown

```
GP-AI/ (~9,255 lines of Python code)
├── core/                    # 🧠 Core AI Reasoning Engines
│   ├── ai_security_engine.py    # Main security analysis (LLM-powered)
│   ├── rag_engine.py            # RAG knowledge retrieval (ChromaDB)
│   └── security_reasoning.py    # Domain logic (deterministic)
│
├── models/                  # 🤖 LLM Management
│   ├── model_manager.py         # Model loading & inference (~299 LOC)
│   └── gpu_config.py            # Hardware optimization (~115 LOC)
│
├── agents/                  # 🎯 Autonomous Workflows
│   ├── jade_orchestrator.py     # LangGraph multi-step agent
│   └── troubleshooting_agent.py # Domain-specific debugging
│
├── cli/                     # 💻 Command-Line Interfaces
│   ├── jade-cli.py              # Main CLI: jade <command>
│   ├── jade_chat.py             # Interactive chat mode
│   ├── jade_explain_gha.py      # GitHub Actions analyzer
│   ├── jade_analyze_gha.py      # GHA deep analysis
│   ├── gha_analyzer.py          # GHA parser module
│   └── simple_gha_explainer.py  # Quick GHA troubleshooter
│
├── api/                     # 🌐 REST API Server
│   ├── main.py                  # FastAPI application
│   ├── approval_routes.py       # Human-in-the-loop workflows (~510 LOC)
│   └── secrets_routes.py        # Secrets management endpoints
│
├── integrations/            # 🔌 External Tool Integrations
│   ├── tool_registry.py         # Dynamic tool discovery (~422 LOC)
│   ├── scan_integrator.py       # Scanner output normalization
│   └── jade_gatekeeper_integration.py # OPA Gatekeeper integration
│
├── workflows/               # 🔄 Pre-built Workflows
│   └── approval_workflow.py     # Approval state machine
│
├── config/                  # ⚙️ Configuration
│   ├── jade_prompts.py          # AI system prompts
│   └── routing_config.json      # Intent routing rules
│
├── engines/                 # 🔧 Adapters
│   └── llm_adapter.py           # LLM provider abstraction
│
├── _local_data/             # 📦 Local Runtime Data
│   ├── ai-models/               # Downloaded model cache
│   └── audit/                   # Local audit logs
│
└── __pycache__/             # Python bytecode cache
```

## Component Workflow

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

### GitHub Actions Analysis Flow
```
User: "jade explain workflow_run 12345"
         ↓
1. jade_explain_gha.py fetches logs from GitHub API
         ↓
2. gha_analyzer.py parses YAML + logs
         ↓
3. AI Security Engine analyzes failures
         ↓
4. Output: Root cause + fix recommendations
```

## Key Features

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

## Model Configuration

### Current Default Model
**Qwen2.5-7B-Instruct** (Recommended)
- Size: ~7GB
- Speed: 1-3s per query (GPU)
- Quality: Excellent for security reasoning
- Location: `~/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct/`

### Alternative Models
Edit `GP-PLATFORM/james-config/gp_data_config.py`:
```python
# High-performance alternatives
"meta-llama/Llama-3.1-8B-Instruct"      # Meta's flagship
"deepseek-ai/deepseek-coder-6.7b"      # Code-focused
"mistralai/Mistral-7B-Instruct-v0.2"   # Fast inference
```

### Hardware Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 16GB | 32GB |
| GPU | None (CPU fallback) | NVIDIA 8GB+ VRAM |
| Disk | 10GB | 20GB (multiple models) |
| CUDA | - | 11.8+ |

## API Endpoints

Start server: `uvicorn api.main:app --reload --port 8000`

### Security Analysis
```bash
POST /api/analyze
{
  "target": "GP-PROJECTS/MyApp",
  "scanners": ["trivy", "bandit"],
  "depth": "deep"
}
```

### Knowledge Query
```bash
POST /api/query
{
  "question": "How to fix SQL injection in Python?",
  "context": {"language": "python"}
}
```

### Approval Workflow
```bash
POST /api/approval
{
  "action": "delete_secrets",
  "target": "file.py",
  "requires_approval": true
}
```

### Secrets Management
```bash
GET /api/secrets/{project}
POST /api/secrets/rotate
```

## Environment Variables

```bash
# Model configuration
export GP_MODEL_NAME="Qwen/Qwen2.5-7B-Instruct"
export GP_MODEL_CACHE="$HOME/.cache/huggingface"

# API server
export GP_API_PORT=8000
export GP_API_HOST="0.0.0.0"

# RAG configuration
export CHROMA_PATH="$HOME/linkops-industries/GP-copilot/GP-DATA/active/chroma_db"

# GPU settings
export CUDA_VISIBLE_DEVICES=0  # Use first GPU
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
```

## Performance Metrics

| Operation | Time (GPU) | Time (CPU) |
|-----------|-----------|-----------|
| Model Loading | 5-10s | 15-30s |
| Single Query | 1-3s | 5-10s |
| RAG Search | 100-200ms | 100-200ms |
| Full Scan Analysis | 3-5s | 10-20s |
| Batch Processing (10) | 15-30s | 60-120s |

## Security & Privacy

✅ **Local-First**: All models run locally, no cloud API calls
✅ **No Data Leakage**: Code never sent to external services
✅ **Encrypted Storage**: Secrets in GP-DATA/audit/ encrypted at rest
✅ **Audit Trail**: All AI decisions logged to evidence.jsonl
✅ **Approval Gates**: Human-in-the-loop for destructive actions
✅ **PII Scrubbing**: Automatic removal from prompts

## Integration Points

### Data Sources (Input)
- **GP-DATA/active/results/** - Scanner outputs
- **GP-DATA/knowledge-base/** - Security documentation
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

## Related Components

- **[GP-DATA/](../GP-DATA/)** - Centralized data management and RAG storage
- **[GP-CONSULTING/](../GP-CONSULTING/)** - Security scanners and fixers
- **[GP-PLATFORM/](../GP-PLATFORM/)** - Shared configuration and utilities
- **[GP-RAG/](../GP-RAG/)** - Document ingestion pipelines
- **[bin/](../bin/)** - Security tool binaries

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
```

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed component design
- **[QUICK_START.md](QUICK_START.md)** - Getting started guide
- **[COMPLETE_JADE_MAP.md](COMPLETE_JADE_MAP.md)** - Full system map
- **[cli/CHAT_MODE_README.md](cli/CHAT_MODE_README.md)** - Chat interface docs
- **[START_HERE.md](../START_HERE.md)** - Platform overview

## Troubleshooting

**Model Loading Fails**
```bash
# Download manually
huggingface-cli download Qwen/Qwen2.5-7B-Instruct

# Check cache
ls ~/.cache/huggingface/hub/
```

**GPU Not Detected**
```bash
nvidia-smi  # Check GPU
python -c "import torch; print(torch.cuda.is_available())"
```

**RAG No Results**
```bash
# Rebuild vector DB
cd GP-DATA && python simple_sync.py
```

**API Port Conflict**
```bash
# Use different port
uvicorn api.main:app --port 8001
```

---

**Status**: ✅ Production Ready
**Last Updated**: 2025-10-07
**Version**: 2.1
**Lines of Code**: ~9,255 Python LOC
**Maintained by**: LinkOps Industries - JADE AI Security Platform Team