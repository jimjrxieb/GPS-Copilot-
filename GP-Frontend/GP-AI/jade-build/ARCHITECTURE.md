# GP-AI Architecture

## System Overview

GP-AI is the **intelligent reasoning layer** of the GuidePoint Security Platform. It provides AI-powered security analysis, knowledge retrieval, and autonomous agent workflows.

```
┌─────────────────────────────────────────────────────────────────┐
│                        GP-AI PLATFORM                           │
│                  (AI Security Intelligence)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │  CORE   │          │ AGENTS  │          │   CLI   │
   │ Engines │          │ Workflows│          │Interface│
   └─────────┘          └─────────┘          └─────────┘
        │                     │                     │
        ├──► AI Security      ├──► Orchestrator    ├──► jade-cli
        ├──► RAG Engine       ├──► Troubleshoot    └──► jade chat
        └──► Reasoning        └──► Multi-step

        ┌─────────────────────┴─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ MODELS  │          │   API   │          │INTEGR.  │
   │ Manager │          │ Server  │          │ Tools   │
   └─────────┘          └─────────┘          └─────────┘
        │                     │                     │
        ├──► Model Load       ├──► REST API        ├──► Scanners
        ├──► GPU Config       ├──► Approvals       ├──► Registry
        └──► Inference        └──► Secrets         └──► Normalize
```

## Component Details

### 1. Core Engines (`core/`)

The brain of GP-AI - handles all AI reasoning and knowledge retrieval.

#### AI Security Engine (`ai_security_engine.py`)
- **Purpose**: Deep security analysis and threat intelligence
- **Capabilities**:
  - Vulnerability impact assessment
  - Attack path analysis
  - Remediation generation
  - Risk scoring with AI confidence
  - Multi-framework compliance mapping
- **LLM Usage**: Qwen2.5-7B for reasoning
- **Input**: Scan results, CVE data, code snippets
- **Output**: Security findings with AI-enhanced metadata

#### RAG Engine (`rag_engine.py`)
- **Purpose**: Knowledge-augmented generation
- **Capabilities**:
  - Semantic search across security knowledge
  - Context injection for LLM queries
  - Multi-collection knowledge bases
  - Auto-sync with scan results
- **Vector DB**: ChromaDB
- **Collections**:
  - `scan_findings` - Historical scan results
  - `documentation` - Security guides
  - `compliance_frameworks` - Regulatory standards
  - `security_patterns` - Best practices
- **Performance**: ~100-200ms query time

#### Security Reasoning (`security_reasoning.py`)
- **Purpose**: Domain-specific security logic
- **Capabilities**:
  - CVE severity calculation
  - Policy violation interpretation
  - Threat modeling
  - Compliance mapping
- **Non-LLM**: Fast, deterministic reasoning

---

### 2. Model Management (`models/`)

Handles LLM lifecycle and hardware optimization.

#### Model Manager (`model_manager.py`)
```python
from models.model_manager import ModelManager

manager = ModelManager()
response = manager.generate(
    prompt="Explain CVE-2024-1234",
    max_tokens=500
)
```

**Features**:
- Lazy loading (model loads on first use)
- GPU/CPU auto-detection
- Model caching
- Multi-model support (Qwen, Llama, DeepSeek)
- Inference API

**Supported Models**:
- `Qwen/Qwen2.5-7B-Instruct` (default)
- `meta-llama/Llama-3.1-8B-Instruct`
- `deepseek-ai/deepseek-coder-6.7b-instruct`

#### GPU Config (`gpu_config.py`)
- CUDA detection
- Memory management
- Multi-GPU support
- CPU fallback

---

### 3. Autonomous Agents (`agents/`)

Multi-step reasoning and task execution.

#### Jade Orchestrator (`jade_orchestrator.py`)
**Framework**: LangGraph
**Purpose**: Multi-turn conversations with tool use

**Workflow**:
```
User Query
    ↓
Intent Classification
    ↓
Domain Detection (k8s, terraform, opa)
    ↓
RAG Knowledge Retrieval
    ↓
Specialized Agent Selection
    ↓
Tool Execution
    ↓
Response Synthesis
```

**Example**:
```bash
jade agent "kubernetes pod crashlooping in production"
```

#### Troubleshooting Agent (`troubleshooting_agent.py`)
**Purpose**: Domain-specific problem solving

**Domains**:
- Kubernetes debugging
- Terraform validation
- OPA policy resolution
- Security tool errors

---

### 4. CLI Interfaces (`cli/`)

User-facing command-line tools.

#### jade-cli.py
**Main command interface**:
```bash
jade scan GP-PROJECTS/MyApp          # Security scan
jade query "How to fix CVE?"         # RAG query
jade agent "debug k8s pod"           # Agentic workflow
jade chat                            # Interactive mode
jade projects                        # List projects
jade stats                           # System health
```

**Architecture**:
- Click-based CLI framework
- Subcommand routing
- Rich console output
- Error handling

#### jade_chat.py
**Interactive conversational interface**:
```bash
You: I want to scan my project quickly
Jade: Quick security scan
      Running: PYTHONPATH=... ./gp-security scan ...
```

**Features**:
- Pattern matching + LLM intent recognition
- Natural language understanding
- Command execution
- Result summarization
- Context-aware project handling

**Pattern Engine**:
```python
command_patterns = {
    r"(scan|check).*project.*quick": {
        "command": "PYTHONPATH=... ./gp-security scan {project}",
        "description": "Quick security scan"
    }
}
```

---

### 5. API Server (`api/`)

RESTful API for external integrations.

#### Main API (`main.py`)
**Framework**: FastAPI
**Port**: 8000

**Endpoints**:
```
GET  /health                    # System health
POST /api/v1/scan               # Security scan
POST /api/v1/query              # RAG query
POST /api/v1/ingest             # Knowledge ingestion
GET  /api/v1/knowledge/stats    # KB statistics
```

**Usage**:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain SQL injection"}'
```

#### Approval Routes (`approval_routes.py`)
**Purpose**: Human-in-the-loop workflows

**Endpoints**:
```
POST /api/approvals/request     # Request approval
GET  /api/approvals/pending     # List pending
POST /api/approvals/{id}/approve # Approve action
POST /api/approvals/{id}/reject  # Reject action
```

**Use Cases**:
- Auto-fix approval
- Production deployments
- Secrets rotation
- Policy changes

#### Secrets Routes (`secrets_routes.py`)
**Purpose**: Secrets management and rotation

**Endpoints**:
```
GET  /api/secrets/detect        # Detect exposed secrets
POST /api/secrets/rotate        # Rotate credentials
GET  /api/secrets/audit         # Audit log
```

---

### 6. Integrations (`integrations/`)

External tool connectivity.

#### Tool Registry (`tool_registry.py`)
**Purpose**: Dynamic tool discovery and registration

**Example**:
```python
@ToolRegistry.register
class TrivyScanner:
    name = "trivy"
    description = "Container vulnerability scanner"

    def execute(self, target):
        # Implementation
        return results
```

**Registered Tools**:
- Bandit (Python SAST)
- Trivy (Container/IaC)
- Semgrep (Multi-language)
- Gitleaks (Secrets)
- OPA (Policy)

#### Scan Integrator (`scan_integrator.py`)
**Purpose**: Normalize scanner outputs

**Features**:
- Multi-scanner aggregation
- Severity normalization
- Deduplication
- GP-DATA sync

**Input**: Raw scanner JSON
**Output**: Unified finding format

---

### 7. Workflows (`workflows/`)

Pre-built automation workflows.

#### Approval Workflow (`approval_workflow.py`)
**Purpose**: State machine for approvals

**States**:
```
PENDING → IN_REVIEW → APPROVED → EXECUTED
                   ↓
                 REJECTED
```

**Features**:
- Multi-approver support
- Timeout handling
- Audit logging
- Rollback capability

---

### 8. Configuration (`config/`)

System prompts and routing.

#### Jade Prompts (`jade_prompts.py`)
**Purpose**: LLM system prompts

**Prompts**:
- Security expert persona
- Reasoning templates
- Domain-specific instructions
- Output formatting

**Example**:
```python
SECURITY_EXPERT_PROMPT = """
You are Jade, a senior security consultant specializing in...
When analyzing vulnerabilities, focus on:
1. Impact assessment
2. Attack vectors
3. Remediation steps
4. Compliance implications
"""
```

#### Routing Config (`routing_config.json`)
**Purpose**: Intent → Agent routing

**Structure**:
```json
{
  "intents": {
    "scan": {"agent": "security_scanner", "priority": "high"},
    "debug": {"agent": "troubleshooting", "domain_specific": true}
  }
}
```

---

## Data Flow

### Scan Workflow
```
1. User: jade scan GP-PROJECTS/MyApp
2. CLI parses command
3. Invokes GP-CONSULTING-AGENTS scanners
4. Scan results → GP-DATA/active/scans/
5. RAG Engine ingests findings
6. AI Security Engine analyzes
7. Response synthesis
8. Output to user + save to GP-DATA
```

### Query Workflow
```
1. User: jade query "How to fix CVE-2024-1234?"
2. RAG Engine: Semantic search
3. Retrieve top 5 relevant documents
4. Inject context into LLM prompt
5. AI Security Engine: Generate response
6. Return answer + sources
```

### Agentic Workflow
```
1. User: jade agent "k8s pod crashlooping"
2. Orchestrator: Classify intent
3. Detect domain: kubernetes
4. Load troubleshooting agent
5. Agent: Execute kubectl commands
6. RAG: Query k8s knowledge base
7. Synthesize diagnosis + remediation
8. Return multi-step solution
```

---

## Performance Characteristics

| Component | Metric | Value |
|-----------|--------|-------|
| Model Load | First Use | 5-10s |
| Inference | Per Query (GPU) | 1-3s |
| RAG Query | Vector Search | 100-200ms |
| Full Scan Analysis | E2E | 30-60s |
| API Response | Health Check | <50ms |

---

## Security & Privacy

✅ **Local Inference** - No cloud API calls
✅ **No Data Leakage** - Models run on-premise
✅ **Secrets Encryption** - GP-DATA/audit/ encrypted
✅ **Audit Logging** - All AI decisions logged
✅ **Human Approval** - Destructive actions require approval
✅ **No PII in Prompts** - Sanitized inputs

---

## Deployment

### Standalone
```bash
cd GP-copilot
source venv/bin/activate
jade chat
```

### API Server
```bash
cd GP-AI
uvicorn api.main:app --reload --port 8000
```

### Docker (Future)
```bash
docker run -p 8000:8000 guidepoint/gp-ai:latest
```

---

## Roadmap

- [ ] Multi-model ensemble (Qwen + Llama + DeepSeek)
- [ ] Fine-tuned security models
- [ ] Real-time streaming responses
- [ ] GPU cluster support
- [ ] Web UI dashboard
- [ ] Docker containerization
- [ ] Kubernetes deployment

---

**Last Updated**: 2025-10-04
**Version**: 2.0
**Maintainer**: GuidePoint Security Team